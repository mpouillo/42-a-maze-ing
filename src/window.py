from src.mlx import Mlx
from src.algo import generate_maze
import os
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
        self.b1_color = 0xFFFF0000
        self.b2_color = 0xFF00FF00
        self.create_button("reset", (width - self.b1_width) // 2, 20,
                           self.b1_width, self.b1_height, self.b1_color,
                           "Regenerate Maze", 0xFFFFFFFF)
        self.create_button("solve", (width - self.b1_width) // 2, 100,
                           self.b2_width, self.b2_height, self.b2_color,
                           "Solve Maze", 0xFFFFFFFF)

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

    def handle_mouse(self, click, x, y, param) -> None:
        if click == 1:
            button = self.button_clicked(x, y)
            if button and button.name == "reset":
                generate_maze(self.maze_file)
                self.display.clear_layers("path", "maze")
                self.display.set_maze_data(
                    self.mlx, self.mlx_ptr, self.maze_file
                )
                self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
                self.display.run_maze_display()
            if button and button.name == "solve":
                path_canvas = self.display.layers.get("path")["canvas"]
                self.path_gen = self.display.draw_valid_path(path_canvas)
                self.display.solving = True
                if "faster" not in self.buttons.keys():
                    self.create_button(
                        "faster", (self.width - self.b1_width)
                        // 2 + self.b1_width + 20,
                        100, self.b2_width, self.b2_height, self.b2_color,
                        "Faster!!", 0xFFFFFFFF)
                if "slower" not in self.buttons.keys():
                    self.create_button(
                        "slower", (self.width - self.b1_width)
                        // 2 - self.b1_width - 20,
                        100, self.b2_width, self.b2_height, self.b1_color,
                        "Slower!!", 0xFFFFFFFF)
            if button and button.name == "faster":
                self.display.update_interval = (
                    self.display.update_interval * 0.5
                )
            if button and button.name == "slower":
                self.display.update_interval = (
                    self.display.update_interval * 1.5
                )

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
        for button in self.buttons.values():
            if (
                x > button.pos_x
                and x < button.pos_x + button.width
                and y > button.pos_y
                and y < button.pos_y + button.height
            ):
                return (button)
        return None
