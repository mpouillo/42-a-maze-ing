"""Square-grid (orthogonal) maze renderer."""

from src.views.renderers import BaseRenderer
from src.views import Canvas
from typing import Any, TypeAlias

StepTuple: TypeAlias = tuple[str, tuple[int, int], tuple[int, int]]


class SquareRenderer(BaseRenderer):
    """Renderer that draws a rectangular maze (4-neighbor walls)."""

    def __init__(self, app: Any, model: Any) -> None:
        """Initialize layers used to draw maze, path, and endpoints."""
        super().__init__(app, model)

        self.wall_size: int = 4
        self.compute_scales()
        self.prev_gen: tuple[int, int] | None = None

        self.add_layer(
            "path", self.offset_x, self.offset_y, 1, self.maze_w, self.maze_h
        )
        self.add_layer(
            "maze", self.offset_x, self.offset_y, 2, self.maze_w, self.maze_h
        )
        self.add_layer(
            "endpoints",
            self.offset_x,
            self.offset_y,
            3,
            self.maze_w,
            self.maze_h,
        )

    def compute_scales(self) -> None:
        """Compute cell sizes and offsets to fit the maze into the window."""
        available_w: int = (
            self.app.window_width - self.pad_w * 2 - self.wall_size
        )
        available_h: int = (
            self.app.window_height - self.pad_h * 2 - self.wall_size
        )
        cols: int = self.model.config.width
        rows: int = self.model.config.height

        self.cell_size: int = max(
            1, min(available_w // cols, available_h // rows)
        )
        if self.wall_size > 1 and self.cell_size <= self.wall_size * 2:
            self.wall_size = max(1, self.wall_size - 1)
            self.compute_scales()

        self.maze_w: int = cols * self.cell_size + self.wall_size
        self.maze_h: int = rows * self.cell_size + self.wall_size
        self.offset_x: int = (self.app.window_width - self.maze_w) // 2
        self.offset_y: int = (self.app.window_height - self.maze_h) // 2

    def draw_maze(self) -> None:
        """Render the maze walls and cell fills to the maze layer."""
        wall_color: int = self.app.colors.get("walls")
        cell_color: int = self.app.colors.get("cell")
        canvas: Any = self.layers.get("maze")
        if not canvas:
            return
        canvas.clear()

        for y, row in enumerate(self.model.maze):
            for x, value in enumerate(row):
                self.draw_cell_walls(canvas, x, y, value, True, wall_color)
                if value == 0xF:
                    self.draw_cell_center(canvas, x, y, cell_color)

    def draw_path(self, path: list[tuple[int, int]]) -> None:
        """Render a path overlay to the path layer."""
        color_start: int = self.app.colors.get("path_1")
        color_end: int = self.app.colors.get("path_2")
        canvas: Any = self.layers.get("path")
        if not canvas:
            return
        canvas.clear()

        for i, (y1, x1) in enumerate(path):
            color: int = self.get_gradient_color(
                color_start, color_end, i / max(1, len(path) - 1)
            )
            self.draw_cell_center(canvas, x1, y1, color)
            if i == 0:
                continue
            (y2, x2) = path[i - 1]
            if y2 < y1:  # Top
                wall = 1
            elif y2 > y1:  # Bottom
                wall = 4
            elif x2 < x1:  # Left
                wall = 8
            elif x2 > x1:  # Right
                wall = 2
            self.draw_cell_walls(canvas, x1, y1, wall, False, color)

    def draw_step(self, step_data: StepTuple) -> None:
        """Render a single generation/solve step to the appropriate layer."""
        step_color: int = self.app.colors.get("step")
        cmd, (y1, x1), (y2, x2) = step_data

        if y2 < y1:  # Top
            wall = 1
        elif y2 > y1:  # Bottom
            wall = 4
        elif x2 < x1:  # Left
            wall = 8
        elif x2 > x1:  # Right
            wall = 2
        else:
            return

        match cmd:
            case "remove":
                maze_canvas: Any = self.layers.get("maze")
                if self.prev_gen:
                    self.draw_cell_center(maze_canvas, *self.prev_gen)
                self.draw_cell_center(maze_canvas, x1, y1)
                self.draw_cell_center(maze_canvas, x2, y2, step_color)
                self.draw_cell_walls(maze_canvas, x1, y1, wall)
            case "fill":
                path_canvas: Any = self.layers.get("path")
                self.draw_cell_center(
                    path_canvas, x1, y1, step_color & 0x7FFFFFFF
                )
                self.draw_cell_center(path_canvas, x2, y2, step_color)
                self.draw_cell_walls(
                    path_canvas, x1, y1, wall, False, step_color & 0x7FFFFFFF
                )
            case "path_found":
                pass
            case _:
                pass

        self.prev_gen = (x2, y2)

    def draw_endpoints(self) -> None:
        """Draw entry and exit markers on the endpoints layer."""
        canvas: Any = self.layers.get("endpoints")
        self.draw_cell_center(
            canvas,
            self.model.config.entry[1],
            self.model.config.entry[0],
            self.app.colors.get("entry"),
        )
        self.draw_cell_center(
            canvas,
            self.model.config.exit[1],
            self.model.config.exit[0],
            self.app.colors.get("exit"),
        )

    def draw_cell_center(
        self, canvas: Canvas, x: int, y: int, color: int = 0xFF000000
    ) -> None:
        """Draw the interior (center) of one cell."""
        cell: int = self.cell_size
        wall: int = self.wall_size
        canvas.fill_rect(
            x * cell + wall, y * cell + wall, cell - wall, cell - wall, color
        )

    def draw_cell_walls(
        self,
        canvas: Canvas,
        x: int,
        y: int,
        value: int = 0,
        corners: bool = False,
        color: int = 0xFF000000,
    ) -> None:
        """Draw walls of a cell.

        Args:
            canvas: Target canvas.
            x: Column index.
            y: Row index.
            value: Wall bitmask for the cell.
            corners: Whether to include outer corner pixels.
            color: Wall color.
        """
        cell: int = self.cell_size
        wall: int = self.wall_size
        x *= cell
        y *= cell

        TOP: int = 1
        RIGHT: int = 2
        BOTTOM: int = 4
        LEFT: int = 8

        if corners is True:
            if value & TOP:
                canvas.fill_rect(x, y, cell + wall, wall, color)
            if value & BOTTOM:
                canvas.fill_rect(x, y + cell, cell + wall, wall, color)
            if value & RIGHT:
                canvas.fill_rect(x + cell, y, wall, cell + wall, color)
            if value & LEFT:
                canvas.fill_rect(x, y, wall, cell + wall, color)
        else:
            if value & TOP:
                canvas.fill_rect(x + wall, y, cell - wall, wall, color)
            if value & BOTTOM:
                canvas.fill_rect(x + wall, y + cell, cell - wall, wall, color)
            if value & RIGHT:
                canvas.fill_rect(x + cell, y + wall, wall, cell - wall, color)
            if value & LEFT:
                canvas.fill_rect(x, y + wall, wall, cell - wall, color)
