from typing import Any
from src.mlx import Mlx


class Canvas:
    def __init__(self, mlx: Mlx, mlx_ptr: Any,
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
