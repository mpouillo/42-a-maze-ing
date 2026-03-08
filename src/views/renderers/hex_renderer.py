from src.models.maze import MazeModel
from src.views.renderers import BaseRenderer
import math


class HexRenderer(BaseRenderer):
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

        s_x = available_w / (math.sqrt(3) * (cols + 0.5))
        s_y = available_h / (1.5 * rows + 0.5)

        self.node_size = max(2, int(min(s_x, s_y)))
        self.hex_w = math.sqrt(3) * self.node_size
        self.hex_h = 2 * self.node_size

        self.maze_w = (int(cols * self.hex_w + self.hex_w / 2)
                       + self.wall_size * 2)
        self.maze_h = (int(rows * 1.5 * self.node_size + 0.5 * self.node_size)
                       + self.wall_size * 2)
        self.offset_x = (self.app.window_width - self.maze_w) // 2
        self.offset_y = (self.app.window_height - self.maze_h) // 2

    def get_center(self, x, y):
        cx = (x * self.hex_w + (self.hex_w / 2 if y % 2 == 1 else 0)
              + self.hex_w / 2 + self.wall_size)
        cy = y * 1.5 * self.node_size + self.node_size + self.wall_size
        return int(cx), int(cy)

    def draw_maze(self):
        wall_color = self.colors.get("walls")
        cell_color = self.colors.get("cell")
        canvas = self.layers.get("maze")
        canvas.clear()

        for y, row in enumerate(self.model.maze):
            for x, value in enumerate(row):
                self.draw_cell_walls(canvas, x, y, value, wall_color)
                if value == 63:
                    self.draw_cell_hex(canvas, x, y, cell_color)

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

    def draw_path(self, path: list, color: int = None):
        color_start = self.colors.get("path_1")
        color_end = self.colors.get("path_2")
        canvas = self.layers.get("path")
        canvas.clear()

        for i, (y1, x1) in enumerate(path):
            color = self.get_gradient_color(
                color_start, color_end, i / max(1, len(path) - 1)
            )
            self.draw_cell_hex(canvas, x1, y1, color)
            if i == 0:
                continue
            (y2, x2) = path[i - 1]
            wall = self.get_wall_direction(y1, x1, y2, x2)
            self.draw_cell_walls(canvas, x1, y1, wall, color)

    def draw_step(self, step_data: dict, color):
        maze_entry = self.model.config.entry
        maze_exit = self.model.config.exit
        cmd, (y1, x1), (y2, x2) = step_data

        wall = self.get_wall_direction(y1, x1, y2, x2)
        if not wall:
            return

        match cmd:
            case 'remove':
                maze_canvas = self.layers.get("maze")
                self.draw_cell_hex(maze_canvas, x1, y1)
                self.draw_cell_hex(maze_canvas, x2, y2)
                self.draw_cell_walls(maze_canvas, x1, y1, wall, 0x00000000)
            case 'fill':
                path_canvas = self.layers.get("path")
                if (y1, x1) not in [maze_entry, maze_exit]:
                    self.draw_cell_hex(path_canvas, x1, y1, color)
                if (y2, x2) not in [maze_entry, maze_exit]:
                    self.draw_cell_hex(path_canvas, x2, y2, color)
                self.draw_cell_walls(path_canvas, x1, y1, wall, color)

        if (y1, x1) == maze_entry or (y2, x2) == maze_exit:
            self.draw_endpoints()

    def draw_endpoints(self):
        canvas = self.layers.get("path")
        self.draw_cell_hex(
            canvas, self.model.config.entry[1], self.model.config.entry[0],
            self.colors.get("entry")
        )
        self.draw_cell_hex(
            canvas, self.model.config.exit[1], self.model.config.exit[0],
            self.colors.get("exit")
        )

    def draw_cell_hex(self, canvas, x, y, color=0xFF000000):
        cx, cy = self.get_center(x, y)
        s = self.node_size - self.wall_size // 2
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
        s = self.node_size
        w = self.hex_w / 2

        # Define the 6 points of the hexagon around the center
        v = [
            (cx, cy - s),           # 0: Top
            (cx + w, cy - s / 2),   # 1: Top-Right
            (cx + w, cy + s / 2),   # 2: Bottom-Right
            (cx, cy + s),           # 3: Bottom
            (cx - w, cy + s / 2),   # 4: Bottom-Left
            (cx - w, cy - s / 2)    # 5: Top-Left
        ]

        if value & 1:
            canvas.draw_line(*v[0], *v[1], color, self.wall_size)   # TR
        if value & 2:
            canvas.draw_line(*v[1], *v[2], color, self.wall_size)   # R
        if value & 4:
            canvas.draw_line(*v[2], *v[3], color, self.wall_size)   # BR
        if value & 8:
            canvas.draw_line(*v[3], *v[4], color, self.wall_size)   # BL
        if value & 16:
            canvas.draw_line(*v[4], *v[5], color, self.wall_size)   # L
        if value & 32:
            canvas.draw_line(*v[5], *v[0], color, self.wall_size)   # TL
