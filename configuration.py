from trytond.model import (ModelView, ModelSQL, fields,
    MultiValueMixin, ModelSingleton)


class Configuration(ModelSingleton, ModelSQL, ModelView, MultiValueMixin):
    '''Task Configuration'''
    __name__ = 'task.configuration'

    task_sequence = fields.Many2One('ir.sequence', 'Sequences',
        help="Used to generate the task code.")