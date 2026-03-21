"""UI components used by the MLX views.

This module currently provides a minimal clickable :class:`~Button` abstraction
used by renderers/scenes.
"""

from typing import Callable


class Button:
    """Clickable UI button.

    Args:
        label: Text displayed on the button.
        x: Left coordinate in window space.
        y: Top coordinate in window space.
        z: Z-index used when drawing.
        width: Button width in pixels.
        height: Button height in pixels.
        action: Callback executed on click.
    """

    def __init__(
        self,
        label: str,
        x: int,
        y: int,
        z: int,
        width: int,
        height: int,
        action: Callable[[], None],
    ) -> None:
        self.label: str = label
        self.x: int = x
        self.y: int = y
        self.z: int = z
        self.width: int = width
        self.height: int = height
        self.action: Callable[[], None] = action
        self.hover: bool = False
        self.enabled: bool = True

    def is_hovered(self, mouse_x: int, mouse_y: int) -> bool:
        """Return whether the mouse position is inside the button bounds."""
        return (
            self.x <= mouse_x <= self.x + self.width
            and self.y <= mouse_y <= self.y + self.height
        )

    def enable(self) -> None:
        """Enable the button (makes it clickable and changes rendering)."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the button (prevents interactions and changes rendering)."""
        self.enabled = False
