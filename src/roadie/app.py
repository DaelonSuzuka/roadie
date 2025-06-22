import nicegui.ui as ui  # noqa: E402


@ui.page('/')
def index():
    ui.header()
    with ui.column().classes('w-full h-[calc(100vh-6rem)] grow border border-red-200'):
        ui.label('top')
        ui.space()
        ui.label('bottom')
    ui.footer()
