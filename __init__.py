"""
En este archivo se definiran unos registros del modulo opportunity que podran ser instanciados
mediante el objeto Pool de Tryton. Este objeto permitira mantener a los modulos con un acceso centralizado
entre ellos y no instanciar individualmente los objetos de cada uno de los modulos.
Lo que se debe añadir dentro de Pool.register('clase la que sea') deben ser el nombre de las clases que se quieran
registrar en Pool. 
No el nombre del modulo (__name__) ni nada por el estilo
"""
# Se importa el objeto Pool. 
from trytond.pool import Pool
# Se importa desde el directorio actual (.) el modulo de Python o paquete opportunity
from . import opportunity
from . import party

def register():
    Pool.register(opportunity.Opportunity, party.Party, opportunity.ConvertStart, module='opportunity', type_='model')

    Pool.register(opportunity.Convert, module='opportunity', type_='wizard')

    Pool.register(opportunity.OpportunityReport, module='opportunity', type_='report')
