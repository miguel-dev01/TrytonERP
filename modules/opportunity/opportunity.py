"""
Tutorial del modulo Tryton
1º - Definiremos el modelo en este fichero, 
2º - Una vez hayamos definido el modelo. Debemos ir al archivo de __init__.py de nuestro modulo opportunity
 y registrar nuestro nuevo modelo en Pool. El Pool, en el contexto de Tryton, se refiere a un objeto global y compartido 
 que proporciona acceso centralizado a los modelos y registros en Tryton.
3º - Activar el modulo en el fichero de configuracion tryton.cfg del modulo
4º - Actualizar la base de datos+dependencias y activar el nuevo modulo mediante: 
    trytond-admin -c etc/tests.conf -d 'nombreBD' -u 'nombredelmodulo' --activate-dependencies

5º - Mostrar los registros(description, start_date, end_date,comment...) a traves de unas vistas que seran definidas en ficheros XML
    Se debe hacer uso de ModelView, modelo base de Tryton que permite mostrar los campos en el cliente Tryton.
    Para ello se crearan varios xml con vistas (ej: de formulario y de lista) y para cada uno de los elementos habra una configuracion XML en 
    su respectivo fichero XML del modelo. Y posteriormente esas "configuraciones" se instanciaran en otro XML general que debera ir fuera del 
    directorio view
"""
# Importamos los objetos ModelSQL y fields del modulo(estructuras de codigo Python) TRYTOND
from trytond.model import ModelSQL, fields, ModelView
from trytond.pool import Pool

class Opportunity(ModelSQL, ModelView):
    "Opportunity" # En realidad, puede ser cualquier nombre, referente a la entidad o concepto que se esta modelando
    # Este atributo (__name__) se utiliza para hacer referencia a este objeto (opportunity)
    # Tambien se utiliza para construir el nombre de la tabla SQL
    __name__ = 'opportunity'
    # Descripcion de la clase principal del modulo
    _rec_name = 'Aqui iria una descripcion sobre este modulo de Tryton llamado Opportunity'

    # A continuacion trabajaremos sobre los campos propios del modulo y que reflejaran sobre la BD
    # Lo siguiente es un campo que se encontrara en BD y que almacenara una descripcion, y ademas 
    # sera obligatorio ya que tiene la especificacion de "required" en True
    description = fields.Char("Description", required=True)
    # Igual sera por tanto para los siguientes campos
    start_date = fields.Date("Start date", required=True)
    end_date = fields.Date("End date")
    # Este tipo de campo tiene que ver con la relacion de un modelo de datos, uno a muchos.
    # Es decir, este modulo Opportunity estaria relacionado con otro modulo de Tryton llamado "Party"
    party = fields.Many2One('party.party', "Party", required=True)
    # Es lo mismo que Char pero Text tiene una longitud ilimitada o variable
    comment = fields.Text("Comments")

    # Definir valores predeterminados
    @classmethod
    def default_start_date(cls):
        pool = Pool()
        Date = pool.get('ir.date')
        return Date.today()

