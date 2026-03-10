from src.models.maze import MazeModel
from src.views.renderers import BaseRenderer


class SquareRenderer(BaseRenderer):
    def __init__(self, app, model: MazeModel) -> None:
        super().__init__(app, model)

        self.wall_size = 4
        self.compute_scales()
        self.prev_gen = None

        self.add_layer("maze", self.offset_x, self.offset_y,
                       1, self.maze_w, self.maze_h)
        self.add_layer("path", self.offset_x, self.offset_y,
                       2, self.maze_w, self.maze_h)
        self.add_layer("endpoints", self.offset_x, self.offset_y,
                       3, self.maze_w, self.maze_h)

    def compute_scales(self):
        available_w = self.app.window_width - self.pad_w * 2 - self.wall_size
        available_h = self.app.window_height - self.pad_h * 2 - self.wall_size
        cols = self.model.config.width
        rows = self.model.config.height

        self.cell_size = max(1, min(available_w // cols, available_h // rows))
        if self.wall_size > 1 and self.cell_size <= self.wall_size * 2:
            self.wall_size = max(1, self.cell_size // 2)
            self.compute_scales()

        self.maze_w = cols * self.cell_size + self.wall_size
        self.maze_h = rows * self.cell_size + self.wall_size
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
                    self.draw_cell_center(canvas, x, y, cell_color)

    def draw_path(self, path: list, color: int = None):
        color_start = self.colors.get("path_1")
        color_end = self.colors.get("path_2")
        canvas = self.layers.get("path")
        canvas.clear()

        for i, (y1, x1) in enumerate(path):
            color = self.get_gradient_color(color_start, color_end,
                                            i / max(1, len(path) - 1))
            self.draw_cell_center(canvas, x1, y1, color)
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

    def draw_step(self, step_data: dict):
        step_color = self.colors.get("step")
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
                if self.prev_gen:
                    self.draw_cell_center(maze_canvas, *self.prev_gen)
                self.draw_cell_center(maze_canvas, x1, y1)
                self.draw_cell_center(maze_canvas, x2, y2, step_color)
                self.draw_cell_walls(maze_canvas, x1, y1, wall)
            case 'fill':
                path_canvas = self.layers.get("path")
                self.draw_cell_center(path_canvas, x1, y1,
                                      step_color & 0x7FFFFFFF)
                self.draw_cell_center(path_canvas, x2, y2, step_color)
                self.draw_cell_walls(path_canvas, x1, y1, wall,
                                     False, step_color & 0x7FFFFFFF)
            case _:
                pass

    def draw_endpoints(self):
        canvas = self.layers.get("endpoints")
        self.draw_cell_center(canvas, self.model.config.entry[1],
                              self.model.config.entry[0],
                              self.colors.get("entry"))
        self.draw_cell_center(canvas, self.model.config.exit[1],
                              self.model.config.exit[0],
                              self.colors.get("exit"))

    def draw_cell_center(self, canvas, x, y, color=0xFF000000):
        cell = self.cell_size
        wall = self.wall_size
        canvas.fill_rect(x * cell + wall, y * cell + wall,
                         cell - wall, cell - wall, color)

    def draw_cell_walls(self, canvas, x, y, value=0,
                        corners=False, color=0xFF000000) -> None:
        cell = self.cell_size
        wall = self.wall_size
        x *= cell
        y *= cell

        if corners is True:
            if value & 1:   # Top
                canvas.fill_rect(x, y, cell + wall, wall, color)
            if value & 4:   # Bottom
                canvas.fill_rect(x, y + cell, cell + wall, wall, color)
            if value & 2:   # Right
                canvas.fill_rect(x + cell, y, wall, cell + wall, color)
            if value & 8:   # Left
                canvas.fill_rect(x, y, wall, cell + wall, color)
        else:
            if value & 1:   # Top
                canvas.fill_rect(x + wall, y, cell - wall, wall, color)
            if value & 4:   # Bottom
                canvas.fill_rect(x + wall, y + cell, cell - wall, wall, color)
            if value & 2:   # Right
                canvas.fill_rect(x + cell, y + wall, wall, cell - wall, color)
            if value & 8:   # Left
                canvas.fill_rect(x, y + wall, wall, cell - wall, color)
