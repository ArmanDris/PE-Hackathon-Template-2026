from peewee import AutoField, IntegerField, CharField, DateTimeField
from app.database import BaseModel
from playhouse.postgres_ext import JSONField

class Events(BaseModel):
    id = AutoField()
    # index=True makes filtering & grouping optimized
    url_id = IntegerField(index=True)
    user_id = IntegerField(index=True)
    event_type = CharField(index=True)
    timestamp = DateTimeField(index=True)
    details = JSONField()
