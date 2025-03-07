#!/usr/bin/env python3
import asyncio
import json, models
from tortoise import Tortoise


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
            url = item['post_link'],
            date = item.get('date', None),
            language = item.get('language', None),
            stars = item.get('watchers_count', None)
        )

async def main():
    await init_db()
    await load_blogs()
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
