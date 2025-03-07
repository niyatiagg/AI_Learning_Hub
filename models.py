from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()

class Resource(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    category = fields.CharField(max_length=64, null=True)
    description = fields.CharField(max_length=2048)
    image = fields.CharField(max_length=255, null=True)
    url = fields.CharField(max_length=255)
    date = fields.DateField(null=True)
    language = fields.CharField(max_length=64, null=True)
    stars = fields.IntField(null=True)
