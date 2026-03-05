from src.models.maze import MazeModel
from src.views.renderers import BaseRenderer


class SquareRenderer(BaseRenderer):
    def __init__(self, app, model: MazeModel) -> None:
        super().__init__(app, model)

        self.wall_size = 2
        self.compute_scales()

        self.layers = {
            "maze": self.create_canvas(self.offset_x, self.offset_y,
                                       0, self.maze_w, self.maze_h),
            "path": self.create_canvas(self.offset_x, self.offset_y,
                                       1, self.maze_w, self.maze_h),
            "ui": self.create_canvas(0, 0, 99, self.app.window_width,
                                     self.app.window_height)
        }

        self.colors = {
            "cell": 0xFF0000FF,
            "character": 0xFF00FFFF,
            "entry": 0xFF00FF00,
            "exit": 0xFFFF0000,
            "path_1": 0xFF00FF00,
            "path_2": 0xFFFF0000,
            "walls": 0xFFFFFFFF,
            "gen": 0xFFFF007F
        }

    def compute_scales(self):
        available_w = self.app.window_width - self.pad_w * 2 - self.wall_size
        available_h = self.app.window_height - self.pad_h * 2 - self.wall_size
        cols = self.model.config.width
        rows = self.model.config.height

        self.node_size = min(available_w // cols, available_h // rows)
        self.maze_w = cols * self.node_size + self.wall_size
        self.maze_h = rows * self.node_size + self.wall_size
        self.offset_x = (self.app.window_width - self.maze_w) // 2
        self.offset_y = (self.app.window_height - self.maze_h) // 2

    def draw_maze(self):
        wall_color = self.colors.get("walls")
        cell_color = self.colors.get("cell")

        canvas = self.layers.get("maze")
        canvas.clear()

        for y, row in enumerate(self.model.maze):
            for x, value in enumerate(row):
                self.draw_cell_walls(canvas, wall_color, x, y, value)
                if value == 0xF:
                    self.draw_cell_square(canvas, cell_color, x, y)

    def draw_path(self, path: list, color: int = None):
        color_start = self.colors.get("path_1")
        color_end = self.colors.get("path_2")
        for i, step_data in enumerate(path):
            cell_color = color if color else self.get_gradient_color(
                color_start, color_end, i / max(1, len(path) - 1)
            )
            self.draw_step(step_data, cell_color)

    def draw_step(self, step_data: dict, color):
        canvas = self.layers.get("path")
        maze_entry = self.model.config.entry
        maze_exit = self.model.config.exit

        (y, x), value = step_data
        self.draw_cell_walls(canvas, color, x, y, value ^ 0xF)
        if (y, x) not in [maze_entry, maze_exit]:
            self.draw_cell_square(canvas, color, x, y)

    def draw_endpoints(self):
        canvas = self.layers.get("path")
        self.draw_cell_square(canvas, self.colors.get("entry"),
                              self.model.config.entry[1],
                              self.config.model.entry[0])
        self.draw_cell_square(canvas, self.colors.get("exit"),
                              self.model.config.exit[1],
                              self.model.config.exit[0])

    def draw_cell_walls(self, canvas, color, x, y, value):
        node = self.node_size
        wall = self.wall_size
        x *= node
        y *= node

        if value & 1:
            canvas.fill_rect(x, y, node + wall, wall, color)
        if value & 4:
            canvas.fill_rect(x, y + node, node + wall, wall, color)
        if value & 2:
            canvas.fill_rect(x + node, y, wall, node + wall, color)
        if value & 8:
            canvas.fill_rect(x, y, wall, node + wall, color)

    def draw_cell_square(self, canvas, color, x, y):
        node = self.node_size
        wall = self.wall_size
        x *= node
        y *= node

        canvas.fill_rect(x + wall, y + wall, node - wall, node - wall, color)
