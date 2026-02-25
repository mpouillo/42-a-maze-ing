import os
import random
import time
# from functools import partial
from src.algo import generate_maze
from src.models.maze_model import MazeModel
from src.views.maze_view import MazeView
from src.mlx import Mlx
from typing import Any


class MazeController:
    def __init__(self, config_file: str, window_width: int,
                 window_height: int) -> None:
        self.window_width = window_width
        self.window_height = window_height
        self.solving = False
        self.keys_pressed = set()

        # MLX Setup
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, window_width, window_height, "A-Maze-ing"
        )

        # Maze setup
        self.config_file = config_file
        self.maze_file = generate_maze(self.config_file)
        self.model = MazeModel(self.maze_file)
        self.view = MazeView(
            self.mlx, self.mlx_ptr, self.win_ptr,
            self.window_width, self.window_height, self.model
        )

        # Initial rendering
        self.view.render_maze()
        self.view.draw_endpoints()
        self.setup_ui()
        self.view.render_ui()
        self.view.refresh()

        # MLX hooks
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.handle_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.handle_keyrelease, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_window, None)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.handle_mouseclick, None)
        # self.mlx.mlx_hook(self.win_ptr, 6, 1 << 6,
        # self.handle_mousehover, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update_window, None)

    def run(self):
        self.mlx.mlx_loop(self.mlx_ptr)

    def setup_ui(self):
        self.view.clear_buttons()
        theme = self.view.ui_style
        btn_width = theme.get("btn_width", 0)
        btn_height = theme.get("btn_height", 0)
        btn_spacing = theme.get("btn_spacing", 0)

        self.view.add_button(
            "reset", "Reset Maze",
            (self.window_width - btn_width * 2 - btn_spacing) // 2,
            btn_spacing, 9999, btn_width, btn_height, self.reset_maze
        )
        self.view.add_button(
            "solve", "Solve Maze", (self.window_width + btn_spacing) // 2,
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

    def handle_keypress(self, keycode, param) -> None:
        self.keys_pressed.add(keycode)
        if 65307 in self.keys_pressed:    # Escape
            self.close_window()

    def handle_keyrelease(self, keycode, param) -> None:
        if keycode in self.keys_pressed:
            self.keys_pressed.remove(keycode)

    def handle_mouseclick(self, click, x, y, param) -> None:
        if click != 1:
            return

        for button in self.view.buttons.values():
            if button.is_hovered(x, y):
                if button.action:
                    button.action()

    def update_window(self, param: Any = None) -> None:
        if self.solving is True:
            current_time = time.time()
            if (
                current_time - self.view.last_path_update
                >= self.view.update_interval
            ):
                try:
                    next(self.view.path_gen)
                    self.view.last_path_update = current_time
                    self.view.refresh()
                except (StopIteration, AttributeError):
                    self.solving = False

    def close_window(self, param: Any = None) -> None:
        self.mlx.mlx_release(self.mlx_ptr)
        print("Exiting...")
        os._exit(0)

    def skip_solve(self):
        btn = self.view.buttons.get("skip")
        if self.model.path_step >= len(self.model.path):
            self.model.path_step = self.model.path_prev
            self.view.layers.get("path").clear()
            self.view.draw_endpoints()
            btn.label = "Skip"
        else:
            self.model.path_prev = self.model.path_step
            self.model.path_step = len(self.model.path)
            btn.label = "Undo"
        self.view.draw_path_to_step(self.model.path_step)
        self.view.render_ui()
        self.view.refresh()

        if self.solving:
            self.toggle_solve()

    def random_colors(self):
        for color in self.view.colors:
            self.view.colors[color] = random.randrange(0xFF000000, 0xFFFFFFFF)
        self.view.render_maze()
        self.view.draw_path_to_step(self.model.path_step)
        self.view.refresh()

    def reset_maze(self):
        self.solving = False
        self.setup_ui()

        maze_file = generate_maze(self.config_file)
        self.model.load_maze_data(maze_file)
        self.model.path_step = 0

        self.view.path_gen = self.view.render_path()
        self.model.path_step = 0

        self.view.layers.get("path").clear()
        self.view.render_maze()
        self.view.draw_endpoints()
        self.view.render_ui()
        self.view.refresh()

    def toggle_solve(self):
        self.solving = not self.solving
        btn = self.view.buttons.get("solve")

        if self.solving:
            if self.model.path_step >= len(self.model.path):
                self.model.path_step = 0
                self.view.layers.get("path").clear()
                self.view.draw_endpoints()
                self.view.path_gen = self.view.render_path()
                self.view.refresh()
            btn.label = "Pause"
            self.view.buttons.get("skip").label = "Skip"
        else:
            btn.label = "Solve Maze"
        self.view.render_ui()
        self.view.refresh()
