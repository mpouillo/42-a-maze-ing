"""Scene base class.

Scenes encapsulate user interactions and coordinate the model/view for a given
UI state (menu, display, game, settings).
"""

from typing import Any


class BaseScene:
    """Base class for all scenes.

    A scene owns a *model* and a *view* (renderer) and provides `update` and
    `render` hooks called by the main application loop.
    """

    def __init__(self, app: Any) -> None:
        """Create a scene bound to the given application instance."""
        self.app: Any = app
        self.model: Any = None
        self.view: Any = None

    def _cmd_open_menu(self) -> None:
        """Switch the current application scene to :class:`~MenuScene`."""
        from src.scenes import MenuScene

        self.app.current_scene = MenuScene(self.app)

    def update(self) -> None:
        """Update hover states and other per-frame scene logic."""
        x, y = self.app.get_mouse_pos()
        for button in self.view.buttons.values():
            if button.is_hovered(x, y) != button.hover:
                button.hover = not button.hover

    def render(self) -> None:
        """Render the current frame for this scene."""
        self.view.redraw_ui()
        self.view.refresh_layers()
