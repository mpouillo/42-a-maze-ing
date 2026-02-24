from src.mlx import Mlx
from src.algo import generate_maze
from functools import partial
import os
import random
import time


class Window:
    def __init__(self, maze_file: str, config_file: str,
                 width: int, height: int) -> None:
        from src.draw_maze import DrawMaze

        self.keys_pressed = set()
        self.buttons = {}

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
        self.display = DrawMaze(
            self.mlx, self.mlx_ptr, self.win_ptr,
            width, height, config_file, maze_file
        )

        bg_canvas = self.display.add_layer(0, 0, -1, width, height, "bg")
        bg_canvas.fill_rect(0, 0, width, height, 0xFF000000)

        self.display.run_maze_display()

        self.b1_width = 300
        self.b1_height = 60
        self.b2_width = self.b1_width
        self.b2_height = self.b1_height
        self.b1_color = 0xFFFF007F
        self.b2_color = 0xFF00FF7F
        self.create_button("reset_maze", (width - self.b1_width) // 2, 20,
                           self.b1_width, self.b1_height, self.b1_color,
                           "Regenerate Maze", 0xFFFFFFFF)
        self.create_button("solve_maze", (width - self.b1_width) // 2, 100,
                           self.b2_width, self.b2_height, self.b2_color,
                           "Solve Maze", 0xFFFFFFFF)
        self.create_button("walls_bigger", 20, 20,
                           self.b2_width, self.b2_height, 0xFF007FFF,
                           "Bigger walls", 0xFFFFFFFF)
        self.create_button("walls_smaller", 20, 100,
                           self.b2_width, self.b2_height, 0xFF007FFF,
                           "Smaller walls", 0xFFFFFFFF)
        self.create_button("maze_colors", width - self.b2_width - 20, 20,
                           self.b2_width, self.b2_height, 0xFF007FFF,
                           "Random colors", 0xFFFFFFFF)

        # Update Hook
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.handle_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.handle_keyrelease, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_window, None)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.handle_mouse, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def close_window(self, param=None):
        self.display.clear_layers()
        self.mlx.mlx_release(self.mlx_ptr)
        os._exit(0)

    def handle_keypress(self, keycode, param) -> None:
        self.keys_pressed.add(keycode)
        if 65307 in self.keys_pressed:    # Escape
            self.close_window()

    def handle_keyrelease(self, keycode, param) -> None:
        if keycode in self.keys_pressed:
            self.keys_pressed.remove(keycode)

    def _cmd_reset_maze(self):
        generate_maze(self.maze_file)
        self.display.clear_layers("path", "maze", "faster", "slower")
        self.display.set_maze_data(self.mlx, self.mlx_ptr, self.maze_file)
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.display.run_maze_display()

    def _cmd_solve_maze(self):
        path_canvas = self.display.layers.get("path")["canvas"]
        self.path_gen = self.display.draw_valid_path(path_canvas)
        self.display.solving = True
        if "solve_faster" not in self.display.layers.keys():
            self.create_button(
                "solve_faster", (self.width - self.b1_width)
                // 2 + self.b1_width + 20, 100, self.b2_width, self.b2_height,
                0xFFFF7F7F, "Faster!!", 0xFFFFFFFF
            )
        if "solve_slower" not in self.display.layers.keys():
            self.create_button(
                "solve_slower", (self.width - self.b1_width)
                // 2 - self.b1_width - 20, 100, self.b2_width, self.b2_height,
                0xFF7F7FFF, "Slower!!", 0xFFFFFFFF
            )

    def _cmd_resize_walls(self, delta) -> None:
        if delta > 0:
            self.display.LINE_WEIGHT = min(
                self.display.NODE_SIZE // 2,
                self.display.LINE_WEIGHT + 1
            )
        else:
            self.display.LINE_WEIGHT = max(1, self.display.LINE_WEIGHT - 1)
        self.display.set_maze_data(self.mlx, self.mlx_ptr, self.maze_file)
        self.display.run_maze_display()

    def _cmd_random_colors(self):
        self.display.set_colors(
            *(random.randrange(0xFF0000FF, 0xFFFFFFFF) for _ in range(6))
        )
        self.display.run_maze_display()
        if "reset_colors" not in self.display.layers.keys():
            self.create_button("reset_colors", self.width - self.b2_width - 20,
                               100, self.b2_width, self.b2_height, 0xFFFF7F00,
                               "Reset colors", 0xFFFFFFFF)

    def _cmd_reset_colors(self):
        self.display.set_colors()
        self.display.clear_layers("reset_colors")
        self.display.run_maze_display()

    def _cmd_adjust_speed(self, factor):
        if factor < 1:
            self.display.update_interval = max(
                0.01, self.display.update_interval * factor
            )
        else:
            self.display.update_interval = min(
                2.0, self.display.update_interval * factor
            )

    def handle_mouse(self, click, x, y, param) -> None:
        if click != 1:
            return

        button = self.button_clicked(x, y)
        if not button:
            return

        commands = {
            "maze_colors": self._cmd_random_colors,
            "reset_colors": self._cmd_reset_colors,
            "reset_maze": self._cmd_reset_maze,
            "solve_faster": partial(self._cmd_adjust_speed, 0.5),
            "solve_slower": partial(self._cmd_adjust_speed, 1.5),
            "solve_maze": self._cmd_solve_maze,
            "walls_bigger": partial(self._cmd_resize_walls, 1),
            "walls_smaller": partial(self._cmd_resize_walls, -1),
        }

        action = commands.get(button.name)
        if action:
            action()

    def update(self, param):
        if self.display.solving:
            current_time = time.time()
            if (
                current_time - self.display.last_path_update
                >= self.display.update_interval
            ):
                try:
                    next(self.display.path_gen)
                    self.display.last_path_update = current_time
                except (StopIteration, AttributeError):
                    self.display.solving = False
        self.display.draw_layers_to_window()

    def create_button(self, name, x, y, width, height, bg_color,
                      text, text_color) -> None:
        canvas = self.display.add_layer(x, y, 9999, width, height, name)
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

    def button_clicked(self, x, y) -> dict:
        for button in reversed(list(self.buttons.values())):
            if (
                x > button.pos_x
                and x < button.pos_x + button.width
                and y > button.pos_y
                and y < button.pos_y + button.height
            ):
                return (button)
        return None
