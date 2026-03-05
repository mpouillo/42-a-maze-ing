import random
from src.models.maze import MazeModel
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer, HexRenderer


class DisplayScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)

        self.model = MazeModel(self.app.config_file)

        if self.model.config.is_hex is True:
            self.view = HexRenderer(self.app, self.model)
        else:
            self.view = SquareRenderer(self.app, self.model)

        self.solving = False
        self.solve_step = 0
        self.generating = False
        self.gen_step = 0

        self.setup_ui()
        self.view.draw_maze()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["regen", "Generate", self._cmd_generate_maze],
            ["solve", "Solve", self._cmd_solve_maze],
            ["colors", "Random colors", self._cmd_random_colors],
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
            9999, btn_width, btn_height, self._cmd_open_menu
        )

    def _cmd_generate_maze(self):
        self.solving = False

        if self.generating:
            self.generating = False
            self.view.draw_maze()
            self.view.buttons.get("regen").label = "Generate"
            self.view.buttons.get("solve").enable()
            self.gen_step = len(self.model.gen_steps)
        else:
            self.model.generator.initialize_maze_grid()
            self.view.draw_maze()
            self.render("maze")
            self.model.generate_new_maze()
            self.view.buttons.get("regen").label = "Skip"
            self.view.buttons.get("solve").disable()
            self.gen_step = 0
            self.generating = True

        self.render("ui")

    def _cmd_solve_maze(self):
        if self.generating or not self.model.path:
            return

        if self.solving:
            self.solving = False
            self.view.buttons.get("solve").label = "Solve"
            self.solve_step = len(self.model.solve_steps)
        else:
            self.view.buttons.get("solve").label = "Skip"
            self.solve_step = 0
            self.solving = True

        self.render("ui")

    def _cmd_random_colors(self):
        for color in self.view.colors:
            self.view.colors[color] = random.randrange(0xFF000000, 0xFFFFFFFF)
        self.render("maze", "path")

    def update(self) -> None:
        if self.generating is True:
            if self.gen_step >= len(self.model.gen_steps):
                self.generating = False
                self.gen_step = 0
            else:
                self.gen_step += 1
                self.view.draw_step(self.model.gen_steps[self.gen_step],
                                    0xFF000000)

        if self.solving is True:
            if self.solve_step >= len(self.model.solve_steps):
                self.solving = False
                self.solve_step = 0
            else:
                if self.solve_step > 1:
                    self.view.draw_step(
                        self.model.solve_steps[self.solve_step - 1],
                        self.view.colors.get("gen") & 0x7FFFFFFF
                    )
                self.view.draw_step(self.model.solve_steps[self.solve_step],
                                    self.view.colors.get("gen"))
                self.solve_step += 1

        super().update()

    def render(self, *args):
        if args:
            if "maze" in args:
                self.view.draw_maze()
            if "path" in args:
                self.view.draw_path()
            if "ui" in args:
                self.view.draw_ui()
            self.view.refresh_layers()
            return

        self.view.draw_ui()
        self.view.refresh_layers()
