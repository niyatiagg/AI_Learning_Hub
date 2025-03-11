from tortoise.expressions import Q

import models

from models import ResourceType
from nicegui.events import ValueChangeEventArguments
from nicegui import app, events, ui
from typing import List

async def search(container) -> None:
    results = None
    resource_type = ResourceType.SELECT
    search_text = ''

    @ui.refreshable
    async def search_results() -> None:
        nonlocal results, resource_type, search_text
        async def bookmark(rid) -> None:
            uid = app.storage.user.get('userid', None)
            if uid is not None:
                await models.Bookmark.create(userid=uid, resourceid=rid)
            search_results.refresh()
            load_resource_page.refresh()

        async def unbookmark(rid) -> None:
            uid = app.storage.user.get('userid', None)
            if uid is not None:
                await models.Bookmark.filter(userid=uid, resourceid=rid).delete()
            search_results.refresh()
            load_resource_page.refresh()

        bookmarks: List[models.Bookmark] = await models.Bookmark.filter(userid=app.storage.user.get('userid'))
        bookmark_ids = [b.resourceid for b in bookmarks]

        results.clear()
        if resource_type == ResourceType.SELECT:
            resources: List[models.Resource] = await models.Resource.filter(Q(title__contains=search_text) | Q(description__contains=search_text)).order_by('-rating', '-stars', '-date')
        else:
            resources: List[models.Resource] = await models.Resource.filter(Q(type=resource_type) &
                                                                            (Q(title__contains=search_text) | Q(description__contains=search_text))).order_by('-rating', '-stars', '-date')
        with results:
            for res in resources:
                with ui.card().classes(
                        'flex flex-col w-96 shadow-lg hover:shadow-xl transition-shadow duration-300 min-h-96'):
                    load_fragment(res)
                    if res.id not in bookmark_ids:
                        ui.chip('Bookmark', selectable=True, icon='bookmark', text_color="white",
                                on_click=lambda rid=res.id: bookmark(rid)).classes('mt-2').props("dark")
                    else:
                        ui.chip('Unbookmark', selectable=True, icon='bookmark', text_color="white", color='green',
                                on_click=lambda rid=res.id: unbookmark(rid)).classes('mt-2')

    async def seee(event: ValueChangeEventArguments) -> None:
        nonlocal search_text
        search_text = event.sender.value
        await search_results()


    async def notify(value: ResourceType) -> None:
        nonlocal resource_type
        resource_type = value
        if search_text != '':
            await search_results()


    with container:
        with ui.row().classes('w-full justify-right items-center'):
            ui.icon('search').classes('text-xl').style('position: absolute; padding-left: 260px; padding-top: 2px; color: grey;')
            ui.input(label="search query", placeholder="Search bar").on('keydown.enter', seee).props(
                'clearable outlined dense outline standout v-model="text" dense="dense" size=32').style('background-color: white; margin-left: 20px;')
            ui.select(label="Resource Type",
                      options=[ResourceType.BLOG, ResourceType.COURSE, ResourceType.HANDBOOK, ResourceType.REPOSITORY,
                           ResourceType.RESEARCH_PAPER, ResourceType.SELECT], value=ResourceType.SELECT,
                      on_change=lambda e: notify(e.value)).style("width:15%; margin-top: -20px;")
        results = ui.row().classes('flex flex-wrap justify-start items-stretch gap-4')



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
    resources: List[models.Resource] = await models.Resource.filter(type=resource_type).order_by('-stars', '-rating', '-date')
    await load_resource_page(resources)

@ui.refreshable
async def load_resource_page(resources) -> None:
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

    if resources is None:
        resources: List[models.Resource] = await models.Resource.filter(id__in=bookmark_ids).order_by('-rating', '-stars', '-date')

    with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
        for res in resources:
            with ui.card().classes(
                    'flex flex-col w-96 shadow-lg hover:shadow-xl transition-shadow duration-300 min-h-96'):
                load_fragment(res)
                if res.id not in bookmark_ids:
                    ui.chip('Bookmark', selectable=True, icon='bookmark', text_color="white",
                            on_click=lambda rid=res.id: bookmark(rid)).classes('mt-2').props("dark")
                else:
                    ui.chip('Unbookmark', selectable=True, icon='bookmark', text_color="white", color='green',
                            on_click=lambda rid=res.id: unbookmark(rid)).classes('mt-2')

def load_fragment(res) -> None:
        if res.image is not None:
            ui.image(res.image).classes('w-full h-48 object-cover')  # Adjust size as necessary
        with ui.column().classes('flex-grow p-4'):
            if res.url:
                with ui.link(target=res.url, new_tab=True):
                    ui.label(res.title).classes('text-lg font-semibold')
            else:
                ui.label(res.title).classes('text-lg font-semibold')
            if res.date:
                ui.label(res.date).classes('text-sm')
            if res.authors:
                ui.label("Authors: " + res.authors).classes('text-sm font-semibold').style('font-family: system-ui')
            if res.category:
                ui.label("Category: " + res.category).classes('text-sm')
            des = res.description if len(res.description) < 255 else res.description[:255] + '...More'
            ui.label(des).classes('text-md')
            if res.rating:
                ui.label("Rating: " + res.rating).classes('text-sm')
            if res.review:
                ui.label("Reviews: " + res.review).classes('text-sm')
            if res.duration:
                ui.label("Level time: " + res.duration).classes('text-sm')
            if res.language:
                ui.label("Language: " + res.language).classes('text-sm')
            if res.stars:
                #ui.icon('star').style('margin-right: -12px;').classes('text-md')
                ui.label("Stars: " + str(res.stars)).classes('text-sm')
                with ui.link(target="https://github.com/" + res.title + "/graphs/contributors", new_tab=True):
                    ui.chip('Contributors')

async def submit_resource_util(container) -> None:
    async def submit() -> None:
        await models.Unapproved.create(title=title.value, description=description.value, type=resource_type, url=url.value,authors=authors.value,
                                     image=image.value)
        title.value=''
        description.value=''
        url.value=''
        image.value=''
        authors.value=''
        ui.notify(f'Resource submitted successfully. Pending Admin Approval.')

    resource_type = ResourceType.BLOG
    def notify(value: ResourceType) -> None:
        nonlocal resource_type
        resource_type = value
    with container:
        with ui.card().style("margin-left:10%;width:80%;font-size:15px"):
            ui.label("Enter Resource Details:")
            ui.select(label="Resource Type",
                      options=[ResourceType.BLOG, ResourceType.COURSE, ResourceType.HANDBOOK, ResourceType.REPOSITORY,
                               ResourceType.RESEARCH_PAPER], value=ResourceType.BLOG, on_change=lambda e: notify(e.value)).style("width:40%"),
            title = ui.input('Title').style("width:40%")
            description = ui.input('Description').style("width:80%")
            authors = ui.input('Author').style("width:80%")
            url = ui.input('Url').style("width:80%")
            image = ui.input('Image').style("width:80%")
            ui.button("Submit", icon='upload', on_click=lambda: submit())
