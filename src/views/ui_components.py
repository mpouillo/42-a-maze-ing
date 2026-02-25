class Button:
    def __init__(self, label: str, x: int, y: int, z: int,
                 width: int, height: int, action: callable) -> None:
        self.label = label
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.action = action
        self.hover = False

    def is_hovered(self, mouse_x: int, mouse_y: int) -> bool:
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)
