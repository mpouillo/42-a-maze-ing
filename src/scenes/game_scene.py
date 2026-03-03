from src.models import MazeModel
from src.scenes import BaseScene
from src.views.renderers import SquareRenderer


class GameScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.model = MazeModel(self.app.config_file)
        self.view = SquareRenderer(self.app, self.model)

        self.pos_x = 0
        self.pos_y = 0

        self.setup_ui()
        self.view.layers.update({
            "character": self.view.create_canvas(
                self.view.offset_x, self.view.offset_y,
                0, self.view.maze_w, self.view.maze_h
            )
        })

    def setup_ui(self):
        self.view.clear_buttons()

        btn_data = [
            ["reset", "Reset", self.reset_game]
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
            9999, btn_width, btn_height, self.open_menu
        )

    def reset_game(self):
        self.pos_x = 0
        self.pos_y = 0
        self.view.refresh()

    def render_char(self):
        node = self.view.node_size
        wall = self.view.wall_size
        color = self.view.colors.get("character")
        canvas = self.view.layers.get("character")

        canvas.clear()
        canvas.fill_rect(self.pos_x * node + wall, self.pos_y * node + wall,
                         node - wall, node - wall, color)

    def end_game(self):
        import time
        canvas = self.view.create_canvas(0, 0, 9999, self.app.window_width,
                                         self.app.window_height)
        self.view.layers.update({"popup": canvas})
        canvas.fill_rect(0, 0, self.app.window_width,
                         self.app.window_height, 0xFF000000)

        font_scale = max(1, min(
            self.app.window_height, self.app.window_width) // 100
        )
        text = "You won!"
        text_w = (len(text) * (self.view.font_width + 1) - 1) * font_scale
        text_h = self.view.font_height * font_scale
        text_x = (self.app.window_width - text_w) // 2
        text_y = (self.app.window_height - text_h) // 2

        self.view.draw_text(canvas, text_x, text_y, text,
                            0xFFFFFFFF, font_scale)

        self.view.refresh()
        self.app.mlx.mlx_do_sync(self.app.mlx_ptr)

        time.sleep(3)

        self.view.layers.pop("popup")
        self.model.maze.maze_gen.height += 1
        self.model.maze.maze_gen.width += 1
        self.reset_game()

    def render(self):
        self.view.render_maze()
        self.view.draw_endpoints()
        self.render_char()
        self.view.render_ui()
        self.view.refresh()

    def update(self) -> None:
        # Move character
        cur_cell = self.model.grid[self.pos_y][self.pos_x]
        if 65361 in self.app.keypresses and not cur_cell & 8:   # Left
            self.pos_x -= 1
        cur_cell = self.model.grid[self.pos_y][self.pos_x]
        if 65362 in self.app.keypresses and not cur_cell & 1:   # Up
            self.pos_y -= 1
        cur_cell = self.model.grid[self.pos_y][self.pos_x]
        if 65364 in self.app.keypresses and not cur_cell & 4:   # Down
            self.pos_y += 1
        cur_cell = self.model.grid[self.pos_y][self.pos_x]
        if 65363 in self.app.keypresses and not cur_cell & 2:   # Right
            self.pos_x += 1

        # Exit reached
        if (self.pos_y, self.pos_x) == self.model.exit:
            self.view.refresh()
            self.end_game()
            return

        # Precise movements
        if 65507 in self.app.keypresses:
            self.app.keypresses.clear()
            self.app.keypresses.add(65507)

        super().update()
