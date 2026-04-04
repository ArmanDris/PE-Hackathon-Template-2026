from peewee import (
    AutoField,
    IntegerField,
    CharField,
    TextField,
    BooleanField,
    DateTimeField,
)

from app.database import BaseModel


class Urls(BaseModel):
    id = AutoField()
    user_id = IntegerField(index=True)
    short_code = CharField(unique=True, index=True)
    original_url = TextField()
    title = CharField(null=True)
    is_active = BooleanField(default=True, index=True)
    created_at = DateTimeField(index=True)
    updated_at = DateTimeField(index=True)
