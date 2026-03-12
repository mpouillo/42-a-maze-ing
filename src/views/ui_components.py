from typing import Callable


class Button:
    def __init__(self, label: str, x: int, y: int, z: int,
                 width: int, height: int, action: Callable[[], None]) -> None:
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
        """Return whether mouse position is within button bounds"""
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)

    def enable(self) -> None:
        """Toggle enabled variable to True"""
        self.enabled = True

    def disable(self) -> None:
        """Toggle enabled variable to False"""
        self.enabled = False
