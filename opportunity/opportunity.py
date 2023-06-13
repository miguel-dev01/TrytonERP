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

6º - Trabajaremos con campos calculados, restricciones sobre campos, valores predeterminados, flujos de trabajo, botones, wizard, informes...

Debemos tener en cuenta como se trabaja con la estructura en una clase .py
"""
# Importamos los objetos ModelSQL y fields del modulo(estructuras de codigo Python) TRYTOND
from trytond.model import ModelSQL, fields, ModelView
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.model import Workflow
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.report import Report
import datetime as dt

class Opportunity(Workflow, ModelSQL, ModelView):
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
    end_date = fields.Date("End date", states={
            'readonly': Eval('state') == 'converted',
            'required': Eval('state') == 'lost',
            })
    # Este tipo de campo tiene que ver con la relacion de un modelo de datos, uno a muchos.
    # Es decir, este modulo Opportunity estaria relacionado con otro modulo de Tryton llamado "Party"
    party = fields.Many2One('party.party', "Party", required=True)
    # Es lo mismo que Char pero Text tiene una longitud ilimitada o variable
    comment = fields.Text("Comments")

    # Agregamos restricciones a los posibles valores de un campo. Ejemplo: Que el valor de un campo numérico debe ser mayor que cero
    # Se representa mediante una sintaxis especifica para el dominio
    # Lo siguiente aniade un campo (address) del modelo/modulo party.address en nuestro modulo opportunity
    address = fields.Many2One(
        'party.address', "Address",
        domain=[
            ('party', '=', Eval('party')),
            ],)

    # El siguiente metodo define valores predeterminados
    @classmethod
    def default_start_date(cls):
        pool = Pool()
        Date = pool.get('ir.date')
        return Date.today()
    
    """
    @fields.depends('party','description','comment')
    def on_change_party(self):
        if self.party:
            if not self.description:
                self.description = self.party.rec_name
            if not self.comment:
                lines = []
                if self.party.phone:
                    lines.append("Tel: %s" % self.party.phone)
                if self.party.email:
                    lines.append("Mail: %s" % self.party.email)
                self.comment = '\n'.join(lines)
    """

    # Calcular valores en funcion de otros campos
    # La propiedad depends indica que si el campo start_date sufre modificaciones, se desencadenara el calculo.
    # Este metodo hace: si el campo start_date contiene algo(devolveria true), entonces se devuelve una fecha+3
    @fields.depends('start_date')
    def on_change_with_end_date(self):
        if self.start_date:
            return self.start_date + dt.timedelta(days=3)

    # La siguiente funcionalidad realiza la agregacion de campos calculados. 
    # Se utiliza para evitar la redundancia de informacion al almacenar datos en la BD
    duration = fields.Function(fields.TimeDelta("Duration"), 'on_change_with_duration')
    @fields.depends('start_date','end_date')
    def on_change_with_duration(self, name):
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None

    # Definir flujos de trabajo, es decir, podemos permitir que opportunity tenga unos estados
    # Primero definiremos los estados
    state = fields.Selection([
              ('draft', "Draft"),
              ('converted', "Converted"),
              ('lost', "Lost"),
              ], "State",
       required=True, readonly=True, sort=False)

    # Se queda el estado del boton por defecto en 'draft'
    @classmethod
    def default_state(cls):
       return 'draft'

    # Definimos las transiciones que tendran los botones
    @classmethod
    def __setup__(cls):
      super().__setup__()
      cls._transitions.update({
                ('draft', 'converted'),
                ('draft', 'lost'),
                ('converted', 'draft'),
                ('lost', 'draft')
                })
      
      cls._buttons.update({
                'convert': {},
                'lost': {},
                'draft': {}
                })


    # Definimos el metodo que realiza la accion al pulsar el boton de Convert
    @classmethod
    @ModelView.button
    @Workflow.transition('converted')
    def convert(cls, opportunities, end_date=None):
       pool = Pool()
       Date = pool.get('ir.date')
       cls.write(opportunities, {
           'end_date': end_date or Date.today(),
           })
     
    # Definimos el metodo que realiza la accion al pulsar el boton de Lost
    @classmethod
    @ModelView.button
    @Workflow.transition('lost')
    def lost(cls, opportunities):
        cls.write(opportunities, {
           'end_date': None,
           })

    # Definimos el metodo que realiza la accion al pulsar el boton de Draft
    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, opportunities):
        cls.default_state()


"""
Clase para el asistente de Tryton. Crea el campo end_date que sera actualizado por la clase Convert
"""
class ConvertStart(ModelView):
    "Convert Opportunities"
    __name__ = 'opportunity.convert.start'

    end_date = fields.Date("End Date", required=True)

"""
Clase de asistente en el que realiza la accion de convertir 'end_date' segun el estado convert.
Esta clase contiene el 'wizard'. 
Una analogia es que esta clase podria ser una extension de la clase ConvertStart
"""
class Convert(Wizard):
    "Convert Opportunities"
    __name__ = 'opportunity.convert'

    # La funcion StateView realiza la accion de abrir una ventana nueva en el cliente
    start = StateView(
        'opportunity.convert.start',
        'opportunity.opportunity_convert_start_view_form',[ 
        Button("Cancel", 'end', 'tryton-cancel'),
        Button("Convert", 'convert', 'tryton-ok', default=True),
        ])

    convert = StateTransition()

    def transition_convert(self):
        self.model.convert(self.records, self.start.end_date)
        return 'end'

"""
Clase para generar informes
"""
class OpportunityReport(Report):
    __name__ = 'opportunity.report'




