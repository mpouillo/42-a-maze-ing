from src.models.maze import MazeModel
from src.views.renderers import BaseRenderer


class SquareRenderer(BaseRenderer):
    def __init__(self, app, model: MazeModel) -> None:
        super().__init__(app, model)

        self.wall_size = 4
        self.compute_scales()

        self.layers = {
            "maze": self.create_canvas(self.offset_x, self.offset_y,
                                       0, self.maze_w, self.maze_h),
            "path": self.create_canvas(self.offset_x, self.offset_y,
                                       1, self.maze_w, self.maze_h),
            "ui": self.create_canvas(0, 0, 99, self.app.window_width,
                                     self.app.window_height)
        }

    def compute_scales(self):
        available_w = self.app.window_width - self.pad_w * 2 - self.wall_size
        available_h = self.app.window_height - self.pad_h * 2 - self.wall_size
        cols = self.model.config.width
        rows = self.model.config.height

        self.node_size = min(available_w // cols, available_h // rows)
        if self.node_size <= self.wall_size * 2:
            self.wall_size = max(1, self.node_size // 2)
            self.compute_scales()

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
                self.draw_cell_walls(canvas, x, y, value, True, wall_color)
                if value == 0xF:
                    self.draw_cell_square(canvas, x, y, cell_color)

    def draw_path(self, path: list, color: int = None):
        color_start = self.colors.get("path_1")
        color_end = self.colors.get("path_2")
        canvas = self.layers.get("path")
        canvas.clear()

        for i, (y1, x1) in enumerate(path):
            color = self.get_gradient_color(color_start, color_end,
                                            i / max(1, len(path) - 1))
            self.draw_cell_square(canvas, x1, y1, color)
            if i == 0:
                continue
            (y2, x2) = path[i - 1]
            if y2 < y1:    # North
                wall = 1
            elif y2 > y1:  # South
                wall = 4
            elif x2 < x1:  # West
                wall = 8
            elif x2 > x1:  # East
                wall = 2
            self.draw_cell_walls(canvas, x1, y1, wall, False, color)

    def draw_step(self, step_data: dict, color):
        maze_entry = self.model.config.entry
        maze_exit = self.model.config.exit
        cmd, (y1, x1), (y2, x2) = step_data

        if y2 < y1:    # North
            wall = 1
        elif y2 > y1:  # South
            wall = 4
        elif x2 < x1:  # West
            wall = 8
        elif x2 > x1:  # East
            wall = 2
        else:
            return

        match cmd:
            case 'remove':
                maze_canvas = self.layers.get("maze")
                self.draw_cell_square(maze_canvas, x1, y1)
                self.draw_cell_square(maze_canvas, x2, y2)
                self.draw_cell_walls(maze_canvas, x1, y1, wall, False)
            case 'fill':
                path_canvas = self.layers.get("path")
                if (y1, x1) not in [maze_entry, maze_exit]:
                    self.draw_cell_square(path_canvas, x1, y1, color)
                if (y2, x2) not in [maze_entry, maze_exit]:
                    self.draw_cell_square(path_canvas, x2, y2, color)
                self.draw_cell_walls(path_canvas, x1, y1, wall, False, color)
            case _:
                pass

        if (
            (y1, x1) == self.model.config.entry
            or (y2, x2) == self.model.config.exit
        ):
            self.draw_endpoints()

    def draw_endpoints(self):
        canvas = self.layers.get("path")
        self.draw_cell_square(canvas, self.model.config.entry[1],
                              self.model.config.entry[0],
                              self.colors.get("entry"))
        self.draw_cell_square(canvas, self.model.config.exit[1],
                              self.model.config.exit[0],
                              self.colors.get("exit"))

    def draw_cell_square(self, canvas, x, y, color=0xFF000000):
        node = self.node_size
        wall = self.wall_size
        canvas.fill_rect(x * node + wall, y * node + wall,
                         node - wall, node - wall, color)

    def draw_cell_walls(self, canvas, x, y, value=0,
                        corners=False, color=0xFF000000) -> None:
        node = self.node_size
        wall = self.wall_size
        x *= node
        y *= node

        if corners is True:
            if value & 1:   # Top
                canvas.fill_rect(x, y, node + wall, wall, color)
            if value & 4:   # Bottom
                canvas.fill_rect(x, y + node, node + wall, wall, color)
            if value & 2:   # Right
                canvas.fill_rect(x + node, y, wall, node + wall, color)
            if value & 8:   # Left
                canvas.fill_rect(x, y, wall, node + wall, color)
        else:
            if value & 1:   # Top
                canvas.fill_rect(x + wall, y, node - wall, wall, color)
            if value & 4:   # Bottom
                canvas.fill_rect(x + wall, y + node, node - wall, wall, color)
            if value & 2:   # Right
                canvas.fill_rect(x + node, y + wall, wall, node - wall, color)
            if value & 8:   # Left
                canvas.fill_rect(x, y + wall, wall, node - wall, color)
