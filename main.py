#!/usr/bin/env python3
import asyncio
import httpx
from langchain_openai import ChatOpenAI
from log_callback_handler import NiceGuiLogElementCallbackHandler
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
    with ui.dialog() as chat_dialog:
        with ui.card():
            chat_output = ui.column()
            user_input = ui.input(placeholder="Ask me something about AI...")
            ui.button("Send", on_click=lambda: asyncio.create_task(send_message(user_input, chat_output)))

    ui.button("Chat with AI", on_click=chat_dialog.open).style('position: fixed; bottom: 20px; right: 20px; z-index: 1000;')

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


OPENAI_API_KEY = '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'  # TODO: set your OpenAI API key here

llm = ChatOpenAI(model_name='gpt-3.5-turbo', streaming=True, openai_api_key=OPENAI_API_KEY)
log = ui.log()  # Create a log element in the UI


async def send_message(query, output_container):
    if not query.value.strip():
        return

    try:
        question = query.value  # Use the query directly
        query.value = ''

        with output_container:
            ui.chat_message(text=question, name='You', sent=True)
            response_message = ui.chat_message(name='Chat Assistant', sent=False)
            spinner = ui.spinner(type='dots')

        response = ''
        async for chunk in llm.astream(question, config={'callbacks': [NiceGuiLogElementCallbackHandler(log)]}):
            response += chunk.content
            response_message.clear()
            with response_message:
                ui.label(f"{response}").style('background-color: blue; color: white; padding: 10px; border-radius: 5px;')
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