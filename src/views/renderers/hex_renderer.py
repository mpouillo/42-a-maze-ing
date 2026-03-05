from src.models.maze import MazeModel
from src.views.renderers import BaseRenderer


class HexRenderer(BaseRenderer):
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
            "logo": 0xFFF0000FF,
            "entry": 0xFF00FF00,
            "exit": 0xFFFF0000,
            "path_1": 0xFF00FF00,
            "path_2": 0xFFFF0000,
            "walls": 0xFFFFFFFF,
            "character": 0xFF00FFFF
        }

    def compute_scales(self):
        pass

    def render_maze(self):
        pass

    def render_path(self):
        pass
