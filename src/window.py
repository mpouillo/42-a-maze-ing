from src.mlx import Mlx
import os


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

        # Display Output
        self.display = DrawMaze(
            self.mlx, self.mlx_ptr, self.win_ptr,
            width, height, config_file, maze_file
        )
        self.display.run_maze_display()

        self.create_button("Button box", 20, 20, 400, 60, 0xFFFF00FF,
                           "This is a button box", 0xFFFFFFFF)

        # Update Hook
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.handle_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.handle_keyrelease, None)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.handle_mouse, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def handle_keypress(self, keycode, param) -> None:
        self.keys_pressed.add(keycode)

    def handle_keyrelease(self, keycode, param) -> None:
        if keycode in self.keys_pressed:
            self.keys_pressed.remove(keycode)

    def handle_mouse(self, button, x, y, param) -> None:
        if button == 1:
            print(f"left click at {x}, {y}")

    def update(self, param):
        if 65307 in self.keys_pressed:    # Escape
            # self.display.clear_layers()
            # self.mlx.mlx_release(self.mlx_ptr)
            os._exit(0)
        self.display.draw_layers_to_window()

    def create_button(self, name, x, y, width, height, bg_color,
                      text, text_color) -> None:
        layer = self.display.add_layer(x, y, width, height, name)
        outline = width // 50
        layer.fill_rect(0, 0, width, height, bg_color & 0x7F7F7F7F)
        layer.fill_rect(0 + outline // 2, 0 + outline // 2,
                        max(0, width - outline),
                        max(0, height - outline),
                        bg_color)
        x_pos = (width - (len(text)
                 * (layer.font_width + layer.font_scale))) // 2
        y_pos = (height - layer.font_height) // 2
        layer.draw_text(x_pos, y_pos, text, text_color)
        self.buttons.update({name: layer})
        return self.buttons.get(name)
