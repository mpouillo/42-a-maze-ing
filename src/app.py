import os
import sys
import time
from mlx import Mlx  # type: ignore
from src.scenes import MenuScene
from typing import Any


class Application:
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.window_width = 1200
        self.window_height = 1200

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
        self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
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
            if button.is_hovered(x, y) and button.enabled:
                if button.action:
                    button.action()
                    return

    def close_window(self, param: Any = None) -> None:
        self.mlx.mlx_do_key_autorepeaton(self.mlx_ptr)
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_release(self.mlx_ptr)
        print("Exiting...")
        sys.stdout.flush()
        os._exit(0)

    @staticmethod
    def validate_config():
        REQ_KEYS = [
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT"
        ]

        for key in REQ_KEYS:
            if key not in os.environ:
                return False

        width = os.environ.get("WIDTH")
        if width in ["None", None]:
            raise ValueError("Width cannot be None")
        if not width.isdigit():
            raise ValueError("Width must be a valid positive integer")
        if int(width) < 1:
            raise ValueError(f"Width below minimum of 1 ({width})")

        height = os.environ.get("HEIGHT")
        if height in ["None", None]:
            raise ValueError("Height cannot be None")
        if not height.isdigit():
            raise ValueError("Height must be a valid positive integer")
        if int(height) < 1:
            raise ValueError(f"Height below minimum of 1 ({height})")

        entry_val = os.environ.get("ENTRY")
        if not entry_val:
            raise ValueError("Entry cannot be None")
        if "," not in entry_val:
            raise ValueError("Entry coordinates must be separated by a ','")
        x, y = entry_val.split(",", 1)
        if not x.isdigit() or not y.isdigit():
            raise ValueError("Entry must be 2 valid positive integers")
        if not 0 <= int(x) < int(width) or not 0 <= int(y) < int(height):
            raise ValueError("Entry coordinates must fit within the maze")

        exit_val = os.environ.get("EXIT")
        if not exit_val:
            raise ValueError("Exit cannot be None")
        if "," not in exit_val:
            raise ValueError("Exit coordinates must be separated by a ','")
        x, y = exit_val.split(",", 1)
        if not x.isdigit() or not y.isdigit():
            raise ValueError("Exit must be 2 valid positive integers")
        if not 0 <= int(x) < int(width) or not 0 <= int(y) < int(height):
            raise ValueError("Exit coordinates must fit within the maze")

        output_file = os.environ.get("OUTPUT_FILE")
        if not output_file:
            raise ValueError("Output file cannot be None")
        if os.path.splitext(output_file)[1] != ".txt":
            raise ValueError("Output file extension must be .txt")

        perfect = os.environ.get("PERFECT")
        if not perfect:
            raise ValueError("Perfect state cannot be None")
        if perfect.lower() not in ["true", "false", "0", "1"]:
            raise ValueError("Perfect state should be either True or False")

        hex_s = os.environ.get("HEX")
        if hex_s and hex_s.lower() not in ["true", "false", "0", "1"]:
            raise ValueError("Hex state should be either True or False")

        seed = os.environ.get("SEED")
        if seed and seed.isdigit():
            if int(seed) < 0:
                raise ValueError(f"Seed below minimum of 0 ({seed})")
        elif seed:
            if seed.lower() != "random":
                raise ValueError(
                    "Seed should be None, 'Random', or a valid integer"
                )

    def update_window(self, param):
        self.key_actions()

        cur_frame = time.time()
        if (cur_frame - self.last_frame >= self.frame_time):
            self.last_frame = cur_frame
            self.current_scene.update()
            self.current_scene.render()
