from tortoise import fields, models
from tortoise.contrib.mysql.fields import GeometryField
from tortoise.contrib.pydantic import pydantic_model_creator
from shapely.geometry import shape
from pydantic import validator


class MyGeometryField(GeometryField, fields.JSONField):
    pass


class Tasks(models.Model):
    id = fields.IntField(pk=True)
    geometry = MyGeometryField()
    data_datetime = fields.DatetimeField()
    object = fields.ForeignKeyField("models.Objects", related_name="tasks")
    oil_spill_chance = fields.FloatField()
    cloudy = fields.FloatField()


class Tags(models.Model):
    id = fields.IntField(pk=True)
    object = fields.ForeignKeyField("models.Objects", related_name="tags")
    key = fields.CharField(max_length=100)
    value = fields.CharField(max_length=100)


    id = fields.IntField(pk=True)
    geometry = MyGeometryField()
    name = fields.CharField(max_length=200, unique=True)
    padding = fields.FloatField()


Task_Pydantic = pydantic_model_creator(Tasks, name="Task")
Tag_Pydantic = pydantic_model_creator(Tags, name="Tag")
Object_Pydantic = pydantic_model_creator(Objects, name="Object")
