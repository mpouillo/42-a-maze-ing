import random
from src.models import MazeModel
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer
from typing import Any


class DisplayScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.model = MazeModel(self.app.config_file)
        self.view = SquareRenderer(self.app, self.model)

        self.solving = False
        self.setup_ui()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["regen", "Regenerate", self.regen_maze],
            ["solve", "Play", self.toggle_solve],
            ["colors", "Random colors", self.random_colors],
            ["skip", "Skip", self.skip_solve]
        ]

        btn_width = min(self.view.ui_style.get("btn_width", 0),
                        round(self.app.window_width // len(btn_data) * 0.8)
                        )
        btn_height = self.view.ui_style.get("btn_height", 0)
        btn_spacing = ((self.app.window_width - (len(btn_data) * btn_width))
                       // (len(btn_data) + 1))

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0], b[1], (i + 1) * btn_spacing + (i * btn_width),
                (self.view.pad_h - btn_height) // 2, 9999,
                btn_width, btn_height, b[2]
            )

        self.view.add_button(
            "menu", "Menu",
            self.app.window_width - (self.view.pad_w + btn_width),
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999, btn_width, btn_height, self.open_menu
        )

    def regen_maze(self):
        self.solving = False
        self.setup_ui()
        self.model.regenerate_maze()
        self.view.refresh()

    def toggle_solve(self):
        self.solving = not self.solving
        btn = self.view.buttons.get("solve")

        if self.solving:
            if self.model.path_step >= len(self.model.path):
                self.model.path_step = 0
                self.view.layers.get("path").clear()
                self.view.refresh()
            btn.label = "Pause"
            self.view.buttons.get("skip").label = "Skip"
        else:
            btn.label = "Play"
        self.view.refresh()

    def skip_solve(self):
        btn = self.view.buttons.get("skip")
        if self.model.path_step >= len(self.model.path):
            self.model.path_step = self.model.path_prev
            btn.label = "Skip"
        else:
            self.model.path_prev = self.model.path_step
            self.model.path_step = len(self.model.path)
            btn.label = "Undo"
        self.view.refresh()

        if self.solving:
            self.toggle_solve()

    def random_colors(self):
        for color in self.view.colors:
            self.view.colors[color] = random.randrange(0xFF000000, 0xFFFFFFFF)
        self.view.refresh()

    def update(self, param: Any = None) -> None:
        if self.solving is True:
            if self.model.path_step == len(self.model.path):
                self.solving = False
                self.model.path_prev = len(self.model.path)
                self.setup_ui()  # Reset UI to remove "Pause" label

            else:
                self.model.path_step += 1

        super().update()

    def render(self):
        self.view.render_maze()
        self.view.render_path()
        self.view.render_ui()
        self.view.refresh()
