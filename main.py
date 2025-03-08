#!/usr/bin/env python3
import asyncio
import httpx

from auth import AuthMiddleware, login
from nicegui import app, ui
from tortoise import Tortoise
from typing import Optional
from utils import blogs, courses, github_repos, research_papers

api = httpx.AsyncClient()
running_query: Optional[asyncio.Task] = None

async def init_db() -> None:
    await Tortoise.init(db_url='sqlite://db.sqlite3', modules={'models': ['models']})
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()

app.on_startup(init_db)
app.on_shutdown(close_db)

@ui.page('/')
def main_page() -> None:
    def logout() -> None:
        app.storage.user.clear() #should we just clear session?
        ui.navigate.to('/login')

    with ui.header().classes('items-right'):
        ui.label(f'{app.storage.user["username"]}').classes('text-2xl')
        ui.button(on_click=logout, icon='logout')

    ui.link('Courses', courses)
    ui.link('Handbooks', github_repos)
    ui.link('Github Repos', github_repos)
    ui.link('Trending Repos', trending_repos)
    ui.link('Research Papers', research_papers)
    ui.link('Blogs', blogs)

@ui.page('/trending_repos')
async def trending_repos() -> None:
    results = ui.row()
    global running_query  # pylint: disable=global-statement # noqa: PLW0603
    if running_query:
        running_query.cancel()  # cancel the previous query; happens when you type fast
    results.clear()
    # store the http coroutine in a task so we can cancel it later if needed
    running_query = asyncio.create_task(api.get(f'https://api.github.com/search/repositories?q=deeplearning'))
    response = await running_query
    if response.text == '':
        return
    with results:  # enter the context of the results row
        with ui.list():
            for repo in response.json()['items'] or []:  # iterate over the response data of the api
                with ui.link(target=repo['html_url']):
                    with ui.item():
                        with ui.item_section().props('avatar'):
                            ui.image(repo['owner']['avatar_url'])
                        with ui.item_section():
                            ui.item_label(repo['full_name'])
                            ui.item_label(repo['description']).props('caption')
                            ui.item_label(repo['language']).props('caption')
                            ui.icon('star')
                            ui.item_label(repo['watchers_count']).props('caption')
    running_query = None

ui.run(storage_secret='THIS_NEEDS_TO_BE_CHANGED')