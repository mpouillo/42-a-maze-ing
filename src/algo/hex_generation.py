from collections import deque
from random import randint
import numpy as np
from typing import Any, List, Tuple, Optional, Deque, Dict
from src.algo.generation import Base


class HexMazeGenerator(Base):
    TOP_RIGHT = 1
    RIGHT = 2
    BOTTOM_RIGHT = 4
    BOTTOM_LEFT = 8
    LEFT = 16
    TOP_LEFT = 32
    FULL = 63

    def __init__(self, config_file: str) -> None:
        super().__init__(config_file)

    def initialize_maze(self) -> None:
        self.maze = np.full((self.height, self.width), 63, dtype=np.uint8)

    def initialize_visited(self) -> None:
        self.visited = np.zeros((self.height, self.width), dtype=bool)

    def apply_logo(self) -> None:
        """Mark logo area as visited so the maze generates around it"""
        with open("src/algo/logo.txt", "r") as f:
            logo = f.read()

        logo_rows = list(logo.strip().split('\n'))
        if not logo_rows:
            return

        center_row = self.visited.shape[0] // 2 - len(logo_rows) // 2
        center_col = self.visited.shape[1] // 2 - len(logo_rows[0]) // 2

        for row in range(0, len(logo_rows)):
            for col in range(0, len(logo_rows[0])):
                if logo_rows[row][col] == '1':
                    self.visited[row + center_row, col + center_col] = True

    def get_unvisited_neighbors(self, cell: Tuple[int, int])\
            -> List[Tuple[int, int]]:
        """Return list of valid unvisited neighbors"""
        r, c = cell
        neighbors = []

        if r % 2 == 0:
            directions = [
                (r - 1, c),      # TOP_RIGHT
                (r, c + 1),      # RIGHT
                (r + 1, c),      # BOTTOM_RIGHT
                (r + 1, c - 1),  # BOTTOM_LEFT
                (r, c - 1),      # LEFT
                (r - 1, c - 1)   # TOP_LEFT
            ]
        else:
            directions = [
                (r - 1, c + 1),  # TOP_RIGHT
                (r, c + 1),      # RIGHT
                (r + 1, c + 1),  # BOTTOM_RIGHT
                (r + 1, c),      # BOTTOM_LEFT
                (r, c - 1),      # LEFT
                (r - 1, c)       # TOP_LEFT
            ]

        for nr, nc in directions:
            if 0 <= nr < self.height and 0 <= nc < self.width:
                if not self.visited[nr, nc]:
                    neighbors.append((nr, nc))

        return neighbors

    def remove_wall(self, current: Tuple[int, int],
                    next_cell: Tuple[int, int]) -> None:
        """Remove walls between two adjacent cells"""
        cr, cc = current
        nr, nc = next_cell
        dr, dc = nr - cr, nc - cc

        if cr % 2 == 0:
            if (dr, dc) == (-1, 0):    # TOP_RIGHT
                self.maze[current] &= 0xFF & ~self.TOP_RIGHT
                self.maze[next_cell] &= 0xFF & ~self.BOTTOM_LEFT
            elif (dr, dc) == (0, 1):   # RIGHT
                self.maze[current] &= 0xFF & ~self.RIGHT
                self.maze[next_cell] &= 0xFF & ~self.LEFT
            elif (dr, dc) == (1, 0):   # BOTTOM_RIGHT
                self.maze[current] &= 0xFF & ~self.BOTTOM_RIGHT
                self.maze[next_cell] &= 0xFF & ~self.TOP_LEFT
            elif (dr, dc) == (1, -1):  # BOTTOM_LEFT
                self.maze[current] &= 0xFF & ~self.BOTTOM_LEFT
                self.maze[next_cell] &= 0xFF & ~self.TOP_RIGHT
            elif (dr, dc) == (0, -1):  # LEFT
                self.maze[current] &= 0xFF & ~self.LEFT
                self.maze[next_cell] &= 0xFF & ~self.RIGHT
            elif (dr, dc) == (-1, -1):  # TOP_LEFT
                self.maze[current] &= 0xFF & ~self.TOP_LEFT
                self.maze[next_cell] &= 0xFF & ~self.BOTTOM_RIGHT
        else:
            if (dr, dc) == (-1, 1):    # TOP_RIGHT
                self.maze[current] &= 0xFF & ~self.TOP_RIGHT
                self.maze[next_cell] &= 0xFF & ~self.BOTTOM_LEFT
            elif (dr, dc) == (0, 1):   # RIGHT
                self.maze[current] &= 0xFF & ~self.RIGHT
                self.maze[next_cell] &= 0xFF & ~self.LEFT
            elif (dr, dc) == (1, 1):   # BOTTOM_RIGHT
                self.maze[current] &= 0xFF & ~self.BOTTOM_RIGHT
                self.maze[next_cell] &= 0xFF & ~self.TOP_LEFT
            elif (dr, dc) == (1, 0):   # BOTTOM_LEFT
                self.maze[current] &= 0xFF & ~self.BOTTOM_LEFT
                self.maze[next_cell] &= 0xFF & ~self.TOP_RIGHT
            elif (dr, dc) == (0, -1):  # LEFT
                self.maze[current] &= 0xFF & ~self.LEFT
                self.maze[next_cell] &= 0xFF & ~self.RIGHT
            elif (dr, dc) == (-1, 0):  # TOP_LEFT
                self.maze[current] &= 0xFF & ~self.TOP_LEFT
                self.maze[next_cell] &= 0xFF & ~self.BOTTOM_RIGHT

    def generate(self) -> np.ndarray[Any, Any]:
        self.initialize_maze()
        self.initialize_visited()
        self.apply_logo()

        if self.visited[self.entry]:
            raise ValueError(f"ENTRY {self.entry} inside the logo area")
        if self.visited[self.exit]:
            raise ValueError(f"EXIT {self.exit} inside the logo area")

        self.visited[self.entry] = True
        stack: List[Tuple[int, int]] = [self.entry]

        while stack:
            curr_cell = stack.pop()
            neighbors = self.get_unvisited_neighbors(curr_cell)

            if neighbors:
                stack.append(curr_cell)
                next_cell = neighbors[randint(0, len(neighbors) - 1)]

                self.visited[next_cell] = True
                self.remove_wall(curr_cell, next_cell)

                stack.append(next_cell)

        return self.maze

    def count_walls(self, row: int, col: int,
                    maze: np.ndarray[Any, Any]) -> int:
        """Count how many walls a specific cell has"""
        cell_val = maze[row, col]
        count = 0
        if cell_val & self.TOP_RIGHT:
            count += 1
        if cell_val & self.RIGHT:
            count += 1
        if cell_val & self.BOTTOM_RIGHT:
            count += 1
        if cell_val & self.BOTTOM_LEFT:
            count += 1
        if cell_val & self.LEFT:
            count += 1
        if cell_val & self.TOP_LEFT:
            count += 1
        return count

    def close_deadend(
        self,
        maze: np.ndarray[Any, Any],
        row: int,
        col: int,
    ) -> None:
        next_cell: Tuple[int, int] = (row, col)

        while (
            next_cell != self.entry
            and next_cell != self.exit
            and self.count_walls(next_cell[0], next_cell[1], maze) == 5
        ):
            row, col = next_cell
            cell_val = int(maze[row, col])

            if row % 2 == 0:
                # Even rows:
                if (cell_val & self.TOP_RIGHT) == 0 and row > 0:
                    maze[row, col] |= self.TOP_RIGHT
                    maze[row - 1, col] |= self.BOTTOM_LEFT
                    next_cell = (row - 1, col)

                elif (cell_val & self.RIGHT) == 0 and col < self.width - 1:
                    maze[row, col] |= self.RIGHT
                    maze[row, col + 1] |= self.LEFT
                    next_cell = (row, col + 1)

                elif (
                    (cell_val & self.BOTTOM_RIGHT) == 0
                    and row < self.height - 1
                ):
                    maze[row, col] |= self.BOTTOM_RIGHT
                    maze[row + 1, col] |= self.TOP_LEFT
                    next_cell = (row + 1, col)

                elif (
                    (cell_val & self.BOTTOM_LEFT) == 0
                    and row < self.height - 1
                    and col > 0
                ):
                    maze[row, col] |= self.BOTTOM_LEFT
                    maze[row + 1, col - 1] |= self.TOP_RIGHT
                    next_cell = (row + 1, col - 1)

                elif (cell_val & self.LEFT) == 0 and col > 0:
                    maze[row, col] |= self.LEFT
                    maze[row, col - 1] |= self.RIGHT
                    next_cell = (row, col - 1)

                elif (cell_val & self.TOP_LEFT) == 0 and row > 0 and col > 0:
                    maze[row, col] |= self.TOP_LEFT
                    maze[row - 1, col - 1] |= self.BOTTOM_RIGHT
                    next_cell = (row - 1, col - 1)
                else:
                    break
            else:
                # Odd rows:
                if (
                    (cell_val & self.TOP_RIGHT) == 0
                    and row > 0
                    and col < self.width - 1
                ):
                    maze[row, col] |= self.TOP_RIGHT
                    maze[row - 1, col + 1] |= self.BOTTOM_LEFT
                    next_cell = (row - 1, col + 1)

                elif (cell_val & self.RIGHT) == 0 and col < self.width - 1:
                    maze[row, col] |= self.RIGHT
                    maze[row, col + 1] |= self.LEFT
                    next_cell = (row, col + 1)

                elif (
                    (cell_val & self.BOTTOM_RIGHT) == 0
                    and row < self.height - 1
                    and col < self.width - 1
                ):
                    maze[row, col] |= self.BOTTOM_RIGHT
                    maze[row + 1, col + 1] |= self.TOP_LEFT
                    next_cell = (row + 1, col + 1)

                elif (
                    (cell_val & self.BOTTOM_LEFT) == 0
                    and row < self.height - 1
                ):
                    maze[row, col] |= self.BOTTOM_LEFT
                    maze[row + 1, col] |= self.TOP_RIGHT
                    next_cell = (row + 1, col)

                elif (cell_val & self.LEFT) == 0 and col > 0:
                    maze[row, col] |= self.LEFT
                    maze[row, col - 1] |= self.RIGHT
                    next_cell = (row, col - 1)

                elif (cell_val & self.TOP_LEFT) == 0 and row > 0:
                    maze[row, col] |= self.TOP_LEFT
                    maze[row - 1, col] |= self.BOTTOM_RIGHT
                    next_cell = (row - 1, col)
                else:
                    break

    def solve_deadends(self) -> np.ndarray[Any, Any]:
        """
        Removes dead ends to find the solution.
        """
        maze = self.maze.copy()
        while True:
            found_deadend = False
            for row in range(self.height):
                for col in range(self.width):
                    if ((row, col) != self.entry and
                            (row, col) != self.exit and
                            self.count_walls(row, col, maze) == 5):
                        self.close_deadend(maze, row, col)
                        found_deadend = True
            if not found_deadend:
                break
        return maze

    def add_paths(
        self,
        solved: np.ndarray[Any, Any],
        file: str,
    ) -> np.ndarray[Any, Any]:
        row, col = self.entry

        with open(file, "r") as f:
            last_line = ""
            for line in f:
                last_line = line

        solve_size = max(0, len(last_line) - 1)
        added_path = False
        number_path = 0
        step = 0
        next_pos: Tuple[int, int] = self.entry
        prev: Optional[Tuple[int, int]] = None

        while (row, col) != self.exit:
            value: bool = (randint(0, 3) == 0)
            curr = (row, col)

            if row % 2 == 0:
                if (
                    (solved[row, col] & self.TOP_RIGHT) == 0
                    and row > 0
                    and (row - 1, col) != prev
                ):
                    next_pos = (row - 1, col)
                elif (
                    (solved[row, col] & self.RIGHT) == 0
                    and col < self.width - 1
                    and (row, col + 1) != prev
                ):
                    next_pos = (row, col + 1)
                elif (
                    (solved[row, col] & self.BOTTOM_RIGHT) == 0
                    and row < self.height - 1
                    and (row + 1, col) != prev
                ):
                    next_pos = (row + 1, col)
                elif (
                    (solved[row, col] & self.BOTTOM_LEFT) == 0
                    and row < self.height - 1
                    and col > 0
                    and (row + 1, col - 1) != prev
                ):
                    next_pos = (row + 1, col - 1)
                elif (
                    (solved[row, col] & self.LEFT) == 0
                    and col > 0
                    and (row, col - 1) != prev
                ):
                    next_pos = (row, col - 1)
                elif (
                    (solved[row, col] & self.TOP_LEFT) == 0
                    and row > 0
                    and col > 0
                    and (row - 1, col - 1) != prev
                ):
                    next_pos = (row - 1, col - 1)
            else:
                if (
                    (solved[row, col] & self.TOP_RIGHT) == 0
                    and row > 0
                    and col < self.width - 1
                    and (row - 1, col + 1) != prev
                ):
                    next_pos = (row - 1, col + 1)
                elif (
                    (solved[row, col] & self.RIGHT) == 0
                    and col < self.width - 1
                    and (row, col + 1) != prev
                ):
                    next_pos = (row, col + 1)
                elif (
                    (solved[row, col] & self.BOTTOM_RIGHT) == 0
                    and row < self.height - 1
                    and col < self.width - 1
                    and (row + 1, col + 1) != prev
                ):
                    next_pos = (row + 1, col + 1)
                elif (
                    (solved[row, col] & self.BOTTOM_LEFT) == 0
                    and row < self.height - 1
                    and (row + 1, col) != prev
                ):
                    next_pos = (row + 1, col)
                elif (
                    (solved[row, col] & self.LEFT) == 0
                    and col > 0
                    and (row, col - 1) != prev
                ):
                    next_pos = (row, col - 1)
                elif (
                    (solved[row, col] & self.TOP_LEFT) == 0
                    and row > 0
                    and (row - 1, col) != prev
                ):
                    next_pos = (row - 1, col)

            prev = curr
            row, col = next_pos
            step += 1

            if (value is True and added_path is False) or (
                solve_size > 0
                and step == solve_size / 2
                and number_path == 0
            ):
                cell = (row, col)
                blocked_cell = self.get_blocked_cell(solved, cell)
                if blocked_cell is not None:
                    added_path = True
                    self.remove_wall(cell, blocked_cell)
                    number_path += 1
            else:
                added_path = False

        return self.maze

    def get_blocked_cell(
        self,
        solved: np.ndarray[Any, Any],
        cell: Tuple[int, int],
    ) -> Optional[Tuple[int, int]]:
        row, col = cell

        def ok(r: int, c: int) -> bool:
            return (
                0 <= r < self.height
                and 0 <= c < self.width
                and self.maze[r, c] != self.FULL
            )

        candidates: List[Tuple[int, int]] = []

        if row % 2 == 0:
            if (
                (solved[row, col] & self.TOP_RIGHT) != 0
                and ok(row - 1, col)
            ):
                candidates.append((row - 1, col))

            if (
                (solved[row, col] & self.RIGHT) != 0
                and ok(row, col + 1)
            ):
                candidates.append((row, col + 1))

            if (
                (solved[row, col] & self.BOTTOM_RIGHT) != 0
                and ok(row + 1, col)
            ):
                candidates.append((row + 1, col))

            if (
                (solved[row, col] & self.BOTTOM_LEFT) != 0
                and ok(row + 1, col - 1)
            ):
                candidates.append((row + 1, col - 1))

            if (
                (solved[row, col] & self.LEFT) != 0
                and ok(row, col - 1)
            ):
                candidates.append((row, col - 1))

            if (
                (solved[row, col] & self.TOP_LEFT) != 0
                and ok(row - 1, col - 1)
            ):
                candidates.append((row - 1, col - 1))
        else:
            if (
                (solved[row, col] & self.TOP_RIGHT) != 0
                and ok(row - 1, col + 1)
            ):
                candidates.append((row - 1, col + 1))

            if (
                (solved[row, col] & self.RIGHT) != 0
                and ok(row, col + 1)
            ):
                candidates.append((row, col + 1))

            if (
                (solved[row, col] & self.BOTTOM_RIGHT) != 0
                and ok(row + 1, col + 1)
            ):
                candidates.append((row + 1, col + 1))

            if (
                (solved[row, col] & self.BOTTOM_LEFT) != 0
                and ok(row + 1, col)
            ):
                candidates.append((row + 1, col))

            if (
                (solved[row, col] & self.LEFT) != 0
                and ok(row, col - 1)
            ):
                candidates.append((row, col - 1))

            if (
                (solved[row, col] & self.TOP_LEFT) != 0
                and ok(row - 1, col)
            ):
                candidates.append((row - 1, col))

        if not candidates:
            return None

        return candidates[randint(0, len(candidates) - 1)]

    def get_neighbors_open(
        self,
        cell: Tuple[int, int],
        solved: np.ndarray[Any, Any],
    ) -> List[Tuple[int, int]]:
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        if r % 2 == 0:
            if (solved[r, c] & self.TOP_RIGHT) == 0 and r > 0:
                neighbors.append((r - 1, c))

            if (
                (solved[r, c] & self.RIGHT) == 0
                and c < self.width - 1
            ):
                neighbors.append((r, c + 1))

            if (
                (solved[r, c] & self.BOTTOM_RIGHT) == 0
                and r < self.height - 1
            ):
                neighbors.append((r + 1, c))

            if (
                (solved[r, c] & self.BOTTOM_LEFT) == 0
                and r < self.height - 1
                and c > 0
            ):
                neighbors.append((r + 1, c - 1))

            if (solved[r, c] & self.LEFT) == 0 and c > 0:
                neighbors.append((r, c - 1))

            if (
                (solved[r, c] & self.TOP_LEFT) == 0
                and r > 0
                and c > 0
            ):
                neighbors.append((r - 1, c - 1))
        else:
            if (
                (solved[r, c] & self.TOP_RIGHT) == 0
                and r > 0
                and c < self.width - 1
            ):
                neighbors.append((r - 1, c + 1))

            if (
                (solved[r, c] & self.RIGHT) == 0
                and c < self.width - 1
            ):
                neighbors.append((r, c + 1))

            if (
                (solved[r, c] & self.BOTTOM_RIGHT) == 0
                and r < self.height - 1
                and c < self.width - 1
            ):
                neighbors.append((r + 1, c + 1))

            if (
                (solved[r, c] & self.BOTTOM_LEFT) == 0
                and r < self.height - 1
            ):
                neighbors.append((r + 1, c))

            if (solved[r, c] & self.LEFT) == 0 and c > 0:
                neighbors.append((r, c - 1))

            if (solved[r, c] & self.TOP_LEFT) == 0 and r > 0:
                neighbors.append((r - 1, c))

        return neighbors

    def bfs(self,
            solved: np.ndarray[Any, Any]) -> Optional[List[Tuple[int, int]]]:
        self.initialize_visited()
        self.apply_logo()

        q: Deque[Tuple[int, int]] = deque()
        self.visited[self.entry] = True
        q.append(self.entry)

        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            self.entry: None
        }
        while q:
            curr = q.popleft()

            if curr == self.exit:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = curr
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path

            for nxt in self.get_neighbors_open(curr, solved):
                if not self.visited[nxt]:
                    self.visited[nxt] = True
                    parent[nxt] = curr
                    q.append(nxt)
        return None
