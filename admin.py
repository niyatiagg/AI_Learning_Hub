from nicegui import events, ui
from typing import List

import models
from models import ResourceType


# @ui.page('/admin')
async def admin_page(container) -> None:
    with container:
        with ui.row().classes('flex flex-wrap justify-start items-stretch gap-4'):
            await admin_table()

@ui.refreshable
async def admin_table() -> None:
    async def approve(res: models.Unapproved) -> None:
        await models.Resource.create(title=res.title, description=res.description, type=res.type, url=res.url, image=res.url, date=res.date, authors=res.authors)
        await res.delete()
        admin_table.refresh()

    async def decline(res: models.Unapproved) -> None:
        await res.delete()
        admin_table.refresh()

    unapproved: List[models.Unapproved] = await models.Unapproved.all()
    with ui.list():
        for res in unapproved:  # iterate over the response data of the api
            # with ui.row().classes('items-center'):
            with ui.item():
                with ui.item_section().props('avatar'):
                    ui.image(res.image)
                with ui.item_section():
                    with ui.link(target=res.url):
                        ui.item_label(res.title).classes('text-lg')
                    ui.item_label(res.description).props('caption').classes('text-lg')
                    ui.item_label(res.date).props('caption')
                    ui.item_label(res.authors).props('caption')
                ui.button(text='Approve', icon='thumb_up_alt', on_click=lambda r=res: approve(r)).props("color=green").style('margin-right: 10px;').classes('h-4 w-25')
                ui.button(text='Reject', icon='thumb_down_alt', on_click=lambda r=res: decline(r)).props("color=red").classes('h-4 w-25')

# @ui.page('/submit_resource')
# async def submit_resource() -> None:
#     async def submit() -> None:
#         await models.Unapproved.create(title=title.value, description=description.value, type=resource_type, url=url.value,authors=authors.value,
#                                      image=image.value)
#         title.value=''
#         description.value=''
#         url.value=''
#         image.value=''
#         authors.value=''

#     resource_type = ResourceType.BLOG
#     def notify(value: ResourceType) -> None:
#         nonlocal resource_type
#         resource_type = value

#     with ui.card().style("margin-left:10%;width:80%;font-size:15px"):
#         ui.label("Enter Resource Details:")
#         ui.select(label="Resource Type",
#                   options=[ResourceType.BLOG, ResourceType.COURSE, ResourceType.HANDBOOK, ResourceType.REPOSITORY,
#                            ResourceType.RESEARCH_PAPER], value=ResourceType.BLOG, on_change=lambda e: notify(e.value)).style("width:40%"),
#         title = ui.input('Title').style("width:40%")
#         description = ui.input('Description').style("width:80%")
#         authors = ui.input('Author').style("width:80%")
#         url = ui.input('Url').style("width:80%")
#         image = ui.input('Image').style("width:80%")
#         ui.button("Submit", on_click=lambda: submit())