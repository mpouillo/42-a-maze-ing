from src.models.maze import MazeModel
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer, HexRenderer


class DisplayScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.solving = False
        self.generating = False
        self.solve_step = 0
        self.gen_step = 0
        self.current_path = 0

        self.model = MazeModel()

        if self.model.config.is_hex is True:
            self.view = HexRenderer(self.app, self.model)
        else:
            self.view = SquareRenderer(self.app, self.model)

        self.setup_ui()
        self.view.draw_maze()
        self.view.draw_endpoints()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["regen", "Generate", self._cmd_generate_maze],
            ["solve", "Solve", self._cmd_solve_maze],
            ["paths", "Toggle paths", self._cmd_toggle_paths],
        ]

        btn_width = min(self.view.ui_style.get("btn_width", 0), round(
            self.app.window_width // len(btn_data) * 0.8))
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

        self.view.add_button(
            "colors", "rdm wall colors",
            self.view.pad_w,
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999, btn_width, btn_height, self._cmd_random_wall_colors
        )

    def _cmd_random_wall_colors(self):
        if self.generating:
            return

        import random
        self.view.colors["walls"] = random.randrange(0xFF000000, 0xFFFFFFFF)
        self.view.draw_maze()

    def _cmd_generate_maze(self):
        self.solving = False

        if self.generating:
            while self.gen_step < len(self.model.gen_steps):
                self.view.draw_step(self.model.gen_steps[self.gen_step])
                self.gen_step += 1
        else:
            self.view.clear_layers("maze", "path", "popup")
            self.model.initialize_maze()
            self.view.draw_maze()
            self.model.generate_new_maze()
            self.view.buttons.get("regen").label = "Skip"
            self.gen_step = 0
            self.generating = True

    def _cmd_solve_maze(self):
        if self.generating:
            return

        if self.solving:
            while self.solve_step < len(self.model.solve_steps):
                self.view.draw_step(self.model.solve_steps[self.solve_step])
                self.solve_step += 1
        else:
            self.view.clear_layers("path", "popup")
            self.view.buttons.get("solve").label = "Skip"
            self.solve_step = 0
            self.solving = True

    def _cmd_toggle_paths(self):
        if self.solving:
            self.solving = False

        if 65507 in self.app.keypresses:
            self.view.clear_layers("path")
            return

        if not self.model.valid_paths:
            return

        # Clamp current_path before using it
        if self.current_path >= len(self.model.valid_paths):
            self.current_path = 0

        self.view.draw_path(self.model.valid_paths[self.current_path])
        self.view.draw_endpoints()

        self.current_path += 1
        if self.current_path > len(self.model.valid_paths) - 1:
            self.current_path = 0

        canvas = self.view.layers.get("popup")
        canvas.clear()
        self.view.draw_text(
            canvas, self.view.offset_x,
            self.app.window_height - self.view.pad_h,
            (f"Displaying path: {self.current_path + 1}/"
             f"{len(self.model.valid_paths)}"
             f"({len(self.model.valid_paths[self.current_path])})"),
            0xFFFFFFFF, 3
        )

    def update(self) -> None:
        if self.generating is True:
            if self.gen_step >= len(self.model.gen_steps):
                self.view.draw_maze()
                self.generating = False
                self.setup_ui()
            else:
                self.view.draw_step(self.model.gen_steps[self.gen_step])
                self.gen_step += 1

        elif self.solving is True:
            if self.solve_step >= len(self.model.solve_steps):
                self.view.draw_maze()
                self.solving = False
                self.setup_ui()
            else:
                self.view.draw_step(self.model.solve_steps[self.solve_step])
                self.solve_step += 1

        if (
            not self.model.valid_paths
            or self.gen_step < len(self.model.gen_steps)
        ):
            self.view.buttons.get("solve").disable()
            self.view.buttons.get("paths").disable()
            self.view.buttons.get("colors").disable()
        else:
            self.view.buttons.get("solve").enable()
            self.view.buttons.get("paths").enable()
            self.view.buttons.get("colors").enable()

        super().update()

    def render(self, *args):
        super().render()
