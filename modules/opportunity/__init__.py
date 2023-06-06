"""
En este archivo se definiran unos registros del modulo opportunity que podran ser instanciados
mediante el objeto Pool de Tryton. Este objeto permitira mantener a los modulos con un acceso centralizado
entre ellos y no instanciar individualmente los objetos de cada uno de los modulos.
"""
# Se importa el objeto Pool. 
from trytond.pool import Pool
# Se importa desde el directorio actual (.) el modulo de Python o paquete opportunity
from . import opportunity

def register():
    Pool.register(opportunity.Opportunity, module='opportunity', type_='model')
