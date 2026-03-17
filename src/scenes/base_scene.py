from typing import Any


class BaseScene:
    def __init__(self, app: Any) -> None:
        self.app: Any = app
        self.model: Any = None
        self.view: Any = None

    def _cmd_open_menu(self) -> None:
        """Change current scene to menu scene"""
        from src.scenes import MenuScene

        self.app.current_scene = MenuScene(self.app)

    def update(self) -> None:
        """Execute UI updates"""
        x, y = self.app.get_mouse_pos()
        for button in self.view.buttons.values():
            if button.is_hovered(x, y) != button.hover:
                button.hover = not button.hover

    def render(self) -> None:
        """Update current frame"""
        self.view.redraw_ui()
        self.view.refresh_layers()
