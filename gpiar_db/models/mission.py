from peewee import CharField, FloatField, IntegerField, BooleanField
from enum import Enum
from .base_model import BaseModel
from .custom_fields import PointField, PointListField, EnumField 

class MissionStatus(Enum):
    NEW = 'New'
    ACTIVE = 'Active'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'
    FAILED = 'Failed'

class Mission(BaseModel):
    name = CharField()
    altitude = FloatField()
    zebras_count = IntegerField()
    
    rhino_lat = FloatField(null=True)
    rhino_lon = FloatField(null=True)
    rhino_image = CharField(null=True)
    is_rhino_detected = BooleanField(default=False)
    
    takeoff_location_lat = FloatField(null=True)
    takeoff_location_lon = FloatField(null=True)
    
    flight_region = PointListField(null=True)
    sensitive_area = PointListField(null=True)
    path_to_survey = PointListField(null=True)
    path_to_take_off = PointListField(null=True)
    survey_area = PointListField(null=True)
    survey_area_start = PointField(null=True)
    survey_area_end = PointField(null=True)
    processing_spots = PointListField(null=True)
    
    status = EnumField(MissionStatus, default=MissionStatus.NEW)
    
    class Meta:
        table_name = 'mission'
