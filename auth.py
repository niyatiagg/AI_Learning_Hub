from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, List

import models

unrestricted_page_routes = {'/login'}

@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    async def try_login() -> None:  # local function to avoid passing username and password as arguments
        users: List[models.User] = await models.User.filter(username=username.value)
        if len(users) == 1 and users[0].password == password.value:
            app.storage.user.update({'username': username.value, 'userid': users[0].id, 'role': users[0].role.value, 'authenticated': True})
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')

     # Container to hold the repeated images
    with ui.row().style('position: relative; width: 100vw; height: 100vh; row-gap: 0px; column-gap: 0px;'):
        # Manually repeating the image to fill the space
        with ui.image("./image3.png").style('width: 100vw; height: 100vh; object-fit: contain;opacity: 0.9;'):
            with ui.card().classes('absolute-center').style('width: 300px; padding: 20px; opacity: 1.0; background-color: rgba(255, 255, 255, 0.9); border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); float: right;'):
                username = ui.input('Username').on('keydown.enter', try_login)
                password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
                ui.button('Log in', on_click=try_login)
    return None

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)

app.add_middleware(AuthMiddleware)