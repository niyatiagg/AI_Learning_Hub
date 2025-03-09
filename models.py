from enum import Enum
from tortoise import fields, models

class RoleType(Enum):
    ADMIN = 'admin'
    USER = 'user'

class ResourceType(Enum):
    BLOG = 'Blog'
    COURSE = 'Course'
    HANDBOOK = 'Handbook'
    REPOSITORY = 'Repository'
    RESEARCH_PAPER = 'Research Paper'

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    role = fields.CharEnumField(RoleType)
    password = fields.CharField(max_length=255)

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
    rating = fields.CharField(max_length=5, null=True)
    review = fields.CharField(max_length=16, null=True)
    duration = fields.CharField(max_length=64, null=True)

class Unapproved(models.Model):
    title = fields.CharField(max_length=255)
    description = fields.CharField(max_length=2048)
    type = fields.CharEnumField(ResourceType)
    image = fields.CharField(max_length=255, null=True)
    url = fields.CharField(max_length=255)
    date = fields.DateField(null=True)
    authors = fields.CharField(max_length=512, null=True)

class Bookmark(models.Model):
    userid = fields.IntField()
    resourceid = fields.IntField()