import os
import random
import time
from functools import partial
from src.algo import generate_maze
from src.draw_maze import DrawMaze
from src.mlx import Mlx
from typing import Any


class Window:
    def __init__(self, maze_file: str, config_file: str,
                 width: int, height: int) -> None:
        # MLX Setup
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, width, height, "A-Maze-ing Display"
        )
        self.maze_file = maze_file
        self.width = width
        self.height = height

        # Display Output
        self.maze = DrawMaze(
            self.mlx, self.mlx_ptr, self.win_ptr,
            width, height, config_file, maze_file
        )

        self.maze.rebuild_maze()
        self.create_ui()

        # MLX update hooks
        self.keys_pressed = set()
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.handle_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.handle_keyrelease, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_window, None)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.handle_mouse, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update_window, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def create_ui(self) -> None:
        if getattr(self, "buttons", None):
            self.remove_buttons()
        self.buttons = {}
        self.b_large_w = 300
        self.b_large_h = 60
        self.b_small_w = 100
        self.b_small_h = 60
        self.create_button(
            "reset_maze", (self.width - self.b_large_w) // 2, 20,
            self.b_large_w, self.b_large_h, 0xFFFF007F,
            "Regenerate Maze", 0xFFFFFFFF
        )
        self.create_button(
            "solve_maze", (self.width - self.b_large_w) // 2, 100,
            self.b_large_w, self.b_large_h, 0xFF00FF7F,
            "Solve Maze", 0xFFFFFFFF
        )
        self.create_button(
            "walls_bigger", 20, 20,
            self.b_large_w, self.b_large_h, 0xFF007FFF,
            "Bigger walls", 0xFFFFFFFF
        )
        self.create_button(
            "walls_smaller", 20, 100,
             self.b_large_w, self.b_large_h, 0xFF007FFF,
            "Smaller walls", 0xFFFFFFFF
        )
        self.create_button(
            "maze_colors", self.width - self.b_large_w - 20, 20,
            self.b_large_w, self.b_large_h, 0xFF007FFF,
            "Random colors", 0xFFFFFFFF
        )

    def close_window(self, param: Any = None) -> None:
        self.maze.clear_layers()
        self.mlx.mlx_release(self.mlx_ptr)
        os._exit(0)

    def update_window(self, param: Any = None) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        if self.maze.solving:
            current_time = time.time()
            if (
                current_time - self.maze.last_path_update
                >= self.maze.update_interval
            ):
                try:
                    next(self.maze.path_gen)
                    self.maze.last_path_update = current_time
                except (StopIteration, AttributeError):
                    self.maze.solving = False
        self.maze.draw_layers_to_window()

    def create_button(self, name, x, y, width, height, bg_color,
                      text, text_color) -> None:
        canvas = self.maze.add_layer(x, y, 9999, width, height, name)
        outline = 6
        canvas.fill_rect(0, 0, width, height, 0xFFFFFFFF)
        canvas.fill_rect(0 + outline // 2, 0 + outline // 2,
                         max(0, width - outline),
                         max(0, height - outline),
                         bg_color)
        x_pos = (width - (len(text)
                 * (canvas.font_width + canvas.font_scale))) // 2
        y_pos = (height - canvas.font_height) // 2
        canvas.draw_text(x_pos, y_pos, text, text_color)
        self.buttons.update({name: canvas})
        return self.buttons.get(name)

    def remove_buttons(self, *names: str):
        if names:
            for name in names:
                if name in self.buttons:
                    self.maze.clear_layers(name)
                    self.buttons.pop(name, None)
        else:
            self.maze.clear_layers(*self.buttons.keys())
            self.buttons.clear()

    def get_clicked_button(self, x, y) -> dict:
        for button in reversed(list(self.buttons.values())):
            if (
                x > button.pos_x
                and x < button.pos_x + button.width
                and y > button.pos_y
                and y < button.pos_y + button.height
            ):
                return (button)
        return None

    def handle_keypress(self, keycode, param) -> None:
        self.keys_pressed.add(keycode)
        if 65307 in self.keys_pressed:    # Escape
            self.close_window()

    def handle_keyrelease(self, keycode, param) -> None:
        if keycode in self.keys_pressed:
            self.keys_pressed.remove(keycode)

    def handle_mouse(self, click, x, y, param) -> None:
        if click != 1:
            return

        button = self.get_clicked_button(x, y)
        if not button:
            return

        commands = {
            "maze_colors": self._cmd_random_colors,
            "reset_colors": self._cmd_reset_colors,
            "reset_maze": self._cmd_reset_maze,
            "skip_solve": self._cmd_skip_solve,
            "solve_faster": partial(self._cmd_adjust_speed, 0.5),
            "solve_slower": partial(self._cmd_adjust_speed, 2),
            "solve_maze": self._cmd_solve_maze,
            "walls_bigger": partial(self._cmd_resize_walls, 1),
            "walls_smaller": partial(self._cmd_resize_walls, -1),
        }

        action = commands.get(button.name)
        if action:
            action()

    def _cmd_reset_maze(self):
        generate_maze(self.maze_file)
        self.remove_buttons("solve_faster", "solve_slower",
                            "solve_speed", "skip_solve", "solve_maze")
        self.create_button(
            "solve_maze", (self.width - self.b_large_w) // 2, 100,
            self.b_large_w, self.b_large_h, 0xFF00FF7F,
            "Solve Maze", 0xFFFFFFFF
        )
        self.maze.update_maze_data(self.maze_file)
        self.maze.solving = False
        self.maze.path_step = 0
        self.maze.rebuild_maze()

    def _cmd_skip_solve(self):
        try:
            if hasattr(self.maze, "path_gen"):
                list(self.maze.path_gen)
        except Exception:
            pass

        self.maze.solving = False
        self.remove_buttons("solve_faster", "solve_slower",
                            "solve_speed", "skip_solve", "solve_maze")
        self.create_button(
            "solve_maze", (self.width - self.b_large_w) // 2, 100,
            self.b_large_w, self.b_large_h, 0xFF00FF7F,
            "Solve Maze", 0xFFFFFFFF
        )

    def _cmd_solve_maze(self):
        if self.maze.solving == True:
            self.maze.solving = False
            self.remove_buttons("pause_solving")
            self.create_button(
                "solve_maze", (self.width - self.b_large_w) // 2, 100,
                self.b_large_w, self.b_large_h, 0xFF00FF7F,
                "Solve Maze", 0xFFFFFFFF
            )
            return

        self.remove_buttons("solve_maze")
        self.create_button(
                "solve_maze", (self.width - self.b_large_w) // 2, 100,
                self.b_large_w, self.b_large_h, 0xFFFF007F,
                "Pause", 0xFFFFFFFF
            )
        step = (self.maze.path_step if self.maze.path_step
                != len(self.maze.VALID_PATH) - 1 else 0)
        self.maze.init_path_layer(step)
        self.maze.solving = True
        if "solve_faster" not in self.buttons:
            self.create_button(
                "solve_faster", (self.width - self.b_large_w)
                // 2 - self.b_large_w // 2 + 30, 100, self.b_small_w, self.b_small_h,
                0xFFFF7F7F, "+", 0xFFFFFFFF
            )
        if "solve_slower" not in self.buttons:
            self.create_button(
                "solve_slower", (self.width - self.b_large_w)
                // 2 - self.b_large_w + 60, 100, self.b_small_w, self.b_small_h,
                0xFF7F7FFF, "-", 0xFFFFFFFF
            )
        if "solve_speed" not in self.buttons:
            text = str(round(0.2 / self.maze.update_interval, 2)) + "x"
            self.create_button(
                "solve_speed", (self.width - self.b_large_w)
                // 2 - self.b_large_w + 60, 20, self.b_small_w * 2 + 20, self.b_small_h,
                0xFFFFFFFF, text, 0xFF000000
            )
        if "skip_solve" not in self.buttons:
            self.create_button(
                "skip_solve", (self.width - self.b_large_w)
                // 2 + self.b_large_w + 20, 100, self.b_small_w * 2 + 20, self.b_small_h,
                0xFF7F7F7F, "Skip", 0xFFFFFFFF
            )

    def _cmd_resize_walls(self, delta) -> None:
        current_step = getattr(self.maze, "path_step", 0)
        was_solving = self.maze.solving

        if delta > 0:
            self.maze.LINE_WEIGHT = min(
                self.maze.NODE_SIZE // 2,
                self.maze.LINE_WEIGHT + 1
            )
        else:
            self.maze.LINE_WEIGHT = max(1, self.maze.LINE_WEIGHT - 1)

        self.maze.update_maze_data(self.maze_file)
        self.maze.init_maze_layer()
        self.maze.init_path_layer(current_step)
        self.maze.solving = was_solving

    def _cmd_random_colors(self):
        self.maze.set_colors(
            *(random.randrange(0xFF0000FF, 0xFFFFFFFF) for _ in range(6))
        )
        self.maze.rebuild_maze()
        if "reset_colors" not in self.maze.layers.keys():
            self.create_button("reset_colors", self.width - self.b2_width - 20,
                               100, self.b2_width, self.b2_height, 0xFFFF7F00,
                               "Reset colors", 0xFFFFFFFF)

    def _cmd_reset_colors(self):
        self.maze.set_colors()
        self.maze.clear_layers("reset_colors")
        self.maze.rebuild_maze()

    def _cmd_adjust_speed(self, factor):
        if factor < 1:
            self.maze.update_interval = max(
                0.00625, self.maze.update_interval * factor
            )
        else:
            self.maze.update_interval = min(
                0.8, self.maze.update_interval * factor
            )

        if "solve_speed" in self.buttons:
            self.remove_buttons("solve_speed")
            text = str(round(0.2 / self.maze.update_interval, 2)) + "x"
            self.create_button(
                "solve_speed", (self.width - self.b_large_w)
                // 2 - self.b_large_w + 60, 20, self.b_small_w * 2 + 20, self.b_small_h,
                0xFFFFFFFF, text, 0xFF000000
            )
