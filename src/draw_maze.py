#!/usr/bin/env python3

import sys
from src.mlx import Mlx
from src.canvas import Canvas
from src.maze import Maze
from typing import Any


class DrawMaze(Maze):
    def __init__(self, mlx: Mlx, mlx_ptr: Any, win_ptr: Any,
                 window_width: int, window_height: int,
                 config: str, maze_file: str) -> None:
        super().__init__(config)

        self.MLX = mlx
        self.MLX_PTR = mlx_ptr
        self.WIN_PTR = win_ptr
        self.WINDOW_WIDTH = window_width
        self.WINDOW_HEIGHT = window_height
        self.layers = {}

        self.set_maze_data(self.MLX, self.MLX_PTR, maze_file)
        self.set_colors()

    def set_maze_data(self, mlx: Mlx, mlx_ptr: Any, maze_file: str):
        try:
            self.MAZE_DICT = self.parse_maze(maze_file)
        except FileNotFoundError:
            sys.exit(f"\"{maze_file}\" file not found.")

        self.ENTRY_POINT = self.MAZE_DICT.get("entry")
        self.EXIT_POINT = self.MAZE_DICT.get("exit")
        self.VALID_PATH = self.MAZE_DICT.get("path")
        self.MAZE_DATA = self.MAZE_DICT.get("maze")

        margin = 80
        self.CANVAS_WIDTH = self.WINDOW_HEIGHT - margin
        self.CANVAS_HEIGHT = self.WINDOW_HEIGHT - margin

        max_w = (self.CANVAS_WIDTH - self.LINE_WEIGHT) // self.MAZE_WIDTH
        max_h = (self.CANVAS_HEIGHT - self.LINE_WEIGHT) // self.MAZE_HEIGHT
        self.NODE_SIZE = min(max_w, max_h)

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
        y, x = self.ENTRY_POINT
        total_steps = len(self.VALID_PATH)

        for i, direction in enumerate(self.VALID_PATH):
            color = self.get_gradient_color(self.COLOR_PATH_START,
                                            self.COLOR_PATH_END,
                                            i / max(1, total_steps - 1))

            match direction:
                case "N": y -= 1
                case "S": y += 1
                case "W": x -= 1
                case "E": x += 1

            draw_x = x * s + w  # x position of rectangle
            draw_y = y * s + w  # y position of rectangle
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

            if (y, x) == self.EXIT_POINT:
                self.draw_exit_node(canvas)

            yield

    def draw_layers_to_window(self, canvas_list: list | None = None) -> None:
        if canvas_list is None:
            canvas_list = self.layers.values()
        for canvas in canvas_list:
            self.MLX.mlx_put_image_to_window(
                self.MLX_PTR, self.WIN_PTR, canvas.ptr,
                canvas.pos_x, canvas.pos_y
            )

    def add_layer(self, layer: Canvas, name: str):
        self.layers.update({name: layer})

    def clear_layers(self):
        for canvas in self.layers.values():
            canvas.destroy()
        self.MLX.mlx_destroy_window(self.MLX_PTR, self.WIN_PTR)

    def run_maze_display(self):
        maze_canvas = Canvas(
            self.MLX, self.MLX_PTR, self.CANVAS_WIDTH, self.CANVAS_HEIGHT,
            (self.WINDOW_WIDTH - self.CANVAS_WIDTH) // 2,
            (self.WINDOW_HEIGHT - self.CANVAS_HEIGHT) // 2
        )
        self.draw_maze_walls(maze_canvas)

        path_canvas = Canvas(
            self.MLX, self.MLX_PTR, self.CANVAS_WIDTH, self.CANVAS_HEIGHT,
            (self.WINDOW_WIDTH - self.CANVAS_WIDTH) // 2,
            (self.WINDOW_HEIGHT - self.CANVAS_HEIGHT) // 2
        )
        self.draw_entry_node(path_canvas)
        self.draw_exit_node(path_canvas)
        list(self.draw_valid_path(path_canvas))

        self.add_layer(maze_canvas, "maze")
        self.add_layer(path_canvas, "path")

        self.draw_layers_to_window()
