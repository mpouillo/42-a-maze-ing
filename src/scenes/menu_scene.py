from src.scenes import BaseScene
from src.views.renderers import BaseRenderer


class MenuScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.view = BaseRenderer(self.app, self.model)
        self.setup_ui()

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["display", "Display", self.start_display],
            ["play", "Play", self.start_game]
        ]

        btn_width = self.view.ui_style.get("btn_width", 0)
        btn_height = self.view.ui_style.get("btn_height", 0)
        btn_spacing = ((self.app.window_width - (len(btn_data) * btn_width))
                       // (len(btn_data) + 1))

        for i, b in enumerate(btn_data):
            self.view.add_button(
                b[0], b[1], (i + 1) * btn_spacing + (i * btn_width),
                (self.app.window_height - btn_height) // 2, 9999,
                btn_width, btn_height, b[2]
            )

    def start_display(self):
        from src.scenes import DisplayScene
        self.view.clear_buttons()
        self.app.current_scene = DisplayScene(self.app)

    def start_game(self):
        from src.scenes import GameScene
        self.view.clear_buttons()
        self.app.current_scene = GameScene(self.app)

    def update(self):
        self.view.render_ui()
        super().update()

    def render(self):
        self.view.refresh()
