import uuid
from datetime import datetime
from peewee import Model, CharField, DateTimeField
from database import db

class BaseModel(Model):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        database = db
