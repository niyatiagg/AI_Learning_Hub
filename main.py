#!/usr/bin/env python3
import asyncio
import httpx

import models
from admin import admin_page
from langchain_openai import ChatOpenAI
from log_callback_handler import NiceGuiLogElementCallbackHandler
from auth import AuthMiddleware, login
from nicegui import app, ui
from tortoise import Tortoise
from typing import Optional, List

from models import RoleType
from utils import bookmarked, blogs, courses, handbooks, github_repos, load_resource_page, research_papers, search, submit_resource_util

api = httpx.AsyncClient()
running_query: Optional[asyncio.Task] = None

async def init_db() -> None:
    await Tortoise.init(db_url='sqlite://db.sqlite3', modules={'models': ['models']})
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()

app.on_startup(init_db)
app.on_shutdown(close_db)

def build_header():
    """Builds the top navigation bar and user/logout section."""
    with ui.header().classes('flex items-center justify-between text-white shadow-md p-4'):
        with ui.row().classes('items-center gap-x-4'):
            ui.label('AI Learning Hub').classes('text-4xl font-bold')
        with ui.row().classes('items-center gap-x-6'):
            ui.icon('account_circle', color='white').classes('text-2xl')
            ui.label(f'{app.storage.user["username"]}').classes('text-2xl font-semibold').style('margin-left: -20px;')
            ui.chip(on_click=lambda: logout(), icon='logout', color='white').props('outline').classes('shadow-lg text-white').style('width: 20%;')

    def logout() -> None:
        app.storage.user.clear() #should we just clear session?
        ui.navigate.to('/login')

@ui.page('/')
def main_page() -> None:
    build_header()
    with ui.dialog().classes('dialog-base flex items-center justify-between') as chat_dialog:
        with ui.card().style('width: 600px; height: 600px;'):
            ui.label('Chat with AI').classes('header-label')
            chat_output = ui.column().classes('chat-output')
            with ui.row().classes('items-center gap-x-2').style("position: absolute; bottom: 20px"):
                user_input = ui.input(placeholder="Ask me something about AI...").classes('input-base').props('autofocus size=60')
                send_button = ui.button('Send', on_click=lambda: asyncio.create_task(send_message(user_input, chat_output))).classes('send-button')
    # ui.button('Chat', on_click=chat_dialog.open).classes('chat-button')

    with ui.splitter(value=15).classes('w-full h-full') as splitter:
        ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
        with splitter.before:
            with ui.tabs().props('vertical').classes('w-full') as tabs:
                dashboard_tab = ui.tab('My Dashboard', icon='mail')
                search_tab = ui.tab('Search', icon='search')
                blogs_tab = ui.tab('Blogs', icon='rss_feed')
                courses_tab = ui.tab('Courses', icon='school')
                handbooks_tab = ui.tab('Handbooks', icon='library_books')
                github_repos_tab = ui.tab('GitHub Repos', icon='eva-github').classes('text-2xl')
                research_papers_tab = ui.tab('Research Papers', icon='article')
                trending_repos_tab = ui.tab('Trending Repos', icon='trending_up')
                if app.storage.user['role'] == RoleType.ADMIN.value:
                    admin_tab = ui.tab('Admin Page', icon='admin_panel_settings')
                else:
                    resource_tab = ui.tab('Submit Resource', icon='cloud_upload')
                    # ui.link('Submit Resource', submit_resource)
        with splitter.after:
            with ui.tab_panels(tabs, value=dashboard_tab) \
                    .props('vertical').classes('w-full h-full'):
                with ui.tab_panel(dashboard_tab) as dashboard_panel:
                    asyncio.create_task(bookmarked(dashboard_panel))
                with ui.tab_panel(search_tab) as search_panel:
                    asyncio.create_task(search(search_panel))
                with ui.tab_panel(blogs_tab) as blogs_panel:
                    asyncio.create_task(blogs(blogs_panel))
                with ui.tab_panel(courses_tab) as course_panel:
                    asyncio.create_task(courses(course_panel))
                with ui.tab_panel(handbooks_tab) as handbooks_panel:
                    asyncio.create_task(handbooks(handbooks_panel))
                with ui.tab_panel(github_repos_tab) as github_panel:
                    asyncio.create_task(github_repos(github_panel))
                with ui.tab_panel(research_papers_tab) as research_panel:
                    asyncio.create_task(research_papers(research_panel))
                with ui.tab_panel(trending_repos_tab) as trending_panel:
                    asyncio.create_task(trending_repos(trending_panel))
                try:
                    with ui.tab_panel(admin_tab) as admin_panel:
                        asyncio.create_task(admin_page(admin_panel))
                except NameError:
                    # Not an admin user
                    print("Not an admin user")
                try:
                    with ui.tab_panel(resource_tab) as resource_panel:
                        asyncio.create_task(submit_resource_util(resource_panel))
                except NameError:
                    # Not a normal user
                    print("Not a normal user")

    with ui.page_sticky(x_offset=18, y_offset=18):
        ui.button('AI Bot', icon='smart_toy', on_click=chat_dialog.open).classes('chat-button')

    # if app.storage.user['role'] == RoleType.USER.value:
    #     with ui.page_sticky(x_offset=18, y_offset=18):
    #         link = ui.link('Submit Resource', submit_resource)
    #         link.style(
    #             'background-color: #17A2B8; color: white; padding: 10px 20px; text-align: center; '
    #             'text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; '
    #             'cursor: pointer; border-radius: 4px; border: none;')

