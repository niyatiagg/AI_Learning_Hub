import models

from models import ResourceType
from nicegui.events import ValueChangeEventArguments
from nicegui import app, ui
from typing import List

@ui.page('/courses')
async def courses() -> None:
    await load_resource_page(ResourceType.COURSE)

@ui.page('/research_papers')
async def research_papers() -> None:
    await load_resource_page(ResourceType.RESEARCH_PAPER)

@ui.page('/blogs')
async def blogs() -> None:
    await load_resource_page(ResourceType.BLOG)

@ui.page('/github_repos')
async def github_repos() -> None:
    await load_resource_page(ResourceType.REPOSITORY)

@ui.page('/bookmarked')
async def bookmarked() -> None:
    await load_resource_page()

@ui.refreshable
async def load_resource_page(resource_type=None) -> None:
    async def bookmark(rid) -> None:
        uid = app.storage.user.get('userid', None)
        if uid is not None:
            await models.Bookmark.create(userid=uid, resourceid=rid)
        load_resource_page.refresh()

    async def unbookmark(rid) -> None:
        uid = app.storage.user.get('userid', None)
        if uid is not None:
            await models.Bookmark.filter(userid=uid, resourceid=rid).delete()
        load_resource_page.refresh()

    bookmarks: List[models.Bookmark] = await models.Bookmark.filter(userid=app.storage.user.get('userid'))
    bookmark_ids = [b.resourceid for b in bookmarks]
    resources: List[models.Resource] = []
    if resource_type is None:
        resources = await models.Resource.filter(id__in=bookmark_ids)
    else:
        resources = await models.Resource.filter(type=resource_type)

    with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
        for resource in resources:
            with ui.card().classes('flex flex-col w-96 shadow-lg hover:shadow-xl transition-shadow duration-300 min-h-96'):
                ui.image(resource.image).classes('w-full h-48 object-cover')  # Adjust size as necessary
                with ui.column().classes('flex-grow p-4'):
                    if resource.url:
                        with ui.link(target=resource.url):
                            ui.label(resource.title).classes('text-lg font-semibold')
                    else:
                        ui.label(resource.title).classes('text-lg font-semibold')
                    ui.label(resource.description).classes('text-sm')
                    if resource.id not in bookmark_ids:
                        ui.chip('Bookmark', selectable=True, icon='bookmark', on_click=lambda rid=resource.id: bookmark(rid)).classes('mt-2')
                    else:
                        ui.chip('Unbookmark', selectable=True, icon='bookmark', on_click=lambda rid=resource.id: unbookmark(rid)).classes('mt-2')


async def search(event: ValueChangeEventArguments) -> None:
    resources: List[models.Resource] = await models.Resource.filter(description__contains=event.sender.value)
    with ui.list():
        for resource in resources:  # iterate over the response data of the api
            with ui.link(target=resource.url):
                with ui.item():
                    with ui.item_section().props('avatar'):
                        ui.image(resource.image)
                    with ui.item_section():
                        ui.item_label(resource.title)
                        ui.item_label(resource.description).props('caption')
                        ui.item_label(resource.category).props('caption')
                        ui.item_label(resource.date).props('caption')
                        ui.item_label(resource.language).props('caption')
                        ui.item_label(resource.authors).props('caption')