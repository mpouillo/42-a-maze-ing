from src.models.maze import MazeGenerator
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer, HexRenderer
from typing import Any, Callable, TypeAlias

BtnData: TypeAlias = list[tuple[str, str, Callable[[], None]]]


class GameScene(BaseScene):
    def __init__(self, app: Any) -> None:
        super().__init__(app)

        self.model: Any = MazeGenerator()
        self.view: Any = None

        if self.model.config.is_hex is True:
            self.view = HexRenderer(self.app, self.model)
        else:
            self.view = SquareRenderer(self.app, self.model)

        self.pos_x: int = self.model.config.entry[1]
        self.pos_y: int = self.model.config.entry[0]
        self.help: bool = False

        self.setup_ui()
        self.view.add_layer(
            "char",
            self.view.offset_x,
            self.view.offset_y,
            4,
            self.view.maze_w,
            self.view.maze_h,
        )
        self.model.generate_new_maze()
        self.view.draw_maze()
        self.view.draw_endpoints()

    def setup_ui(self) -> None:
        """Create buttons with default values"""
        self.view.clear_buttons()

        btn_data: BtnData = [
            ("reset", "Reset", self.reset_game),
            ("help", "Help OFF", self.toggle_help),
        ]

        btn_width: int = min(
            self.view.ui_style.get("btn_width", 0),
            round(self.app.window_width // len(btn_data) * 0.8),
        )
        btn_height: int = self.view.ui_style.get("btn_height", 0)
        btn_spacing: int = (
            self.app.window_width - (len(btn_data) * btn_width)
        ) // (len(btn_data) + 1)

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0],
                b[1],
                (i + 1) * btn_spacing + (i * btn_width),
                (self.view.pad_h - btn_height) // 2,
                9999,
                btn_width,
                btn_height,
                b[2],
            )

        self.view.add_button(
            "menu",
            "Menu",
            self.app.window_width - (self.view.pad_w + btn_width),
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999,
            btn_width,
            btn_height,
            self._cmd_open_menu,
        )

    def toggle_help(self) -> None:
        """Toggle visibility for shortest path to exit"""
        if self.help:
            self.view.buttons.get("help").label = "Help OFF"
            self.help = False
        else:
            self.view.buttons.get("help").label = "Help ON"
            self.help = True

    def reset_game(self) -> None:
        """Move character back to start"""
        self.pos_x = self.model.config.entry[1]
        self.pos_y = self.model.config.entry[0]
        self.view.refresh_layers()

    def draw_character(self) -> None:
        """Render character at current position"""
        color: int = self.app.colors.get("character")
        canvas: Any = self.view.layers.get("char")
        canvas.clear()
        self.view.draw_cell_center(canvas, self.pos_x, self.pos_y, color)

    def end_game(self) -> None:
        """Display 'YOU WIN' screen and restart game"""
        import time

        canvas: Any = self.view.layers.get("popup")
        canvas.clear()
        font_scale: int = max(
            1, min(self.app.window_height, self.app.window_width) // 100
        )
        text: str = "You win!"
        text_w: int = (len(text) * (self.view.font_width + 1) - 1) * font_scale
        text_h: int = self.view.font_height * font_scale
        text_x: int = (self.app.window_width - text_w) // 2
        text_y: int = (self.app.window_height - text_h) // 2

        # Background dim
        canvas.fill_rect(
            0, 0, self.app.window_width, self.app.window_height, 0x7F000000
        )
        # Box background
        canvas.fill_rect(
            text_x - 30,
            text_y - 30,
            text_w + 80,
            text_h + 80,
            self.app.colors.get("bg_2"),
        )
        # Box foreground
        canvas.fill_rect(
            text_x - 40,
            text_y - 40,
            text_w + 80,
            text_h + 80,
            self.app.colors.get("bg_1"),
        )
        # Text
        self.view.draw_text(
            canvas, text_x, text_y, text, 0xFFFFFFFF, font_scale
        )

        self.view.refresh_layers()
        self.app.mlx.mlx_do_sync(self.app.mlx_ptr)

        time.sleep(2)

        canvas.clear()
        self.model.generate_new_maze()
        self.view.draw_maze()
        if self.help:
            self.toggle_help()
        self.reset_game()

    def update(self) -> None:
        """Update maze display depending on current values"""
        KEY_LEFT: int = 65361
        KEY_UP: int = 65362
        KEY_RIGHT: int = 65363
        KEY_DOWN: int = 65364

        is_even: int = self.pos_y % 2 == 0
        keys: set[int | None] = self.app.keypresses
        cur_cell: int = self.model.maze[self.pos_y][self.pos_x]
        pressed_keys: set[int] = set()

        if not self.model.config.is_hex:
            if KEY_LEFT in keys and not cur_cell & 8:
                self.pos_x -= 1
                pressed_keys.add(KEY_LEFT)
            elif KEY_UP in keys and not cur_cell & 1:
                self.pos_y -= 1
                pressed_keys.add(KEY_UP)
            elif KEY_DOWN in keys and not cur_cell & 4:
                self.pos_y += 1
                pressed_keys.add(KEY_DOWN)
            elif KEY_RIGHT in keys and not cur_cell & 2:
                self.pos_x += 1
                pressed_keys.add(KEY_RIGHT)
        else:
            if KEY_LEFT in keys:
                if KEY_UP in keys and not cur_cell & 32:
                    self.pos_y -= 1
                    if is_even:
                        self.pos_x -= 1
                    pressed_keys.add(KEY_LEFT)
                    pressed_keys.add(KEY_UP)
                elif KEY_DOWN in keys and not cur_cell & 8:
                    self.pos_y += 1
                    if is_even:
                        self.pos_x -= 1
                    pressed_keys.add(KEY_LEFT)
                    pressed_keys.add(KEY_DOWN)
                elif not cur_cell & 16:
                    self.pos_x -= 1
                    pressed_keys.add(KEY_LEFT)
            elif KEY_RIGHT in keys:
                if KEY_UP in keys and not cur_cell & 1:
                    self.pos_y -= 1
                    if not is_even:
                        self.pos_x += 1
                    pressed_keys.add(KEY_RIGHT)
                    pressed_keys.add(KEY_UP)
                elif KEY_DOWN in keys and not cur_cell & 4:
                    self.pos_y += 1
                    if not is_even:
                        self.pos_x += 1
                    pressed_keys.add(KEY_RIGHT)
                    pressed_keys.add(KEY_DOWN)
                elif not cur_cell & 2:
                    self.pos_x += 1
                    pressed_keys.add(KEY_RIGHT)

        # Exit reached
        if (self.pos_y, self.pos_x) == self.model.config.exit:
            self.end_game()
            return

        # Precise movements
        if 65507 in self.app.keypresses:
            self.app.keypresses -= pressed_keys

        if 108 in self.app.keypresses:
            self.end_game()

        super().update()

    def render(self) -> None:
        """Update current frame"""
        self.draw_character()
        if self.help is True:
            cur = (self.pos_y, self.pos_x)
            for path in self.model.valid_paths:
                if cur in path:
                    self.view.draw_path(path)
                    break
        else:
            self.view.clear_layers("path")

        super().render()
