from trytond.pool import Pool
from . import task
from . import configuration

def register():
    Pool.register(
        task.Task,
        configuration.Configuration,
        module='tasks', type_='model')
