from src.scenes import BaseScene
from src.views.renderers import BaseRenderer


class MenuScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.view = BaseRenderer(self.app, self.model)
        self.draw_bg()
        self.setup_ui()
        self.draw_logo()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["display", "Display", self._cmd_start_display],
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

    def draw_bg(self):
        canvas = self.view.add_layer("bg", 0, 0, -1,
                                     self.app.window_width,
                                     self.app.window_height)
        for row in range(self.app.window_height):
            mix = row / self.app.window_height
            color = self.view.get_gradient_color(
                0xFFFF00FF, 0xFFF7931E, mix
            )
            canvas.fill_rect(0, row, canvas.width, 1, color)

    def draw_logo(self):
        canvas = self.view.add_layer("logo", 0, 0, 999,
                                     self.app.window_width,
                                     self.app.window_height)
        text = "A-Maze-ing"
        scale = 10
        text_w = (len(text) + 1) * scale * self.view.font_width

        offset = 4
        self.view.draw_text(
            canvas,
            (self.app.window_width - text_w) // 2 + offset,
            self.app.window_height // 10 * 4 + offset,
            "A-Maze-ing", 0xFF7F7F7F, 10
        )

        self.view.draw_text(
            canvas,
            (self.app.window_width - text_w) // 2,
            self.app.window_height // 10 * 4, "A-Maze-ing", 0xFFFFFFFF, 10
        )

    def _cmd_start_display(self):
        from src.scenes import DisplayScene
        self.view.delete_layer("bg")
        self.view.delete_layer("logo")
        self.view.clear_buttons()
        self.app.current_scene = DisplayScene(self.app)

    def _cmd_start_game(self):
        from src.scenes import GameScene
        self.view.delete_layer("bg")
        self.view.delete_layer("logo")
        self.view.clear_buttons()
        self.app.current_scene = GameScene(self.app)

    def update(self):
        super().update()

    def render(self):
        self.view.draw_ui()
        self.view.refresh_layers()
