from trytond.model import (ModelView, ModelSQL, fields,
    Unique, Workflow)
from trytond.pool import Pool
from trytond.pyson import Eval, If, Bool
from datetime import date as dt


class Task(Workflow, ModelSQL, ModelView):
    '''Task'''
    __name__ = 'task.task'

    name = fields.Char("Task name", required=True,
        help="The main identifier of the task.")
    code = fields.Char("Code", readonly=True,
        help="The unique identifier of the task.")
    issue = fields.Many2One('party.category', "Issue")
    description = fields.Text('Description')
    end_date = fields.Date("End date task",
        domain=[
            If(Bool(Eval('end_date')),
                ('end_date', '>=', dt.today()),
                ())])
    state = fields.Selection([
        ('draft', "Draft"),
        ('pending', "Pending"),
        ('done', "Done"),
        ], "State",
       required=True, readonly=True, sort=False)

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
    def default_state(cls):
        return 'draft'

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