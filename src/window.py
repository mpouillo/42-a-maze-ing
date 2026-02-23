from src.mlx import Mlx
import os


class Window:
    def __init__(self, maze_file: str, config_file: str,
                 width: int, height: int) -> None:
        from src.draw_maze import DrawMaze

        self.keys_pressed = set()

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
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.display.WIN_PTR, 4, 4, 0xFFFFFFFF,
            "Escape: Close"
        )

        # Update Hook
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.handle_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.handle_keyrelease, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def handle_keypress(self, keycode, param) -> None:
        self.keys_pressed.add(keycode)

    def handle_keyrelease(self, keycode, param) -> None:
        if keycode in self.keys_pressed:
            self.keys_pressed.remove(keycode)

    def update(self, param):
        if 65307 in self.keys_pressed:    # Escape
            # self.display.clear_layers()
            # self.mlx.mlx_release(self.mlx_ptr)
            os._exit(0)
