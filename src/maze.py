import os
import sys
from dotenv import load_dotenv


class Maze:
    def __init__(self, config: str) -> None:
        load_dotenv(config)

        # Get maze dimensions from config
        try:
            self.MAZE_WIDTH = int(os.environ.get("WIDTH"))
            self.MAZE_HEIGHT = int(os.environ.get("HEIGHT"))
        except ValueError:
            sys.exit("Error while parsing config file")

        # Wall thickness
        try:
            self.LINE_WEIGHT = int(os.environ.get("LINE_WEIGHT"))
        except TypeError:
            self.LINE_WEIGHT = 4

        # Window dimensions
        self.WINDOW_WIDTH = 1920
        self.WINDOW_HEIGHT = 1080

        self.CANVAS_WIDTH = self.MAZE_WIDTH + self.LINE_WEIGHT
        self.CANVAS_HEIGHT = self.MAZE_HEIGHT + self.LINE_WEIGHT

        if self.CANVAS_WIDTH > self.WINDOW_WIDTH:
            self.WINDOW_WIDTH = self.CANVAS_WIDTH
        if self.CANVAS_HEIGHT > self.WINDOW_HEIGHT:
            self.WINDOW_HEIGHT = self.CANVAS_HEIGHT


class Canvas:
    def __init__(self, mlx, mlx_ptr,
                 width: int, height: int,
                 pos_x: int, pos_y: int):
        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.mlx = mlx
        self.mlx_ptr = mlx_ptr

        self.ptr = self.mlx.mlx_new_image(mlx_ptr, width, height)
        self.addr, self.bpp, self.size_line, self.endian = (
            self.mlx.mlx_get_data_addr(self.ptr)
        )
        self.buffer = memoryview(self.addr)
        self.bytes_per_pixel = self.bpp // 8

    def fill_rect(self, x: int, y: int,
                  width: int, height: int,
                  color: int) -> None:
        if not (
          0 <= x < self.width
          and 0 <= x + width <= self.width
          and 0 <= y < self.height
          and 0 <= y + height <= self.height
        ):
            return

        b = color & 0xFF
        g = (color >> 8) & 0xFF
        r = (color >> 16) & 0xFF
        a = (color >> 24) & 0xFF

        pixel = (bytes([b, g, r, a]) if self.endian == 0
                 else bytes([a, r, g, b]))

        line_data = pixel * width
        for i in range(y, y + height):
            start = (i * self.size_line) + (x * self.bytes_per_pixel)
            self.buffer[start:(start + len(line_data))] = line_data

    def destroy(self):
        if self.ptr:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.ptr)
            self.ptr = None
