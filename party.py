"""
Nueva clase del modulo Party que extiende nuestro modelo de opportunity
"""
from trytond.model import fields
from trytond.pool import PoolMeta

class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    opportunities = fields.One2Many('opportunity','party',"Opportunities")
