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

@ui.page('/submit_resource')
async def submit_resource() -> None:
    with ui.card().style("margin-left:10%;width:80%;font-size:15px"):
        ui.label("Enter resource details:")
        ui.select(label="Resource Type",
                  options=[ResourceType.BLOG, ResourceType.COURSE, ResourceType.HANDBOOK, ResourceType.REPOSITORY,
                           ResourceType.RESEARCH_PAPER], value=ResourceType.BLOG).style("width:40%"),
        ui.input('Title').style("width:40%")
        ui.input('Description').style("width:80%")
        ui.input('Url').style("width:80%")
        ui.input('Image').style("width:80%")

        def handle_upload(e: events.UploadEventArguments) -> None:
            ui.button(e.name, icon='file_download', on_click=lambda: ui.download(e.content.read(), e.name))

        ui.upload(on_upload=handle_upload, multiple=True)
        ui.button("Submit", on_click=lambda: print("Form submitted!"))
        # username = ui.input('Username').on('keydown.enter', try_login)
        # password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        # ui.button('Log in', on_click=try_login)