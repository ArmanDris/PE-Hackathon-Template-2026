from peewee import AutoField, CharField, DateTimeField
from datetime import datetime, timezone

from app.database import BaseModel


class Users(BaseModel):
    id = AutoField()
    username = CharField()
    email = CharField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
