#!/usr/bin/env python3
import asyncio
import json, models

from datetime import datetime
from tortoise import Tortoise
from models import ResourceType, RoleType


async def init_db() -> None:
    await Tortoise.init(db_url='sqlite://db.sqlite3', modules={'models': ['models']})
    await Tortoise.generate_schemas()

async def close_db() -> None:
     await Tortoise.close_connections()

async def load_blogs() -> None:
    with open('datasets/blogs.json', 'r') as file:
        data = json.load(file)
    for item in data:
        await models.Resource.create(
            title = item['title'],
            category = item.get('category', None),
            description = item['description'],
            image = item['image_url'],
            type = ResourceType.BLOG,
            url = item['post_link'],
            date = item.get('date', None),
            language = item.get('language', None),
            stars = item.get('watchers_count', None)
        )

async def load_repos() -> None:
    with open('datasets/repos.json', 'r') as file:
        data = json.load(file)
    for item in data['items']:
        if item['description'] is not None:
            await models.Resource.create(
                title = item['full_name'],
                category = item.get('category', None),
                description = item['description'],
                image = item['owner']['avatar_url'],
                type = ResourceType.REPOSITORY,
                url = item['html_url'],
                date = item.get('date', None),
                language = item.get('language', None),
                stars = item.get('watchers_count', None)
            )

async def load_courses() -> None:
    with open('datasets/courses.json', 'r') as file:
        data = json.load(file)
    for item in data:
        if 'description' in item and item['description'] != "No description found.":
            await models.Resource.create(
                title = item['title'],
                category = item.get('category', None),
                description = item['description'],
                type = ResourceType.COURSE,
                url = item['link'],
                date = datetime.strptime(item['date'], "%b %d, %Y") if 'date' in item else None,
                language = item.get('language', None),
                authors = item.get('author', None),
                rating = item.get('rating', None),
                reviews = item.get('reviews', None),
                duration = item.get('duration', None)
            )

async def load_research_papers() -> None:
    with open('datasets/research_papers.json', 'r') as file:
        data = json.load(file)
    for item in data:
        await models.Resource.create(
            title=item['title'],
            category=item.get('category', None),
            description=item['summary'],
            type=ResourceType.RESEARCH_PAPER,
            url=item['pdf_link'],
            date=item.get('date', None),
            language=item.get('language', None),
            authors=item['authors']
        )

#TODO: Enable form to submit for admin approval
async def load_unapproved() -> None:
    with open('datasets/blogs.json', 'r') as file:
        data = json.load(file)
    for item in data:
        await models.Unapproved.create(
            title=item['title'],
            description=item['description'],
            image=item['image_url'],
            type=ResourceType.BLOG,
            url=item['post_link'],
            date=item.get('date', None),
            authors=item.get('authors', None)
        )

async def load_users() -> None:
    await models.User.create(username='admin', password='admin', role=RoleType.ADMIN)
    await models.User.create(username='mrudula', password='password', role=RoleType.USER)
    await models.User.create(username='niyati', password='password', role=RoleType.USER)

async def main():
    await init_db()
    await load_blogs()
    await load_courses()
    await load_repos()
    await load_research_papers()
    await load_unapproved()
    await load_users()
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
