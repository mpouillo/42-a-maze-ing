from src.models.maze import MazeModel
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer, HexRenderer


class GameScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)

        self.model = MazeModel()

        if self.model.config.is_hex is True:
            self.view = HexRenderer(self.app, self.model)
        else:
            self.view = SquareRenderer(self.app, self.model)

        self.pos_x = 0
        self.pos_y = 0
        self.help = False

        self.setup_ui()
        self.view.add_layer("char", self.view.offset_x, self.view.offset_y,
                            4, self.view.maze_w, self.view.maze_h)
        self.model.generate_new_maze()
        self.view.draw_maze()
        self.view.draw_endpoints()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["reset", "Reset", self.reset_game],
            ["help", "Help OFF", self.toggle_help]
        ]

        btn_width = min(self.view.ui_style.get("btn_width", 0),
                        round(self.app.window_width // len(btn_data) * 0.8)
                        )
        btn_height = self.view.ui_style.get("btn_height", 0)
        btn_spacing = ((self.app.window_width - (len(btn_data) * btn_width))
                       // (len(btn_data) + 1))

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0], b[1], (i + 1) * btn_spacing + (i * btn_width),
                (self.view.pad_h - btn_height) // 2, 9999,
                btn_width, btn_height, b[2]
            )

        self.view.add_button(
            "menu", "Menu",
            self.app.window_width - (self.view.pad_w + btn_width),
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999, btn_width, btn_height, self._cmd_open_menu
        )

    def toggle_help(self):
        if self.help:
            self.view.buttons.get("help").label = "Help OFF"
            self.help = False
        else:
            self.view.buttons.get("help").label = "Help ON"
            self.help = True

    def reset_game(self):
        self.pos_x = 0
        self.pos_y = 0
        self.view.refresh_layers()

    def draw_character(self):
        color = self.app.colors.get("character")
        canvas = self.view.layers.get("char")
        canvas.clear()
        self.view.draw_cell_center(canvas, self.pos_x, self.pos_y, color)

    def end_game(self):
        import time
        canvas = self.view.layers.get("popup")
        canvas.clear()
        font_scale = max(1, min(
            self.app.window_height, self.app.window_width) // 100
        )
        text = "You win!"
        text_w = (len(text) * (self.view.font_width + 1) - 1) * font_scale
        text_h = self.view.font_height * font_scale
        text_x = (self.app.window_width - text_w) // 2
        text_y = (self.app.window_height - text_h) // 2

        canvas.fill_rect(0, 0, self.app.window_width, self.app.window_height,
                         0x7F000000)

        canvas.fill_rect(text_x - 30, text_y - 30, text_w + 80, text_h + 80,
                         0xFF754814)

        canvas.fill_rect(text_x - 40, text_y - 40, text_w + 80, text_h + 80,
                         0xFFF7931E)

        self.view.draw_text(canvas, text_x, text_y, text,
                            0xFFFFFFFF, font_scale)

        self.view.refresh_layers()
        self.app.mlx.mlx_do_sync(self.app.mlx_ptr)

        time.sleep(2)

        canvas.clear()
        self.model.generate_new_maze()
        self.view.draw_maze()
        if self.help:
            self.toggle_help()
        self.reset_game()

    def render(self):
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

    def update(self) -> None:
        KEY_LEFT = 65361
        KEY_UP = 65362
        KEY_RIGHT = 65363
        KEY_DOWN = 65364

        is_even = (self.pos_y % 2 == 0)
        keys = self.app.keypresses
        cur_cell = self.model.maze[self.pos_y][self.pos_x]

        if not self.model.config.is_hex:
            if KEY_LEFT in keys and not cur_cell & 8:
                self.pos_x -= 1
            elif KEY_UP in keys and not cur_cell & 1:
                self.pos_y -= 1
            elif KEY_DOWN in keys and not cur_cell & 4:
                self.pos_y += 1
            elif KEY_RIGHT in keys and not cur_cell & 2:
                self.pos_x += 1
        else:
            if KEY_LEFT in keys:
                if KEY_UP in keys and not cur_cell & 32:
                    self.pos_y -= 1
                    if is_even:
                        self.pos_x -= 1
                elif KEY_DOWN in keys and not cur_cell & 8:
                    self.pos_y += 1
                    if is_even:
                        self.pos_x -= 1
                elif not cur_cell & 16:
                    self.pos_x -= 1
            elif KEY_RIGHT in keys:
                if KEY_UP in keys and not cur_cell & 1:
                    self.pos_y -= 1
                    if not is_even:
                        self.pos_x += 1
                elif KEY_DOWN in keys and not cur_cell & 4:
                    self.pos_y += 1
                    if not is_even:
                        self.pos_x += 1
                elif not cur_cell & 2:
                    self.pos_x += 1

        # Exit reached
        if (self.pos_y, self.pos_x) == self.model.config.exit:
            self.end_game()
            return

        # Precise movements
        if 65507 in self.app.keypresses:
            self.app.keypresses.clear()
            self.app.keypresses.add(65507)

        if 108 in self.app.keypresses:
            self.end_game()

        super().update()
