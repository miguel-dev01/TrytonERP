from trytond.model import (ModelView, ModelSQL, fields,
    Unique, Workflow)
from trytond.pool import Pool
from trytond.pyson import Eval, If, Bool
from datetime import date as dt


class Task(Workflow, ModelSQL, ModelView):
    '''Task'''
    __name__ = 'task.task'

    name = fields.Char("Task name", required=True,
        states = {'readonly': Eval('state') == 'done'},
        help="The main identifier of the task.")
    code = fields.Char("Code", readonly=True,
        states = {'readonly': Eval('state') == 'done'},
        help="The unique identifier of the task.")
    issue = fields.Many2One('party.category', "Issue", 
        states = {'readonly': Eval('state') == 'done'})
    description = fields.Text('Description',
        states = {'readonly': Eval('state') == 'done'})
    end_date = fields.Date("End date task",
        states = {'readonly': Eval('state') == 'done'},
        domain=[
            If(Bool(Eval('end_date')),
                ('end_date', '>=', dt.today()), ())
            ])
    state = fields.Selection([
            ('draft', "Draft"),
            ('pending', "Pending"),
            ('done', "Done"),
            ], "State",
        required=True, readonly=True, sort=False)
    priority = fields.Selection([
            ('urgent', "Urgent"),
            ('high', "High"),
            ('normal', "Normal"),
            ('low', "Low"),
            ], "Priority", states = {'readonly': Eval('state') == 'done'},
        required=True, sort=False, help='Indicates the priority of the task')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('code_uniq', Unique(t, t.code), 'tasks.msg_task_code_unique')
        ]
        cls._transitions.update({
            ('draft', 'pending'),
            ('draft', 'done'),
            ('pending', 'draft'),
            ('pending', 'done'),
            ('done', 'pending'),
        })
        cls._buttons.update({
            'draft': {},
            'pending': {},
            'done': {}
        })

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_end_date():
        return dt.today()

    @classmethod
    def _new_code(cls):
        pool = Pool()
        Configuration = pool.get('task.configuration')
        config = Configuration(1)
        sequence = config.task_sequence
        if sequence:
            return sequence.get()

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('code'):
                values['code'] = cls._new_code()
        return super(Task, cls).create(vlist)

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('/tree', 'visual', If(Eval('end_date', 0) <= dt.today(), 'warning', '')),
            ('/tree/field[@name="priority"]',
                'visual', If(Eval('priority', '') == 'urgent', 'danger', '')),
        ]

    @fields.depends('name', 'description')
    def on_change_with_description(self, name=None):
        if self.name and not self.description:
            return self.name
        return self.description if self.description else None

    @classmethod
    @Workflow.transition('draft')
    def draft(cls, records):
        pass

    @classmethod
    @Workflow.transition('pending')
    def pending(cls, records):
        pass

    @classmethod
    @Workflow.transition('done')
    def done(cls, records):
        pass


class TaskEvent(ModelSQL, ModelView):
    '''Task Event Calendar'''
    __name__ = 'task.event'

    name = fields.Char("Event name", required=True)
    event_date = fields.Date("Event date", required=True)
    calendar_bgcolor = fields.Function(
        fields.Char('Background color'), 'get_calendar_bgcolor')

    @classmethod
    def view_attributes(cls):
        return [
            ('/tree', 'visual', 
                If(Eval('event_date', 0) < dt.today(), 'success', 'danger')),
        ]

    def get_calendar_bgcolor(self, name=None):
        if self.event_date < dt.today():
            return 'lightblue'
        else:
            return 'red'