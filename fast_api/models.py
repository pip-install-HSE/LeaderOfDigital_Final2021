from tortoise import fields, models
from tortoise.contrib.mysql.fields import GeometryField
from shapely.geometry import shape


class MyGeometryField(GeometryField, fields.JSONField):
    pass


class Tasks(models.Model):
    id = fields.IntField(pk=True, index=True)
    geometry = MyGeometryField()
    data_datetime = fields.DatetimeField()
    object_id = fields.IntField()
    # object = fields.ForeignKeyField("models.Objects", related_name="tasks")
    oil_spill_chance = fields.FloatField()
    cloudy = fields.FloatField()


class Tags(models.Model):
    id = fields.IntField(pk=True, index=True)
    object_id = fields.IntField()
    # object = fields.ForeignKeyField("models.Objects", related_name="tags")
    key = fields.CharField(max_length=100)
    value = fields.CharField(max_length=100)


class Objects(models.Model):
    id = fields.IntField(pk=True, index=True)
    geometry = MyGeometryField()
    name = fields.CharField(max_length=200, unique=True)
    padding = fields.FloatField()
