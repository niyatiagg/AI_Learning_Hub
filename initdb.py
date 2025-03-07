#!/usr/bin/env python3
import asyncio
import json, models

from docutils.nodes import authors
from tortoise import Tortoise

from models import ResourceType


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
        if 'description' in item:
            await models.Resource.create(
                title = item['title'],
                category = item.get('category', None),
                description = item['description'],
                type = ResourceType.COURSE,
                url = item['link'],
                #date = item.get('date', None), #TODO: Fix logic for date
                language = item.get('language', None),
                authors = item['author']
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

async def main():
    await init_db()
    await load_blogs()
    await load_courses()
    await load_repos()
    await load_research_papers()
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
