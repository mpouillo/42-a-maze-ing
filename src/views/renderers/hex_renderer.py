from src.models.maze import MazeModel
from src.views.renderers import BaseRenderer
import math


class HexRenderer(BaseRenderer):
    def __init__(self, app, model: MazeModel) -> None:
        super().__init__(app, model)

        self.wall_size = 4
        self.compute_scales()
        print(self.wall_size)
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
        s_x = available_w / (math.sqrt(3) * (cols + 0.5))
        s_y = available_h / (1.5 * rows + 0.5)

        self.cell_size = max(1, int(min(s_x, s_y)))
        if self.wall_size > 1 and self.cell_size <= self.wall_size * 2:
            self.wall_size = max(1, self.wall_size - 1)
            self.compute_scales()

        self.hex_w = math.sqrt(3) * self.cell_size
        self.hex_h = 2 * self.cell_size
        self.maze_w = (int(cols * self.hex_w + self.hex_w / 2)
                       + self.wall_size * 2)
        self.maze_h = (int(rows * 1.5 * self.cell_size + 0.5 * self.cell_size)
                       + self.wall_size * 2)
        self.offset_x = (self.app.window_width - self.maze_w) // 2
        self.offset_y = (self.app.window_height - self.maze_h) // 2

    def draw_maze(self):
        wall_color = self.colors.get("walls")
        cell_color = self.colors.get("cell")
        canvas = self.layers.get("maze")
        canvas.clear()

        for y, row in enumerate(self.model.maze):
            for x, value in enumerate(row):
                if value == 63:
                    self.draw_cell_center(canvas, x, y, cell_color)
                self.draw_cell_walls(canvas, x, y, value, wall_color)

    def draw_path(self, path: list, color: int = None):
        color_start = self.colors.get("path_1")
        color_end = self.colors.get("path_2")
        canvas = self.layers.get("path")
        canvas.clear()

        for i, (y1, x1) in enumerate(path):
            color = self.get_gradient_color(
                color_start, color_end, i / max(1, len(path) - 1)
            )
            self.draw_cell_center(canvas, x1, y1, color)
            if i == 0:
                continue
            (y2, x2) = path[i - 1]
            wall = self.get_wall_direction(y1, x1, y2, x2)
            self.draw_cell_walls(canvas, x1, y1, wall, color)

    def draw_step(self, step_data: dict):
        step_color = self.colors.get("step")
        cmd, (y1, x1), (y2, x2) = step_data

        wall = self.get_wall_direction(y1, x1, y2, x2)
        if not wall:
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
                                     step_color & 0x7FFFFFFF)
            case _:
                pass

        self.prev_gen = (x2, y2)

    def draw_endpoints(self):
        canvas = self.layers.get("endpoints")
        self.draw_cell_center(
            canvas, self.model.config.entry[1], self.model.config.entry[0],
            self.colors.get("entry")
        )
        self.draw_cell_center(
            canvas, self.model.config.exit[1], self.model.config.exit[0],
            self.colors.get("exit")
        )

    def get_center(self, x, y):
        cx = (x * self.hex_w + (self.hex_w / 2 if y % 2 == 1 else 0)
              + self.hex_w / 2 + self.wall_size)
        cy = y * 1.5 * self.cell_size + self.cell_size + self.wall_size
        return int(cx), int(cy)

    def get_wall_direction(self, y1, x1, y2, x2):
        is_odd = y1 % 2 != 0
        dy, dx = y2 - y1, x2 - x1

        if is_odd:
            return {
                (-1, 1): 1,
                (0, 1): 2,
                (1, 1): 4,
                (1, 0): 8,
                (0, -1): 16,
                (-1, 0): 32
            }.get((dy, dx), 0)
        else:
            return {
                (-1, 0): 1,
                (0, 1): 2,
                (1, 0): 4,
                (1, -1): 8,
                (0, -1): 16,
                (-1, -1): 32
            }.get((dy, dx), 0)

    def draw_cell_center(self, canvas, x, y, color=0xFF000000):
        cx, cy = self.get_center(x, y)
        s = self.cell_size - self.wall_size // 2
        if s <= 0:
            return

        for i in range(int(-s), int(s) + 1):
            if i < -s / 2:   # Top Triangle
                half_w = (i + s) / (s / 2) * (math.sqrt(3) * s / 2)
            elif i > s / 2:  # Bottom Triangle
                half_w = (s - i) / (s / 2) * (math.sqrt(3) * s / 2)
            else:            # Middle Rect
                half_w = math.sqrt(3) * s / 2

            canvas.fill_rect(
                int(cx - half_w), int(cy + i), int(half_w * 2), 1, color
            )

    def draw_cell_walls(self, canvas, x, y, value=0, color=0xFF000000) -> None:
        cx, cy = self.get_center(x, y)
        s = self.cell_size
        w = round(math.sqrt(3) * s / 2)
        s_half = round(s / 2)

        v = [
            (cx, cy - s),           # 0: Top
            (cx + w, cy - s_half),  # 1: Top-Right
            (cx + w, cy + s_half),  # 2: Bottom-Right
            (cx, cy + s),           # 3: Bottom
            (cx - w, cy + s_half),  # 4: Bottom-Left
            (cx - w, cy - s_half)   # 5: Top-Left
        ]

        walls = [
            (v[0], v[1], 1),    # TR
            (v[1], v[2], 2),    # R
            (v[2], v[3], 4),    # BR
            (v[3], v[4], 8),    # BL
            (v[4], v[5], 16),   # L
            (v[5], v[0], 32)    # TL
        ]

        for (p1, p2, mask) in walls:
            if value & mask:
                canvas.draw_line(p1[0], p1[1], p2[0], p2[1],
                                 color, self.wall_size)
