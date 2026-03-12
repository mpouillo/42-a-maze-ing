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

        self.colors = {
            "cell": 0xfff9ac53,
            "character": 0xff0000ff,
            "entry": 0xFF00FF00,
            "exit": 0xFFFF0000,
            "path_1": 0xff153cb4,
            "path_2": 0xff300350,
            "walls": 0xffe93479,
            "step": 0xfff62e97,
            "bg_1": 0xff94167f,
            "bg_2": 0xfff62e97
        }

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
                raise ValueError(f"Missing key in config file: {key}")

        # Getting logo data to check endpoints position
        logo_data = None
        try:
            with open("src/models/maze/logo.txt", "r") as f:
                logo_data = [line for line in f.read().splitlines()
                             if line.strip()]
        except Exception:
            raise ValueError("Error reading logo data."
                             "Do you have permissions?")
        if logo_data:
            logo_h = len(logo_data)
            logo_w = len(logo_data[0])
        else:
            raise ValueError("No logo data found")

        width = os.environ.get("WIDTH")
        if width in ["None", None]:
            raise ValueError("Width cannot be None")
        if not width.isdigit():
            raise ValueError("Width must be a valid positive integer")
        width = int(width)
        if width < 1:
            raise ValueError(f"Width below minimum of 1 ({width})")
        if width < logo_w:
            raise ValueError("Width cannot be smaller than "
                             f"logo width ({logo_w})")

        height = os.environ.get("HEIGHT")
        if height in ["None", None]:
            raise ValueError("Height cannot be None")
        if not height.isdigit():
            raise ValueError("Height must be a valid positive integer")
        height = int(height)
        if height < 1:
            raise ValueError(f"Height below minimum of 1 ({height})")
        if height < logo_h:
            raise ValueError("Height cannot be smaller than "
                             f"logo's ({logo_h})")

        off_x = (width - logo_w) // 2
        off_y = (height - logo_h) // 2

        entry_val = os.environ.get("ENTRY")
        if not entry_val:
            raise ValueError("Entry cannot be None")
        if "," not in entry_val:
            raise ValueError("Entry coordinates must be separated by a ','")
        entry_y, entry_x = entry_val.split(",", 1)
        if not entry_x.isdigit() or not entry_y.isdigit():
            raise ValueError("Entry must be 2 valid positive integers")
        entry_y, entry_x = int(entry_y), int(entry_x)
        if not 0 <= entry_x < width or not 0 <= entry_y < height:
            raise ValueError("Entry coordinates must fit within the maze")
        if (
            off_x <= entry_x < off_x + logo_w
            and off_y <= entry_y < off_y + logo_h
        ):
            if logo_data[entry_y - off_y][entry_x - off_x] == '1':
                raise ValueError("Entry cannot overlap with logo")

        exit_val = os.environ.get("EXIT")
        if not exit_val:
            raise ValueError("Exit cannot be None")
        if "," not in exit_val:
            raise ValueError("Exit coordinates must be separated by a ','")
        exit_y, exit_x = exit_val.split(",", 1)
        if not exit_x.isdigit() or not exit_y.isdigit():
            raise ValueError("Exit must be 2 valid positive integers")
        exit_y, exit_x = int(exit_y), int(exit_x)
        if not 0 <= exit_x < width or not 0 <= exit_y < height:
            raise ValueError("Exit coordinates must fit within the maze")
        if (
            off_x <= exit_x < off_x + logo_w
            and off_y <= exit_y < off_y + logo_h
        ):
            if logo_data[exit_y - off_y][exit_x - off_x] == '1':
                raise ValueError("Exit cannot overlap with logo")

        if (entry_y, entry_x) == (exit_y, exit_x):
            raise ValueError("Entry and Exit cannot overlap")

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
