import models

from models import ResourceType
from nicegui.events import ValueChangeEventArguments
from nicegui import app, events, ui
from typing import List

# @ui.page('/blogs')
async def blogs(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await resource_page(ResourceType.BLOG)

# @ui.page('/courses')
async def courses(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await resource_page(ResourceType.COURSE)

# @ui.page('/courses')
async def handbooks(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await resource_page(ResourceType.HANDBOOK)

# @ui.page('/research_papers')
async def research_papers(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await resource_page(ResourceType.RESEARCH_PAPER)

# @ui.page('/github_repos')
async def github_repos(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await resource_page(ResourceType.REPOSITORY)

# @ui.page('/bookmarked')
async def bookmarked(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await load_resource_page(None)

async def resource_page(resource_type=None) -> None:
    resources: List[models.Resource] = await models.Resource.filter(type=resource_type)
    await load_resource_page(resources)

# @ui.refreshable
async def load_resource_page(resources) -> None:
    async def bookmark(rid) -> None:
        uid = app.storage.user.get('userid', None)
        if uid is not None:
            await models.Bookmark.create(userid=uid, resourceid=rid)

    async def unbookmark(rid) -> None:
        uid = app.storage.user.get('userid', None)
        if uid is not None:
            await models.Bookmark.filter(userid=uid, resourceid=rid).delete()

    bookmarks: List[models.Bookmark] = await models.Bookmark.filter(userid=app.storage.user.get('userid'))
    bookmark_ids = [b.resourceid for b in bookmarks]

    if resources is None:
        resources: List[models.Resource] = await models.Resource.filter(id__in=bookmark_ids)

    with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
        for res in resources:
            with ui.card().classes(
                    'flex flex-col w-96 shadow-lg hover:shadow-xl transition-shadow duration-300 min-h-96'):
                if res.image is not None:
                    ui.image(res.image).classes('w-full h-48 object-cover')  # Adjust size as necessary
                with ui.column().classes('flex-grow p-4'):
                    if res.url:
                        with ui.link(target=res.url):
                            ui.label(res.title).classes('text-lg font-semibold')
                    else:
                        ui.label(res.title).classes('text-lg font-semibold')
                    ui.label(res.description).classes('text-sm')
                    #TODO: show rating, reviews, duration for coursera

                    #TODO: show stars, language for github repos

                    #TODO: show category, date, authors whereever available
                    if res.id not in bookmark_ids:
                        ui.chip('Bookmark', selectable=True, icon='bookmark', text_color="white", 
                                on_click=lambda rid=res.id: bookmark(rid)).classes('mt-2').props("dark")
                    else:
                        ui.chip('Unbookmark', selectable=True, icon='bookmark', text_color="white", color='green',
                                on_click=lambda rid=res.id: unbookmark(rid)).classes('mt-2')

@ui.page('/search')
async def search(event: ValueChangeEventArguments) -> None:
    resources: List[models.Resource] = await models.Resource.filter(description__contains=event.sender.value)
    await load_resource_page(resources)