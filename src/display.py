#!/usr/bin/env python3

from mlx import Mlx
from .maze import Maze, Canvas
import sys
import time


class DisplayMaze(Maze):
    def __init__(self,
                 config: str,
                 maze_file: str) -> None:
        super().__init__(config)
        self.mlx = Mlx()
        self.MLX_PTR = self.mlx.mlx_init()
        if not self.MLX_PTR:
            sys.exit("Failed to initialize MLX")

        # Get maze data from file
        try:
            self.MAZE_DICT = self.parse_maze(maze_file)
        except FileNotFoundError:
            sys.exit(f"\"{maze_file}\" file not found.")

        self.ENTRY_POINT = self.MAZE_DICT.get("entry")
        self.EXIT_POINT = self.MAZE_DICT.get("exit")
        self.VALID_PATH = self.MAZE_DICT.get("path")
        self.MAZE_DATA = self.MAZE_DICT.get("maze")

        self.NODE_SIZE = (min(self.MAZE_WIDTH, self.MAZE_HEIGHT)
                          // max(len(self.MAZE_DATA), len(self.MAZE_DATA[0])))

        self.WIN_PTR = self.mlx.mlx_new_window(
            self.MLX_PTR,
            self.WINDOW_WIDTH,
            self.WINDOW_HEIGHT,
            "A-Maze-ing Display"
        )

        self.layers = {}

        self.keys_pressed = set()
        self.last_action_time = 0
        self.ACTION_INTERVAL = 0.1  # 100ms

    def add_layer(self, layer: Canvas, name: str):
        self.layers.update({name: layer})

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
                self.draw_maze_square_outline(
                    canvas, x * s, y * s, value, color
                )

    def draw_maze_square_outline(self, canvas: Canvas,
                                 start_x: int, start_y: int,
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

    def draw_entry_node(self, canvas: Canvas):
        s = self.NODE_SIZE
        w = self.LINE_WEIGHT
        canvas.fill_rect(self.ENTRY_POINT[1] * s + w,
                         self.ENTRY_POINT[0] * s + w,
                         s - w, s - w, 0xFF00FF00)  # Green

    def draw_exit_node(self, canvas: Canvas):
        s = self.NODE_SIZE
        w = self.LINE_WEIGHT
        canvas.fill_rect(self.EXIT_POINT[1] * s + w,
                         self.EXIT_POINT[0] * s + w,
                         s - w, s - w, 0xFFFF0000)  # Red

    def draw_valid_path(self, canvas: Canvas):
        s = self.NODE_SIZE
        w = self.LINE_WEIGHT
        y, x = self.ENTRY_POINT

        for direction in self.VALID_PATH:
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

            canvas.fill_rect(draw_x, draw_y, draw_w, draw_h, 0xFF0000FF)

            if (y, x) == self.EXIT_POINT:
                self.draw_exit_node(canvas)

            yield

    def update_window(self):
        for canvas in self.layers.values():
            self.mlx.mlx_put_image_to_window(
                self.MLX_PTR, self.WIN_PTR, canvas.ptr,
                canvas.pos_x, canvas.pos_y
            )

    def clear_window(self):
        for canvas in self.layers.values():
            canvas.destroy()
        self.mlx.mlx_destroy_window(self.MLX_PTR, self.WIN_PTR)

    def handle_keypress(self, keycode, param) -> None:
        self.keys_pressed.add(keycode)

    def handle_keyrelease(self, keycode, param) -> None:
        if keycode in self.keys_pressed:
            self.keys_pressed.remove(keycode)

    def update(self, param):
        current_time = time.time()
        if 65307 in self.keys_pressed:    # Escape
            self.clear_window()
            self.mlx.mlx_release(self.MLX_PTR)
        if 65363 in self.keys_pressed:    # Right Arrow
            if current_time - self.last_action_time >= self.ACTION_INTERVAL:
                try:
                    next(self.path_gen)
                    self.update_window()
                    self.last_action_time = current_time
                except (StopIteration, AttributeError):
                    pass

    def run_maze_display(self):
        maze_canvas = Canvas(
            self.mlx, self.MLX_PTR, self.CANVAS_WIDTH, self.CANVAS_HEIGHT,
            (self.WINDOW_WIDTH - self.CANVAS_WIDTH) // 2,
            (self.WINDOW_HEIGHT - self.CANVAS_HEIGHT) // 2
        )
        self.draw_maze_walls(maze_canvas)
        self.add_layer(maze_canvas, "maze")

        path_canvas = Canvas(
            self.mlx, self.MLX_PTR, self.CANVAS_WIDTH, self.CANVAS_HEIGHT,
            (self.WINDOW_WIDTH - self.CANVAS_WIDTH) // 2,
            (self.WINDOW_HEIGHT - self.CANVAS_HEIGHT) // 2
        )
        self.add_layer(path_canvas, "path")

        self.draw_entry_node(path_canvas)
        self.draw_exit_node(path_canvas)
        self.path_gen = self.draw_valid_path(self.layers.get("path"))

        self.update_window()

        self.mlx.mlx_string_put(
            self.MLX_PTR, self.WIN_PTR, 4, 4, 0xFFFFFFFF,
            "Right arrow: Solve | Escape: Close"
        )
        self.mlx.mlx_hook(self.WIN_PTR, 2, 1, self.handle_keypress, None)
        self.mlx.mlx_hook(self.WIN_PTR, 3, 2, self.handle_keyrelease, None)
        self.mlx.mlx_loop_hook(self.MLX_PTR, self.update, None)
        self.mlx.mlx_loop(self.MLX_PTR)


if __name__ == "__main__":
    printer = DisplayMaze("config", "output_maze.txt")
    printer.run_maze_display()
