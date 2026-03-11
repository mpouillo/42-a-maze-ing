from src.scenes import BaseScene
from src.views.renderers import BaseRenderer


class MenuScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.bg_step = 0
        self.view = BaseRenderer(self.app, self.model)
        self.draw_bg()
        self.setup_ui()
        self.draw_title()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["demo", "Demo", self._cmd_start_display],
            ["play", "Play", self._cmd_start_game]
        ]

        btn_width = self.view.ui_style.get("btn_width", 0)
        btn_height = self.view.ui_style.get("btn_height", 0)
        btn_spacing = ((self.app.window_width - (len(btn_data) * btn_width))
                       // (len(btn_data) + 1))

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0], b[1], (i + 1) * btn_spacing + (i * btn_width),
                (self.app.window_height - btn_height) // 10 * 6, 9999,
                btn_width, btn_height, b[2]
            )

        self.view.add_button(
            "settings", "Settings",
            self.view.pad_w,
            self.app.window_height - (self.view.pad_h + btn_height) // 2,
            9999, btn_width, btn_height, self._cmd_open_settings
        )

    def draw_bg(self):
        canvas = self.view.layers.get("bg")
        height = self.app.window_height
        if self.bg_step == 2 * height:
            self.bg_step = 0
        progress = (self.bg_step / height) % 2.0

        for y in range(height):
            offset_y = y / height
            rmix = (offset_y + progress) % 2.0
            smix = 1.0 - abs(rmix - 1.0)
            color = self.view.get_gradient_color(0xffffbe0b, 0xffff006e, smix)
            canvas.fill_rect(0, y, canvas.width, 1, color)

    def draw_title(self):
        canvas = self.view.layers.get("popup")
        text = "A-Maze-ing"
        scale = 10
        text_w = (len(text) + 1) * scale * self.view.font_width

        offset = 4
        self.view.draw_text(
            canvas,
            (self.app.window_width - text_w) // 2 + offset,
            self.app.window_height // 10 * 4 + offset,
            text, 0xFF7F7F7F, 10
        )

        self.view.draw_text(
            canvas,
            (self.app.window_width - text_w) // 2,
            self.app.window_height // 10 * 4, text, 0xFFFFFFFF, 10
        )

    def _cmd_start_display(self):
        from src.scenes import DisplayScene
        self.view.clear_layers()
        self.view.clear_buttons()
        try:
            self.app.current_scene = DisplayScene(self.app)
        except Exception as e:
            print(e)
            self.app.current_scene = MenuScene(self.app)

    def _cmd_start_game(self):
        from src.scenes import GameScene
        self.view.clear_layers()
        self.view.clear_buttons()
        try:
            self.app.current_scene = GameScene(self.app)
        except Exception as e:
            print(e)
            self.app.current_scene = MenuScene(self.app)

    def _cmd_open_settings(self):
        from src.scenes import SettingsScene
        self.view.clear_layers()
        self.view.clear_buttons()
        self.app.current_scene = SettingsScene(self.app)

    def update(self):
        self.draw_bg()
        self.bg_step += 10
        super().update()

    def render(self):
        super().render()
