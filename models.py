from enum import Enum
from tortoise import fields, models

class ResourceType(Enum):
    BLOG = 'blog'
    COURSE = 'course'
    HANDBOOK = 'handbook'
    REPOSITORY = 'repository'
    RESEARCH_PAPER = 'research_paper'

class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()

class Resource(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    category = fields.CharField(max_length=64, null=True)
    description = fields.CharField(max_length=2048)
    type = fields.CharEnumField(ResourceType)
    image = fields.CharField(max_length=255, null=True)
    url = fields.CharField(max_length=255)
    date = fields.DateField(null=True)
    authors = fields.CharField(max_length=512, null=True)
    language = fields.CharField(max_length=64, null=True)
    stars = fields.IntField(null=True)
