from src.models.maze_model import MazeModel
from src.views.renderers import BaseRenderer


class SquareRenderer(BaseRenderer):
    def __init__(self, app, model: MazeModel) -> None:
        super().__init__(app, model)

        self.wall_size = 2
        self.compute_scales()

        self.last_update = 0
        self.update_interval = 1/30  # 30 fps

        self.layers = {
            "maze": self.create_canvas(self.offset_x, self.offset_y,
                                       0, self.maze_w, self.maze_h),
            "path": self.create_canvas(self.offset_x, self.offset_y,
                                       1, self.maze_w, self.maze_h),
            "ui": self.create_canvas(0, 0, 99, self.app.window_width,
                                     self.app.window_height)
        }

        self.colors = {
            "logo": 0xFFF0000FF,
            "entry": 0xFF00FF00,
            "exit": 0xFFFF0000,
            "path_1": 0xFF00FF00,
            "path_2": 0xFFFF0000,
            "walls": 0xFFFFFFFF,
            "character": 0xFF00FFFF
        }

    def compute_scales(self):
        available_w = self.app.window_width - self.pad_w * 2 - self.wall_size
        available_h = self.app.window_height - self.pad_h * 2 - self.wall_size
        cols = self.model.width
        rows = self.model.height

        self.node_size = min(available_w // cols, available_h // rows)
        self.maze_w = cols * self.node_size + self.wall_size
        self.maze_h = rows * self.node_size + self.wall_size
        self.offset_x = (self.app.window_width - self.maze_w) // 2
        self.offset_y = (self.app.window_height - self.maze_h) // 2

    def render_maze(self):
        node = self.node_size
        wall = self.wall_size
        color = self.colors.get("walls")

        canvas = self.layers.get("maze")
        canvas.clear()

        for y, row in enumerate(self.model.grid):
            for x, cell in enumerate(row):
                pos_x = x * self.node_size
                pos_y = y * self.node_size

                if cell & 1:   # Top
                    canvas.fill_rect(pos_x, pos_y, node + wall, wall, color)
                if cell & 2:   # Right
                    canvas.fill_rect(pos_x + node, pos_y, wall, node + wall,
                                     color)
                if cell & 4:   # Bottom
                    canvas.fill_rect(pos_x, pos_y + node, node + wall, wall,
                                     color)
                if cell & 8:   # Left
                    canvas.fill_rect(pos_x, pos_y, wall, node + wall, color)
                if cell == 0xF:    # 42 Logo
                    canvas.fill_rect(pos_x + wall, pos_y + wall, node - wall,
                                     node - wall, self.colors.get("logo"))

    def draw_endpoints(self):
        path = self.layers.get("path")
        color_entry = self.colors.get("entry")
        color_exit = self.colors.get("exit")
        node = self.node_size
        wall = self.wall_size

        path.fill_rect(self.model.entry[1] * node + wall,
                       self.model.entry[0] * node + wall,
                       node - wall, node - wall, color_entry)
        path.fill_rect(self.model.exit[1] * node + wall,
                       self.model.exit[0] * node + wall,
                       node - wall, node - wall, color_exit)

    def render_path(self):
        node = self.node_size
        wall = self.wall_size
        step = self.model.path_step
        curr_y, curr_x = self.model.entry
        canvas = self.layers.get("path")

        canvas.clear()
        self.draw_endpoints()

        for i in range(step):
            if i >= len(self.model.path):
                break

            direction = self.model.path[i]
            color = self.get_gradient_color(
                self.colors.get("path_1"),
                self.colors.get("path_2"),
                i / max(1, len(self.model.path) - 1)
            )

            match direction:
                case "N": curr_y -= 1
                case "S": curr_y += 1
                case "W": curr_x -= 1
                case "E": curr_x += 1

            draw_x = curr_x * node + wall   # x position of rectangle
            draw_y = curr_y * node + wall   # y position of rectangle
            draw_w = node - wall            # width of rectangle
            draw_h = node - wall            # height of rectangle

            match direction:
                case "N":
                    draw_h += wall
                case "S":
                    draw_y -= wall
                    draw_h += wall
                case "W":
                    draw_w += wall
                case "E":
                    draw_x -= wall
                    draw_w += wall

            canvas.fill_rect(draw_x, draw_y, draw_w, draw_h, color)

            if (curr_y, curr_x) == self.model.exit:
                self.draw_endpoints()
                return
