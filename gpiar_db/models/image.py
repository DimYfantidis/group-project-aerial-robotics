from peewee import CharField, FloatField, BooleanField, ForeignKeyField
from .custom_fields import PointListField
from .base_model import BaseModel
from .mission import Mission


class Image(BaseModel):
    path = CharField()
    lat = FloatField(null=True)
    lon = FloatField(null=True)
    yaw = FloatField(null=True)
    zebra_locations = PointListField(default=[])
    is_zebra = BooleanField(default=False)
    is_rhino = BooleanField(default=False)
    is_processed = BooleanField(default=False)
    
    mission = ForeignKeyField(Mission, backref='images', on_delete='CASCADE')
    
    class Meta:
        table_name = 'image'
