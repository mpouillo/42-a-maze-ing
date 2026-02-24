import os
import sys
from typing import Any
from src.mlx import Mlx


class Canvas:
    def __init__(self, mlx: Mlx, mlx_ptr: Any, x: int, y: int,
                 width: int, height: int, name: str) -> None:
        self.width = width
        self.height = height
        self.pos_x = x
        self.pos_y = y
        self.name = name

        self.mlx = mlx
        self.mlx_ptr = mlx_ptr

        self.ptr = self.mlx.mlx_new_image(mlx_ptr, width, height)
        self.addr, self.bpp, self.size_line, self.endian = (
            self.mlx.mlx_get_data_addr(self.ptr)
        )
        self.buffer = memoryview(self.addr)
        self.bytes_per_pixel = self.bpp // 8
        self.buffer[:] = (bytes([0]) *
                          (self.width * self.height * self.bytes_per_pixel))

        self.fonts_dir = "src/fonts"
        self.fonts_dict = self.parse_fonts(self.fonts_dir)
        self.font_scale = 3
        try:
            self.font_width = (len(self.fonts_dict.get("a")[0])
                               * self.font_scale)
            self.font_height = len(self.fonts_dict.get("a")) * self.font_scale
        except Exception:
            sys.exit("Failed to parse fonts dictionnary")

    def parse_fonts(self, fonts_dir):
        fonts_dict = {}
        files = os.listdir(fonts_dir)

        for f in files:
            try:
                with open(fonts_dir + "/" + f) as font_file:
                    array = []
                    for line in font_file:
                        row = []
                        for c in line.strip():
                            row.append(int(c, 16))
                        array.append(row)
                    fonts_dict.update({chr(int(f)): array})
            except (ValueError, TypeError) as e:
                sys.exit("Error while parsing fonts:", e)

        return fonts_dict

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

    def draw_text(self, start_x, start_y, text, color):
        char_offset = 0
        for character in text.lower():
            if character in self.fonts_dict:
                char_data = self.fonts_dict.get(character)
                for y, row in enumerate(char_data):
                    y *= self.font_scale
                    for x, value in enumerate(row):
                        x *= self.font_scale
                        if value == 1:
                            self.fill_rect(
                                start_x + x + char_offset, start_y + y,
                                self.font_scale, self.font_scale, color
                            )
            char_offset += self.font_width + self.font_scale

    def destroy(self):
        if self.ptr:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.ptr)
            self.ptr = None
