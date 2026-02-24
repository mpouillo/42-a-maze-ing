import os
import sys
from dotenv import load_dotenv
from src.mlx import Mlx
from src.canvas import Canvas
from typing import Any


class DrawMaze:
    def __init__(self, mlx: Mlx, mlx_ptr: Any, win_ptr: Any,
                 window_width: int, window_height: int,
                 config_file: str, maze_file: str) -> None:
        self.load_config(config_file)

        self.MLX = mlx
        self.MLX_PTR = mlx_ptr
        self.WIN_PTR = win_ptr
        self.WINDOW_WIDTH = window_width
        self.WINDOW_HEIGHT = window_height
        self.layers = {}
        self.maze_file = maze_file

        self.update_maze_data(maze_file)
        self.set_colors()
        self.update_interval = 0.2
        self.last_path_update = 0
        self.path_step = 0
        self.solving = False

    def load_config(self, config_file: str) -> None:
        load_dotenv(config_file)

        try:
            self.MAZE_WIDTH = int(os.environ.get("WIDTH"))
            self.MAZE_HEIGHT = int(os.environ.get("HEIGHT"))
        except ValueError:
            sys.exit("Error while parsing config file")

        try:
            self.LINE_WEIGHT = int(os.environ.get("LINE_WEIGHT"))
        except TypeError:
            self.LINE_WEIGHT = 2

    def update_maze_data(self, maze_file: str):
        try:
            self.MAZE_DICT = self.parse_maze(maze_file)
        except FileNotFoundError:
            sys.exit(f"\"{maze_file}\" file not found.")

        self.ENTRY_POINT = self.MAZE_DICT.get("entry")
        self.EXIT_POINT = self.MAZE_DICT.get("exit")
        self.VALID_PATH = self.MAZE_DICT.get("path")
        self.MAZE_DATA = self.MAZE_DICT.get("maze")

        self.t_margin = 180
        self.b_margin = 20
        self.l_margin = 20
        self.r_margin = 20
        self.ALLOWED_WIDTH = (self.WINDOW_WIDTH
                              - (self.l_margin + self.r_margin))
        self.ALLOWED_HEIGHT = (self.WINDOW_HEIGHT
                               - (self.t_margin + self.b_margin))

        max_w = (self.ALLOWED_WIDTH - self.LINE_WEIGHT) // self.MAZE_WIDTH
        max_h = (self.ALLOWED_HEIGHT - self.LINE_WEIGHT) // self.MAZE_HEIGHT
        self.NODE_SIZE = min(max_w, max_h)

        self.CANVAS_WIDTH = (self.MAZE_WIDTH * self.NODE_SIZE
                             + self.LINE_WEIGHT)
        self.CANVAS_HEIGHT = (self.MAZE_HEIGHT * self.NODE_SIZE
                              + self.LINE_WEIGHT)

    def set_colors(self,
                   fortytwo: int = 0xFFF0000FF,
                   maze_entry: int = 0xFF00FF00,
                   maze_exit: int = 0xFFFF0000,
                   path_start: int = 0xFF00FF00,
                   path_end: int = 0xFFFF0000,
                   walls: int = 0xFFFFFFFF):
        self.COLOR_42 = fortytwo
        self.COLOR_ENTRY = maze_entry
        self.COLOR_EXIT = maze_exit
        self.COLOR_PATH_START = path_start
        self.COLOR_PATH_END = path_end
        self.COLOR_WALLS = walls

    @staticmethod
    def parse_maze(filename: str) -> dict:
        '''Parse file and return maze data as a dict'''
        try:
            data = {}
            array = []
            with open(filename, 'r') as maze_file:
                for line in maze_file:
                    if not line.strip():
                        break
                    row = []
                    for c in line.strip():
                        row.append(int(c, 16))
                    array.append(row)
                data.update({"maze": array})
                data.update(
                    {"entry": tuple(
                        int(c) for c in maze_file.readline().strip().split(",")
                    )}
                )
                data.update(
                    {"exit": tuple(
                        int(c) for c in maze_file.readline().strip().split(",")
                    )}
                )
                data.update({"path": maze_file.readline().strip()})
            return data
        except Exception as e:
            sys.exit(f"Error while parsing maze output file: {e}")

    def draw_maze_walls(self, canvas: Canvas, color: int = 0xFFFFFFFF):
        x, y = 0, 0
        s = self.NODE_SIZE
        for y, row in enumerate(self.MAZE_DATA):
            for x, value in enumerate(row):
                self.draw_maze_cell(canvas, x * s, y * s, value, color)

    def draw_maze_cell(self, canvas: Canvas, start_x: int, start_y: int,
                       bit_value: int, color: int) -> None:
        w = self.LINE_WEIGHT
        s = self.NODE_SIZE

        if bit_value & 1:   # Top
            canvas.fill_rect(start_x, start_y, s + w, w, color)
        if bit_value & 2:   # Right
            canvas.fill_rect(start_x + s, start_y, w, s + w, color)
        if bit_value & 4:   # Bottom
            canvas.fill_rect(start_x, start_y + s, s + w, w, color)
        if bit_value & 8:   # Left
            canvas.fill_rect(start_x, start_y, w, s + w, color)

        if bit_value == 0xF:    # 42 Logo
            canvas.fill_rect(start_x + w, start_y + w,
                             s - w, s - w, self.COLOR_42)

    def draw_entry_node(self, canvas: Canvas):
        s = self.NODE_SIZE
        w = self.LINE_WEIGHT
        canvas.fill_rect(self.ENTRY_POINT[1] * s + w,
                         self.ENTRY_POINT[0] * s + w,
                         s - w, s - w, self.COLOR_ENTRY)

    def draw_exit_node(self, canvas: Canvas):
        s = self.NODE_SIZE
        w = self.LINE_WEIGHT
        canvas.fill_rect(self.EXIT_POINT[1] * s + w,
                         self.EXIT_POINT[0] * s + w,
                         s - w, s - w, self.COLOR_EXIT)

    def get_gradient_color(self, c1, c2, mix):
        a1 = (c1 >> 24) & 0xFF
        r1 = (c1 >> 16) & 0xFF
        g1 = (c1 >> 8) & 0xFF
        b1 = c1 & 0xFF
        a2 = (c2 >> 24) & 0xFF
        r2 = (c2 >> 16) & 0xFF
        g2 = (c2 >> 8) & 0xFF
        b2 = c2 & 0xFF
        a = int(a1 + (a2 - a1) * mix)
        r = int(r1 + (r2 - r1) * mix)
        g = int(g1 + (g2 - g1) * mix)
        b = int(b1 + (b2 - b1) * mix)
        return (a << 24) | (r << 16) | (g << 8) | b

    def draw_valid_path(self, canvas: Canvas):
        s = self.NODE_SIZE
        w = self.LINE_WEIGHT
        y_start, x_start = self.ENTRY_POINT
        total_steps = len(self.VALID_PATH)

        if not hasattr(self, 'path_step'):
            self.path_step = 0

        while self.path_step < total_steps:
            curr_y, curr_x = y_start, x_start

            for i in range(self.path_step + 1):
                direction = self.VALID_PATH[i]
                color = self.get_gradient_color(
                    self.COLOR_PATH_START,
                    self.COLOR_PATH_END,
                    i / max(1, total_steps - 1)
                )

                match direction:
                    case "N": curr_y -= 1
                    case "S": curr_y += 1
                    case "W": curr_x -= 1
                    case "E": curr_x += 1

                draw_x = curr_x * s + w  # x position of rectangle
                draw_y = curr_y * s + w  # y position of rectangle
                draw_w = s - w      # width of rectangle
                draw_h = s - w      # height of rectangle

                match direction:
                    case "N":
                        draw_h += w
                    case "S":
                        draw_y -= w
                        draw_h += w
                    case "W":
                        draw_w += w
                    case "E":
                        draw_x -= w
                        draw_w += w

            canvas.fill_rect(draw_x, draw_y, draw_w, draw_h, color)

            if (curr_y, curr_x) == self.EXIT_POINT:
                self.draw_exit_node(canvas)
                return

            self.path_step += 1
            yield

    def draw_layers_to_window(self) -> None:
        sorted_layers = sorted(
            self.layers.values(),
            key=lambda item: item.get("z_index")
        )
        for layer in sorted_layers:
            canvas = layer.get("canvas")
            self.MLX.mlx_put_image_to_window(
                self.MLX_PTR, self.WIN_PTR, canvas.ptr,
                canvas.pos_x, canvas.pos_y
            )

    def add_layer(self, x, y, z_index, width, height, name: str):
        canvas = Canvas(
            self.MLX, self.MLX_PTR, x, y, width, height, name
        )
        self.layers.update({name: {"canvas": canvas, "z_index": z_index}})
        return canvas

    def clear_layers(self, *names: str):
        if names:
            for name in names:
                layer = self.layers.get(name)
                if layer:
                    layer.get("canvas").destroy()
                    del self.layers[name]
        else:
            for layer_data in self.layers.values():
                layer_data.get("canvas").destroy()
            self.layers.clear()

    def init_path_layer(self, path_step: int = 0) -> Canvas:
        self.clear_layers("path")
        x_pos = self.l_margin + (self.ALLOWED_WIDTH - self.CANVAS_WIDTH) // 2
        y_pos = self.t_margin + (self.ALLOWED_HEIGHT - self.CANVAS_HEIGHT) // 2
        path_canvas = self.add_layer(
            x_pos, y_pos, 1, self.CANVAS_WIDTH, self.CANVAS_HEIGHT, "path"
        )

        self.draw_entry_node(path_canvas)
        self.draw_exit_node(path_canvas)

        self.path_step = 0
        self.path_gen = self.draw_valid_path(path_canvas)

        for _ in range(path_step):
            try:
                next(self.path_gen)
            except StopIteration:
                break

        return path_canvas

    def init_maze_layer(self):
        self.clear_layers("maze")
        x_pos = self.l_margin + (self.ALLOWED_WIDTH - self.CANVAS_WIDTH) // 2
        y_pos = self.t_margin + (self.ALLOWED_HEIGHT - self.CANVAS_HEIGHT) // 2
        maze_canvas = self.add_layer(
            x_pos, y_pos, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT, "maze"
        )
        self.draw_maze_walls(maze_canvas, self.COLOR_WALLS)
        return maze_canvas

    def rebuild_maze(self):
        current_step = getattr(self, "path_step", 0)
        was_solving = self.solving
        self.update_maze_data(self.maze_file)
        self.init_maze_layer()
        self.init_path_layer(current_step)
        self.solving = was_solving
