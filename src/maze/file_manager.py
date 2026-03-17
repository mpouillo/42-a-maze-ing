import numpy as np
from typing import List, Tuple, Optional, Any
from src.maze.maze_config import MazeConfig


class MazeFileManager:
    def __init__(self, config: MazeConfig):
        self.config = config

    def write_maze(self, file_path: str, maze: np.ndarray[Any, Any]) -> None:
        """Writes the maze grid and entry/exit points to the file."""
        with open(file_path, "w") as f:
            if self.config.is_hex:
                for row in maze:
                    line = "".join(format(int(c) & 0x3F, "02X") for c in row)
                    f.write(line + "\n")
            else:
                for row in maze:
                    line = "".join(format(int(c) & 0xF, "X") for c in row)
                    f.write(line + "\n")

            f.write("\n")
            f.write(str(self.config.entry).strip("()"))
            f.write("\n")
            f.write(str(self.config.exit).strip("()"))
            f.write("\n")

    def append_solution(self, file_path: str, solution_str: str) -> None:
        """Appends a solution string to the file."""
        if solution_str:
            with open(file_path, "a") as f:
                f.write(solution_str)

    def resolve_to_string(
        self, maze: np.ndarray[Any, Any], maze_gen_instance: Any
    ) -> str:
        """
        Returns the solution string.
        """
        if self.config.is_hex:
            return self._resolve_hex(maze, maze_gen_instance)
        else:
            return self._resolve_rect(maze)

    def path_to_string(self, path: Optional[List[Tuple[int, int]]]) -> str:
        """
        Converts a list of coordinates into a direction string (NESW or ABCDEF)
        """
        if not path or len(path) < 2:
            return ""

        result = []
        if self.config.is_hex:
            row, col = path[0]
            for nxt in path[1:]:
                direction = self._get_hex_direction((row, col), nxt)
                if direction:
                    result.append(direction)
                row, col = nxt
        else:
            for (r1, c1), (r2, c2) in zip(path, path[1:]):
                dr, dc = r2 - r1, c2 - c1
                if dr == -1 and dc == 0:
                    result.append("N")
                elif dr == 1 and dc == 0:
                    result.append("S")
                elif dr == 0 and dc == 1:
                    result.append("E")
                elif dr == 0 and dc == -1:
                    result.append("W")

        return "".join(result)

    # --- Private Helpers ---

    def _resolve_rect(self, maze: np.ndarray[Any, Any]) -> str:
        row, col = self.config.entry
        prev: Optional[Tuple[int, int]] = None
        path_chars = []

        TOP, RIGHT, BOTTOM, LEFT = 1, 2, 4, 8

        while (row, col) != self.config.exit:

            # Check North (Top) - Bit 0
            if not (maze[row, col] & TOP) and (row - 1, col) != prev:
                prev = (row, col)
                row -= 1
                path_chars.append("N")
                continue

            # Check East (Right) - Bit 1
            elif not (maze[row, col] & RIGHT) and (row, col + 1) != prev:
                prev = (row, col)
                col += 1
                path_chars.append("E")
                continue

            # Check South (Bottom) - Bit 2
            elif not (maze[row, col] & BOTTOM) and (row + 1, col) != prev:
                prev = (row, col)
                row += 1
                path_chars.append("S")
                continue

            # Check West (Left) - Bit 3
            elif not (maze[row, col] & LEFT) and (row, col - 1) != prev:
                prev = (row, col)
                col -= 1
                path_chars.append("W")
                continue

            break

        return "".join(path_chars)

    def _resolve_hex(self, maze: np.ndarray[Any, Any], gen: Any) -> str:
        row, col = self.config.entry
        prev: Optional[Tuple[int, int]] = None
        path_chars = []

        while (row, col) != self.config.exit:
            curr = (row, col)
            val = int(maze[row, col])

            # Hex logic relies on even/odd rows.
            # We map specific conditions to helper functions to reduce nesting.

            next_step = self._get_next_hex_step(row, col, val, prev, gen)

            if next_step:
                new_row, new_col, char = next_step
                prev = curr
                row, col = new_row, new_col
                path_chars.append(char)
            else:
                break

        return "".join(path_chars)

    def _get_next_hex_step(
        self,
        row: int,
        col: int,
        val: int,
        prev: Optional[Tuple[int, int]],
        gen: Any,
    ) -> Optional[Tuple[int, int, str]]:
        """Determines the next step for Hex maze based
        on walls and previous position."""

        # Define neighbor offsets and wall masks based on generator constants
        # Assuming gen has attributes: TOP_RIGHT, RIGHT, BOTTOM_RIGHT,
        # BOTTOM_LEFT, LEFT, TOP_LEFT

        is_even = row % 2 == 0

        # Directions: (d_row, d_col, wall_mask, char_code)
        if is_even:
            moves = [
                (-1, 0, gen.TOP_RIGHT, "A"),
                (0, 1, gen.RIGHT, "B"),
                (1, 0, gen.BOTTOM_RIGHT, "C"),
                (1, -1, gen.BOTTOM_LEFT, "D"),
                (0, -1, gen.LEFT, "E"),
                (-1, -1, gen.TOP_LEFT, "F"),
            ]
        else:
            moves = [
                (-1, 1, gen.TOP_RIGHT, "A"),
                (0, 1, gen.RIGHT, "B"),
                (1, 1, gen.BOTTOM_RIGHT, "C"),
                (1, 0, gen.BOTTOM_LEFT, "D"),
                (0, -1, gen.LEFT, "E"),
                (-1, 0, gen.TOP_LEFT, "F"),
            ]

        for dr, dc, mask, char in moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < gen.config.height and 0 <= nc < gen.config.width:
                if (val & mask) == 0 and (nr, nc) != prev:
                    return (nr, nc, char)

        return None

    def _get_hex_direction(
        self, curr: Tuple[int, int], nxt: Tuple[int, int]
    ) -> str:
        """Helper to find direction char between two hex cells"""
        r, c = curr
        nr, nc = nxt

        if r % 2 == 0:
            if (nr, nc) == (r - 1, c):
                return "A"
            if (nr, nc) == (r, c + 1):
                return "B"
            if (nr, nc) == (r + 1, c):
                return "C"
            if (nr, nc) == (r + 1, c - 1):
                return "D"
            if (nr, nc) == (r, c - 1):
                return "E"
            if (nr, nc) == (r - 1, c - 1):
                return "F"
        else:
            if (nr, nc) == (r - 1, c + 1):
                return "A"
            if (nr, nc) == (r, c + 1):
                return "B"
            if (nr, nc) == (r + 1, c + 1):
                return "C"
            if (nr, nc) == (r + 1, c):
                return "D"
            if (nr, nc) == (r, c - 1):
                return "E"
            if (nr, nc) == (r - 1, c):
                return "F"
        return ""
