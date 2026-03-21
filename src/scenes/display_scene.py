"""Maze display (demo) scene.

This scene animates maze generation/solving and allows toggling between
different shortest valid paths.
"""

from src.models.maze import MazeGenerator
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer, HexRenderer
from typing import Any, Callable, TypeAlias

BtnData: TypeAlias = list[tuple[str, str, Callable[[], None]]]


class DisplayScene(BaseScene):
    """Scene that visualizes maze generation and solution paths."""

    def __init__(self, app: Any) -> None:
        """Create the display scene and initialize renderer/model."""
        super().__init__(app)

        self.solving: bool = False
        self.generating: bool = False
        self.solve_step: int = 0
        self.gen_step: int = 0
        self.current_path: int = 0

        self.model: Any = MazeGenerator()
        self.view: Any = None

        if self.model.config.is_hex is True:
            self.view = HexRenderer(self.app, self.model)
        else:
            self.view = SquareRenderer(self.app, self.model)

        self.setup_ui()
        self.view.draw_maze()
        self.view.draw_endpoints()

    def setup_ui(self) -> None:
        """Create and position the display scene buttons."""
        self.view.clear_buttons()

        btn_data: BtnData = [
            ("regen", "Generate", self._cmd_generate_maze),
            ("solve", "Solve", self._cmd_solve_maze),
            ("paths", "Toggle paths", self._cmd_toggle_paths),
        ]

        btn_width: int = min(
            self.view.ui_style.get("btn_width", 0),
            round(self.app.window_width // len(btn_data) * 0.8),
        )
        btn_height: int = self.view.ui_style.get("btn_height", 0)
        btn_spacing: int = (
            self.app.window_width - (len(btn_data) * btn_width)
        ) // (len(btn_data) + 1)

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0],
                b[1],
                (i + 1) * btn_spacing + (i * btn_width),
                (self.view.pad_h - btn_height) // 2,
                9999,
                btn_width,
                btn_height,
                b[2],
            )

        self.view.add_button(
            "menu",
            "Menu",
            self.app.window_width - (self.view.pad_w + btn_width),
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999,
            btn_width,
            btn_height,
            self._cmd_open_menu,
        )

    def _cmd_generate_maze(self) -> None:
        """Start maze generation animation or skip to the end."""
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

    def _cmd_solve_maze(self) -> None:
        """Start maze solving animation or skip to the end."""
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

    def _cmd_toggle_paths(self) -> None:
        """Cycle through (or hide) the available valid shortest paths."""
        if self.solving:
            self.solving = False

        if 65507 in self.app.keypresses:
            self.view.clear_layers("path")
            return

        if not self.model.valid_paths:
            return

        self.view.draw_path(self.model.valid_paths[self.current_path])
        self.view.draw_endpoints()

        canvas = self.view.layers.get("popup")
        canvas.clear()
        self.view.draw_text(
            canvas,
            self.view.offset_x,
            self.app.window_height - self.view.pad_h + 20,
            (
                f"Displaying path: {self.current_path + 1}/"
                f"{len(self.model.valid_paths)}"
                f"({len(self.model.valid_paths[self.current_path])})"
            ),
            0xFFFFFFFF,
            3,
        )

        self.current_path += 1
        if self.current_path >= len(self.model.valid_paths):
            self.current_path = 0

    def update(self) -> None:
        """Advance generation/solving animations and update UI state."""
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

        if not self.model.valid_paths or self.gen_step < len(
            self.model.gen_steps
        ):
            self.view.buttons.get("solve").disable()
            self.view.buttons.get("paths").disable()
        else:
            self.view.buttons.get("solve").enable()
            self.view.buttons.get("paths").enable()

        super().update()

    def render(self) -> None:
        """Render the display scene frame."""
        super().render()
