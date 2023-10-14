from trytond.pool import Pool
from . import task
from . import configuration

def register():
    Pool.register(
        task.Task,
        task.TaskEvent,
        configuration.Configuration,
        module='tasks', type_='model')
