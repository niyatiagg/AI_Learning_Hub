from nicegui import ui
from typing import List

from nicegui.events import ValueChangeEventArguments

import models
from models import ResourceType

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
    repos: List[models.Resource] = await models.Resource.filter(type=models.ResourceType.REPOSITORY)
    with ui.list():
        for repo in repos:  # iterate over the response data of the api
            with ui.link(target=repo.url):
                with ui.item():
                    with ui.item_section().props('avatar'):
                        ui.image(repo.image)
                    with ui.item_section():
                        ui.item_label(repo.title)
                        ui.item_label(repo.description).props('caption')
                        ui.item_label(repo.category).props('caption')
                        ui.item_label(repo.language).props('caption')
                        ui.item_label(repo.date).props('caption')
                        ui.icon('star')
                        ui.item_label(repo.stars).props('caption')

async def load_resource_page(resource_type) -> None:
    resources: List[models.Resource] = await models.Resource.filter(type=models.ResourceType.REPOSITORY)
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