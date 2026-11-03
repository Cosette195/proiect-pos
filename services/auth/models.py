from peewee import Model, CharField, BooleanField, BinaryUUIDField
from database import db


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    uid = BinaryUUIDField(primary_key=True)
    username = CharField()
    password = CharField(null=True)
    role = CharField()
    is_active = BooleanField()

    class Meta:
        db_table = "users"
