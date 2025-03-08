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

@ui.refreshable
async def load_resource_page(resource_type) -> None:
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
    resources: List[models.Resource] = await models.Resource.filter(type=resource_type)
    with ui.list():
        for resource in resources:
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
                        if resource.stars is not None:
                            ui.icon('star')
                            ui.item_label(resource.stars).props('caption')

            if resource.id not in bookmark_ids:
                ui.button(text='Bookmark', icon='bookmark', on_click=lambda rid=resource.id: bookmark(rid))
            else:
                ui.button(text='Unbookmark', icon='user', on_click=lambda rid=resource.id: unbookmark(rid))


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