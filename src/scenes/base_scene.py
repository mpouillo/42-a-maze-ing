class BaseScene:
    def __init__(self, app) -> None:
        self.app = app
        self.model = None
        self.view = None

    def _cmd_open_menu(self):
        from src.scenes import MenuScene
        self.app.current_scene = MenuScene(self.app)

    def update(self):
        x, y = self.app.get_mouse_pos()
        for button in self.view.buttons.values():
            if button.is_hovered(x, y) != button.hover:
                button.hover = not button.hover

    def render(self):
        self.view.redraw_ui()
        self.view.refresh_layers()