async def trending_repos(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
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
                await trend(response.json()['items'] or [])
            running_query = None

@ui.refreshable
async def trend(repos) -> None:
    async def get_id(repo) -> int:
        repos: List[models.Resource] = await models.Resource.filter(url=repo['html_url'])
        if len(repos) > 0:
            return repos[0].id
        return None

    async def bookmark(repo) -> None:
        uid = app.storage.user.get('userid', None)
        if uid is not None:
            rid = await get_id(repo)
            if rid is None:
                await models.Resource.create(
                    title=repo['full_name'],
                    description=repo['description'],
                    image=repo['owner']['avatar_url'],
                    type=models.ResourceType.REPOSITORY,
                    url=repo['html_url'],
                    language=repo.get('language', None),
                    stars=repo.get('watchers_count', None)
                )
            rid = await get_id(repo)
            await models.Bookmark.create(userid=uid, resourceid=rid)
        trend.refresh()
        load_resource_page.refresh()

    async def unbookmark(rid) -> None:
        uid = app.storage.user.get('userid', None)
        if uid is not None:
            await models.Bookmark.filter(userid=uid, resourceid=rid).delete()
        trend.refresh()
        load_resource_page.refresh()

    bookmarks: List[models.Bookmark] = await models.Bookmark.filter(userid=app.storage.user.get('userid'))
    bookmark_ids = [b.resourceid for b in bookmarks]
    bookmarked_repos: List[models.Resource] = await models.Resource.filter(id__in=bookmark_ids)
    bookmarked_urls = {b.url: b.id for b in bookmarked_repos}

    sorted_repos = sorted(repos, key=lambda r: r['watchers_count'], reverse=True)
    with ui.list():
        for repo in sorted_repos:  # iterate over the response data of the api
            with ui.item():
                with ui.item_section().props('avatar'):
                    ui.image(repo['owner']['avatar_url'])
                with ui.item_section():
                    with ui.link(target=repo['html_url'], new_tab=True):
                        ui.item_label(repo['full_name']).classes('text-lg')
                    ui.item_label(repo['description']).props('caption').classes('text-lg').style(
                        'padding-top: 5px; padding-bottom: 5px;')
                    with ui.row().classes('items-center'):
                        ui.item_label(repo['language']).props('caption').classes('text-md')
                        ui.icon('star').style('margin-right: -12px;').classes('text-md')
                        ui.item_label(repo['watchers_count']).props('caption').classes('text-md')
                        with ui.link(target="https://github.com/" + repo['full_name'] + "/graphs/contributors",
                                     new_tab=True):
                            ui.chip('Contributors', text_color='white')
                if repo['html_url'] not in bookmarked_urls:
                    ui.chip('Bookmark', selectable=True, icon='bookmark', text_color="white",
                            on_click=lambda rep=repo: bookmark(rep)).classes('mt-2').props("dark")
                else:
                    ui.chip('Unbookmark', selectable=True, icon='bookmark', text_color="white", color='green',
                            on_click=lambda rid=bookmarked_urls[repo['html_url']]: unbookmark(rid)).classes('mt-2')


OPENAI_API_KEY = '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'
llm = ChatOpenAI(model_name='gpt-3.5-turbo', streaming=True, openai_api_key=OPENAI_API_KEY)
log = ui.log()  # Create a log element in the UI


async def send_message(query, output_container):
    if not query.value.strip():
        return

    try:
        question = query.value  # Use the query directly
        query.value = ''

        with output_container:
            ui.chat_message(text=question, name='You', sent=True).classes('message-user').style('align-self: flex-start; ')
            response_message = ui.chat_message(name='Chat Assistant', sent=False).style('align-self: flex-end')
            spinner = ui.spinner(type='dots')

        response = ''
        async for chunk in llm.astream(question, config={'callbacks': [NiceGuiLogElementCallbackHandler(log)]}):
            response += chunk.content
            response_message.clear()
            with response_message:
                ui.label(f"{response}").classes('chat-output message-ai')
        output_container.remove(spinner)

    except httpx.HTTPStatusError as e:
        response = f"An error occurred: HTTP error status {e.response.status_code}"
        response_message.clear()
        with response_message:
            ui.label(f"{response}").style('background-color: red; color: white; padding: 10px; border-radius: 5px;')

    except Exception as e:
        response = f"An error occurred: {str(e)}"
        response_message.clear()
        with response_message:
            ui.label(f"{response}").style('background-color: red; color: white; padding: 10px; border-radius: 5px;')


ui.run(storage_secret='THIS_NEEDS_TO_BE_CHANGED')