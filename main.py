#!/usr/bin/env python3
import asyncio
import httpx

from admin import admin_page, submit_resource
from langchain_openai import ChatOpenAI
from log_callback_handler import NiceGuiLogElementCallbackHandler
from auth import AuthMiddleware, login
from nicegui import app, ui
from tortoise import Tortoise
from typing import Optional

from models import RoleType
from utils import bookmarked, blogs, courses, github_repos, research_papers, search

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
            ui.label('AI Learning Hub').classes('text-3xl font-semi')
        with ui.row().classes('items-center gap-x-6'):
            ui.input(label="search query", placeholder="Search bar").on('keydown.enter', search).props('clearable outlined dense outline').style('background-color: white;')
            ui.label(f'{app.storage.user["username"]}').classes('text-xl')
            ui.chip(on_click=lambda: logout(), icon='logout').props('outline').classes('shadow-lg text-white')

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
            with ui.row().classes('items-center gap-x-2'):
                user_input = ui.input(placeholder="Ask me something about AI...").classes('input-base').props('autofocus')
                send_button = ui.button('Send', on_click=lambda: asyncio.create_task(send_message(user_input, chat_output))).classes('send-button')
    # ui.button('Chat', on_click=chat_dialog.open).classes('chat-button')

    with ui.splitter(value=30).classes('w-full h-full') as splitter:
        with splitter.before:
            with ui.tabs().props('vertical').classes('w-full') as tabs:
                dashboard_tab = ui.tab('Personalized Dashboard', icon='mail')
                courses_tab = ui.tab('Courses', icon='school')
                handbooks_tab = ui.tab('Handbooks', icon='library_books')
                github_repos_tab = ui.tab('GitHub Repos', icon='code')
                trending_repos_tab = ui.tab('Trending Repos', icon='trending_up')
                research_papers_tab = ui.tab('Research Papers', icon='article')
                blogs_tab = ui.tab('Blogs', icon='rss_feed')
        with splitter.after:
            with ui.tab_panels(tabs, value=dashboard_tab) \
                    .props('vertical').classes('w-full h-full'):
                with ui.tab_panel(dashboard_tab) as dashboard_panel:
                    asyncio.create_task(bookmarked(dashboard_panel))
                with ui.tab_panel(courses_tab) as course_panel:
                    asyncio.create_task(courses(course_panel))
                with ui.tab_panel(handbooks_tab) as handbooks_panel:
                    asyncio.create_task(github_repos(handbooks_panel))
                with ui.tab_panel(github_repos_tab) as github_panel:
                    asyncio.create_task(github_repos(github_panel))
                with ui.tab_panel(trending_repos_tab) as trending_panel:
                    asyncio.create_task(trending_repos(trending_panel))
                with ui.tab_panel(research_papers_tab) as research_panel:
                    asyncio.create_task(research_papers(research_panel))
                with ui.tab_panel(blogs_tab) as blogs_panel:
                    asyncio.create_task(blogs(blogs_panel))


    if app.storage.user['role'] == RoleType.ADMIN.value:
        ui.link('Admin', admin_page)
    else:
        ui.link('Submit Resource', submit_resource)

    ui.button('Chat', on_click=chat_dialog.open).classes('chat-button')

# @ui.page('/trending_repos')
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