import os
import sys
import time
from mlx import Mlx
from src.scenes import MenuScene
from typing import Any


class Application:
    """
    Instantiate an application window.

    Keyword arguments:
    config_file -- local filepath for configuration file
    """

    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.window_width: int = 1200
        self.window_height: int = 900

        self.frame_time: float = 1 / 60
        self.last_frame: float = 0

        self.keypresses: set[int | None] = set()
        self.mouseclicks: set[int | None] = set()
        self.key_autorepeat: bool = True
        self.mouse_autorepeat: bool = False

        self.colors: dict[str, int] = {
            "cell": 0xFFF9AC53,
            "character": 0xFF00FFFF,
            "entry": 0xFF00FF00,
            "exit": 0xFFFF0000,
            "path_1": 0xFF153CB4,
            "path_2": 0xFF300350,
            "walls": 0xFFE93479,
            "step": 0xFFF62E97,
            "bg_1": 0xFFF62E97,
            "bg_2": 0xFF94167F,
        }

        self.mlx: Any = Mlx()
        self.mlx_ptr: int = self.mlx.mlx_init()
        self.win_ptr: int = self.mlx.mlx_new_window(
            self.mlx_ptr, self.window_width, self.window_height, "A-Maze-ing"
        )

        self.current_scene: Any = MenuScene(self)

    def run(self) -> None:
        """Start Mlx hooks"""
        self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
        self.mlx.mlx_hook(self.win_ptr, 2, 1 << 0, self.handle_keydown, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 1 << 1, self.handle_keyup, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_window, None)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.handle_mouse, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update_window, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def handle_keydown(self, keycode: int, param: Any) -> None:
        """Add keycode to keypresses set"""
        self.keypresses.add(keycode)

    def handle_keyup(self, keycode: int, param: Any) -> None:
        """Remove keycode from keypress set"""
        if keycode in self.keypresses:
            self.keypresses.remove(keycode)

    def key_actions(self) -> None:
        """Execute actions if matching keypress detected"""
        if 65307 in self.keypresses:  # Escape
            self.close_window()

    def get_mouse_pos(self) -> tuple[int, int]:
        """Return current mouse position as tuple"""
        _, mouse_x, mouse_y = self.mlx.mlx_mouse_get_pos(self.win_ptr)
        return (mouse_x, mouse_y)

    def handle_mouse(self, click: int, x: int, y: int, param: Any) -> None:
        """On click, check for hovered button and execute action"""
        if click != 1:
            return

        for button in self.current_scene.view.buttons.values():
            if button.is_hovered(x, y) and button.enabled:
                if button.action:
                    button.action()
                    return

    def close_window(self, param: Any = None) -> None:
        """Kill Mlx hooks and exit program"""
        self.mlx.mlx_do_key_autorepeaton(self.mlx_ptr)
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_release(self.mlx_ptr)
        print("Exiting...")
        sys.stdout.flush()
        os._exit(0)

    @staticmethod
    def validate_config() -> None:
        """Raise ValueError in case of config error"""
        REQ_KEYS: list[str] = [
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        ]

        for key in REQ_KEYS:
            if key not in os.environ:
                raise ValueError(f"Missing key in config file: {key}")

        # Getting logo data to check endpoints position
        logo_data: list[str] | None = None
        try:
            with open("src/models/maze/logo.txt", "r") as f:
                logo_data = [
                    line for line in f.read().splitlines() if line.strip()
                ]
        except Exception:
            raise ValueError(
                "Error reading logo data." "Do you have permissions?"
            )
        if logo_data:
            logo_h: int = len(logo_data)
            logo_w: int = len(logo_data[0])
        else:
            raise ValueError("No logo data found")

        width_val: str | None = os.environ.get("WIDTH")
        if width_val in ["None", None]:
            raise ValueError("Width cannot be None")
        if not width_val or not width_val.isdigit():
            raise ValueError("Width must be a valid positive integer")
        width: int = int(width_val)
        if width < 1:
            raise ValueError(f"Width below minimum of 1 ({width})")
        if width < logo_w:
            raise ValueError(
                "Width cannot be smaller than " f"logo width ({logo_w})"
            )

        height_val: str | None = os.environ.get("HEIGHT")
        if height_val in ["None", None]:
            raise ValueError("Height cannot be None")
        if not height_val or not height_val.isdigit():
            raise ValueError("Height must be a valid positive integer")
        height: int = int(height_val)
        if height < 1:
            raise ValueError(f"Height below minimum of 1 ({height})")
        if height < logo_h:
            raise ValueError(
                "Height cannot be smaller than " f"logo's ({logo_h})"
            )

        off_x: int = (width - logo_w) // 2
        off_y: int = (height - logo_h) // 2

        entry_val: str | None = os.environ.get("ENTRY")
        if not entry_val:
            raise ValueError("Entry cannot be None")
        if "," not in entry_val:
            raise ValueError("Entry coordinates must be separated by a ','")
        entry_val_y, entry_val_x = entry_val.split(",", 1)
        if not entry_val_x.isdigit() or not entry_val_y.isdigit():
            raise ValueError("Entry must be 2 valid positive integers")
        entry_y, entry_x = int(entry_val_y), int(entry_val_x)
        if not 0 <= entry_x < width or not 0 <= entry_y < height:
            raise ValueError("Entry coordinates must fit within the maze")
        if (
            off_x <= entry_x < off_x + logo_w
            and off_y <= entry_y < off_y + logo_h
        ):
            if logo_data[entry_y - off_y][entry_x - off_x] == "1":
                raise ValueError("Entry cannot overlap with logo")

        exit_val: str | None = os.environ.get("EXIT")
        if not exit_val:
            raise ValueError("Exit cannot be None")
        if "," not in exit_val:
            raise ValueError("Exit coordinates must be separated by a ','")
        exit_val_y, exit_val_x = exit_val.split(",", 1)
        if not exit_val_x.isdigit() or not exit_val_y.isdigit():
            raise ValueError("Exit must be 2 valid positive integers")
        exit_y, exit_x = int(exit_val_y), int(exit_val_x)
        if not 0 <= exit_x < width or not 0 <= exit_y < height:
            raise ValueError("Exit coordinates must fit within the maze")
        if (
            off_x <= exit_x < off_x + logo_w
            and off_y <= exit_y < off_y + logo_h
        ):
            if logo_data[exit_y - off_y][exit_x - off_x] == "1":
                raise ValueError("Exit cannot overlap with logo")

        if (entry_y, entry_x) == (exit_y, exit_x):
            raise ValueError("Entry and Exit cannot overlap")

        perfect: str | None = os.environ.get("PERFECT")
        if not perfect:
            raise ValueError("Perfect state cannot be None")
        if perfect.lower() not in ["true", "false", "0", "1"]:
            raise ValueError("Perfect state should be either True or False")

        hex_val: str | None = os.environ.get("HEX")
        if hex_val and hex_val.lower() not in ["true", "false", "0", "1"]:
            raise ValueError("Hex state should be either True or False")

        seed: str | None = os.environ.get("SEED")
        if seed and seed.isdigit():
            if int(seed) < 0:
                raise ValueError(f"Seed below minimum of 0 ({seed})")
        elif seed:
            if seed.lower() != "random":
                raise ValueError(
                    "Seed should be None, 'Random', or a valid integer"
                )

    def update_window(self, param: Any) -> None:
        """Execute scene updates and rendering functions"""
        self.key_actions()

        cur_frame: float = time.time()
        if cur_frame - self.last_frame >= self.frame_time:
            self.last_frame = cur_frame
            self.current_scene.update()
            self.current_scene.render()
