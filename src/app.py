import os
import time
from mlx import Mlx
from src.scenes import MenuScene
from typing import Any


class Application:
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.window_width = 1000
        self.window_height = 1000

        self.frame_time = 1/60
        self.last_frame = 0

        self.keypresses = set()
        self.mouseclicks = set()
        self.key_autorepeat = True
        self.mouse_autorepeat = False
        self.mouse_pos = (None, None)

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.window_width, self.window_height, "A-Maze-ing"
        )

        self.current_scene = MenuScene(self)

    def run(self):
        self.mlx.mlx_hook(self.win_ptr, 2, 1 << 0, self.handle_keydown, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 1 << 1, self.handle_keyup, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_window, None)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.handle_mouse, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update_window, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def handle_keydown(self, keycode, param) -> None:
        self.keypresses.add(keycode)

    def handle_keyup(self, keycode, param) -> None:
        if keycode in self.keypresses:
            self.keypresses.remove(keycode)

    def key_actions(self) -> None:
        if 65307 in self.keypresses:    # Escape
            self.close_window()

    def get_mouse_pos(self) -> tuple[int, int]:
        _, mouse_x, mouse_y = self.mlx.mlx_mouse_get_pos(self.win_ptr)
        return (mouse_x, mouse_y)

    def handle_mouse(self, click, x, y, param) -> None:
        if click != 1:
            return

        for button in self.current_scene.view.buttons.values():
            if button.is_hovered(x, y):
                if button.action:
                    button.action()
                    return

    def close_window(self, param: Any = None) -> None:
        self.mlx.mlx_release(self.mlx_ptr)
        print("Exiting...")
        os._exit(0)

    def update_window(self, param):
        self.key_actions()

        cur_frame = time.time()
        if (cur_frame - self.last_frame >= self.frame_time):
            self.last_frame = cur_frame
            self.current_scene.update()
            self.current_scene.render()
