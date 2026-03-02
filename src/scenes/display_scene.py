import random
from src.models import MazeModel
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer
from typing import Any


class SolveScene(BaseScene):
    def __init__(self) -> None:
        self.solving = False

        # Model/View setup
        self.model = MazeModel(self.config_file)
        self.view = SquareRenderer(self.model)

        # Button setup
        self.setup_ui()

    def setup_ui(self):
        self.view.clear_buttons()
        btn_width = self.view.ui_style.get("btn_width", 0)
        btn_height = self.view.ui_style.get("btn_height", 0)
        btn_spacing = self.view.ui_style.get("btn_spacing", 0)

        self.view.add_button(
            "regen", "Regenerate",
            (self.window_width - btn_width * 2 - btn_spacing) // 2,
            btn_spacing, 9999, btn_width, btn_height, self.regen_maze
        )
        self.view.add_button(
            "solve", "Play", (self.window_width + btn_spacing) // 2,
            btn_spacing, 9999, btn_width, btn_height, self.toggle_solve
        )
        self.view.add_button(
            "random_colors", "Random colors",
            (self.window_width - btn_width * 2 - btn_spacing) // 2,
            btn_spacing * 2 + btn_height, 9999, btn_width, btn_height,
            self.random_colors
        )
        self.view.add_button(
            "skip", "Skip", (self.window_width + btn_spacing) // 2,
            btn_spacing * 2 + btn_height, 9999, btn_width, btn_height,
            self.skip_solve
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
            self.view.refresh()
