"""Low-level pixel buffer helpers for MiniLibX rendering.

The :class:`~Canvas` class wraps an MLX image, exposes a byte-backed buffer,
and provides basic drawing primitives (rectangles, pixels, and thick lines).
"""

from typing import Any


class Canvas:
    """An MLX image plus drawing helpers.

    Args:
        app: Application-like object exposing MLX pointers.
        x: X position where the image is blitted in the window.
        y: Y position where the image is blitted in the window.
        z: Z-index used for layer compositing.
        width: Image width in pixels.
        height: Image height in pixels.
    """

    def __init__(
        self, app: Any, x: int, y: int, z: int, width: int, height: int
    ) -> None:
        self.app: Any = app
        self.x: int = x
        self.y: int = y
        self.z: int = z
        self.width: int = width
        self.height: int = height

        self.ptr: int | None = self.app.mlx.mlx_new_image(
            self.app.mlx_ptr, width, height
        )
        self.addr, self.bpp, self.size_line, self.endian = (
            self.app.mlx.mlx_get_data_addr(self.ptr)
        )
        self.buffer: memoryview = memoryview(self.addr)
        self.bytes_per_pixel: int = self.bpp // 8

        self.clear()

    def get_color_bytes(self, color: int) -> bytes:
        """Convert an RGBA int into bytes in the order expected by MLX."""
        b: int = color & 0xFF
        g: int = (color >> 8) & 0xFF
        r: int = (color >> 16) & 0xFF
        a: int = (color >> 24) & 0xFF

        return bytes([b, g, r, a]) if self.endian == 0 else bytes([a, r, g, b])

    def fill_rect(
        self, x: int, y: int, width: int, height: int, color: int
    ) -> None:
        """Fill a rectangular area in the backing buffer."""
        if not (
            0 <= x < self.width
            and 0 <= x + width <= self.width
            and 0 <= y < self.height
            and 0 <= y + height <= self.height
        ):
            return

        pixel: bytes = self.get_color_bytes(color)
        line_data: bytes = pixel * width

        for i in range(y, y + height):
            start: int = (i * self.size_line) + (x * self.bytes_per_pixel)
            self.buffer[start: (start + len(line_data))] = line_data

    def draw_pixel(self, x: int, y: int, pixel: bytes) -> None:
        """Write a single pixel into the backing buffer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            start = (y * self.size_line) + (x * self.bytes_per_pixel)
            self.buffer[start: (start + self.bytes_per_pixel)] = pixel

    def draw_line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: int,
        thickness: int = 1,
    ) -> None:
        """Draw a straight line (optionally thick) into the backing buffer."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
        err: int = dx - dy
        pixel: bytes = self.get_color_bytes(color)

        offsets: list[tuple[int, int]] = []
        if thickness > 1:
            half: int = thickness // 2
            for i in range(-half, half + 1):
                for j in range(-half, half + 1):
                    if i * i + j * j <= half * half + 1:
                        offsets.append((i, j))
        if not offsets:
            offsets = [(0, 0)]

        while True:
            for ox, oy in offsets:
                self.draw_pixel(x0 + ox, y0 + oy, pixel)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def clear(self) -> None:
        """Clear the image buffer.

        The buffer is filled with zeros (transparent black).
        """
        self.buffer[:] = bytes([0]) * (
            self.width * self.height * self.bytes_per_pixel
        )

    def destroy(self) -> None:
        """Destroy the underlying MLX image."""
        if self.ptr:
            self.app.mlx.mlx_destroy_image(self.app.mlx_ptr, self.ptr)
            self.ptr = None
