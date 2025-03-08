from nicegui import ui
from typing import List

import models

@ui.page('/admin')
async def admin_page() -> None:
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
            with ui.link(target=res.url):
                with ui.item():
                    with ui.item_section().props('avatar'):
                        ui.image(res.image)
                    with ui.item_section():
                        ui.item_label(res.title)
                        ui.item_label(res.description).props('caption')
                        ui.item_label(res.date).props('caption')
                        ui.item_label(res.authors).props('caption')
            ui.button(text='Approve', icon='check', on_click=lambda r=res: approve(r))
            ui.button(text='Reject', icon='cross', on_click=lambda r=res: decline(r))