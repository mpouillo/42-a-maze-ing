from collections import deque
from random import randint, seed
import numpy as np
from dotenv import load_dotenv
import os
from typing import Any, List, Tuple, Optional, Deque, Dict


class MazeGenerator:

    TOP = 1
    RIGHT = 2
    BOTTOM = 4
    LEFT = 8
    FULL = 15

    def __init__(self, config_file: str) -> None:
        self.load_config(config_file)
        seed(self.seed)

    def load_config(self, config_file: str) -> None:
        load_dotenv(config_file)

        self.height = int(str(os.environ.get("HEIGHT")))
        self.width = int(str(os.environ.get("WIDTH")))

        if self.height <= 0 or self.width <= 0:
            raise ValueError(
                "HEIGHT and WIDTH must be positive"
            )

        if self.height < 7 or self.width < 9:
            raise ValueError(
                "Maze must be at least 7x9"
            )

        entry_str = str(os.environ.get("ENTRY")).strip().split(',')
        if len(entry_str) != 2:
            raise ValueError("ENTRY must be 'row,col'")
        self.entry = (int(entry_str[0]), int(entry_str[1]))

        exit_str = str(os.environ.get("EXIT")).strip().split(',')
        if len(exit_str) != 2:
            raise ValueError("EXIT must be 'row,col'")
        self.exit = (int(exit_str[0]), int(exit_str[1]))

        try:
            seed = str(os.environ.get("SEED"))
            self.seed = int(seed)
        except Exception:
            self.seed = None

        erow, ecol = self.entry
        xrow, xcol = self.exit

        if self.entry == self.exit:
            raise ValueError(
                "The ENTRY can't be at the same place as the EXIT"
            )
        if not (0 <= erow < self.height and 0 <= ecol < self.width):
            raise ValueError(
                f"ENTRY {self.entry} is outside maze bounds "
            )
        if not (0 <= xrow < self.height and 0 <= xcol < self.width):
            raise ValueError(
                f"EXIT {self.exit} is outside maze bounds "
            )

        perfect: str = str(os.environ.get("PERFECT"))
        if perfect == "False" or perfect == "0":
            self.perfect: bool = False
        elif perfect == "True" or perfect == "1":
            self.perfect = True
        else:
            raise ValueError(
                "PERFECT is not a bool : True or False"
            )

    def initialize_maze(self) -> None:
        self.maze = np.full((self.height, self.width), 15, dtype=np.uint8)

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
        row, col = cell
        neighbors = []

        # Up
        if row > 0 and not self.visited[row - 1, col]:
            neighbors.append((row - 1, col))
        # Down
        if row < self.height - 1 and not self.visited[row + 1, col]:
            neighbors.append((row + 1, col))
        # Left
        if col > 0 and not self.visited[row, col - 1]:
            neighbors.append((row, col - 1))
        # Right
        if col < self.width - 1 and not self.visited[row, col + 1]:
            neighbors.append((row, col + 1))

        return neighbors

    def remove_wall(self, current: Tuple[int, int],
                    next_cell: Tuple[int, int]) -> None:
        """Remove walls between two adjacent cells"""
        cr, cc = current
        nr, nc = next_cell

        if nr < cr:
            self.maze[current] &= 0XFF & ~self.TOP
            self.maze[next_cell] &= 0XFF & ~self.BOTTOM
        elif nr > cr:
            self.maze[current] &= 0XFF & ~self.BOTTOM
            self.maze[next_cell] &= 0XFF & ~self.TOP
        elif nc < cc:
            self.maze[current] &= 0XFF & ~self.LEFT
            self.maze[next_cell] &= 0XFF & ~self.RIGHT
        elif nc > cc:
            self.maze[current] &= 0XFF & ~self.RIGHT
            self.maze[next_cell] &= 0XFF & ~self.LEFT

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

    def count_walls(self, row: int, col: int, maze) -> int:
        """Count how many walls a specific cell has"""
        cell_val = maze[row, col]
        count = 0
        if cell_val & self.TOP:
            count += 1
        if cell_val & self.RIGHT:
            count += 1
        if cell_val & self.BOTTOM:
            count += 1
        if cell_val & self.LEFT:
            count += 1
        return count

    def close_deadend(self, maze, row: int, col: int) -> None:
        """Fill a deadend by adding a wall to the only open side"""
        next_cell = (row, col)
        # If TOP is open, close it (add TOP wall)
        # and add BOTTOM wall to the neighbor above
        while (next_cell != self.entry and
               next_cell != self.exit and
               self.count_walls(next_cell[0], next_cell[1], maze)) == 3:

            row, col = next_cell
            cell_val = maze[row, col]

            if not (cell_val & self.TOP):
                maze[row, col] |= self.TOP
                if row > 0:
                    maze[row - 1, col] |= self.BOTTOM
                    next_cell = (row - 1, col)

            elif not (cell_val & self.RIGHT):
                maze[row, col] |= self.RIGHT
                if col < self.width - 1:
                    maze[row, col + 1] |= self.LEFT
                    next_cell = (row, col + 1)

            elif not (cell_val & self.BOTTOM):
                maze[row, col] |= self.BOTTOM
                if row < self.height - 1:
                    maze[row + 1, col] |= self.TOP
                    next_cell = (row + 1, col)

            elif not (cell_val & self.LEFT):
                maze[row, col] |= self.LEFT
                if col > 0:
                    maze[row, col - 1] |= self.RIGHT
                    next_cell = (row, col - 1)

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
                            self.count_walls(row, col, maze) == 3):
                        self.close_deadend(maze, row, col)
                        found_deadend = True
            if not found_deadend:
                break
        return maze

    def add_paths(self, solved, filename) -> np.ndarray[Any, Any]:
        row, col = self.entry

        with open(filename, "r") as f:
            last_line = ""
            for line in f:
                last_line = line

        solve_size = max(0, len(last_line) - 1)
        added_path = False
        number_path = 0
        step = 0
        next_pos = self.entry
        prev = None

        while (row, col) != self.exit:

            value: bool = (randint(0, 3) == 0)
            curr = (row, col)

            if not (solved[row, col] & self.TOP) and (row-1, col) != prev:
                next_pos = (row - 1, col)
            elif not (solved[row, col] & self.RIGHT) and (row, col+1) != prev:
                next_pos = (row, col + 1)
            elif not (solved[row, col] & self.BOTTOM) and (row+1, col) != prev:
                next_pos = (row + 1, col)
            elif not (solved[row, col] & self.LEFT) and (row, col-1) != prev:
                next_pos = (row, col - 1)

            prev = curr
            row, col = next_pos
            step += 1

            if (value is True and added_path is False) or (
                solve_size > 0 and step == solve_size / 2 and number_path == 0
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

    def get_blocked_cell(self, solved, cell) -> Tuple | None:

        row, col = cell

        def ok(row: int, col: int) -> bool:
            return (0 <= row < self.height and 0 <= col < self.width and
                    self.maze[row, col] != self.FULL)
        candidates: List[Tuple[int, int]] = []
        if (solved[row, col] & self.TOP) and ok(row - 1, col):
            candidates.append((row - 1, col))

        if (solved[row, col] & self.RIGHT) and ok(row, col + 1):
            candidates.append((row, col + 1))

        if (solved[row, col] & self.BOTTOM) and ok(row + 1, col):
            candidates.append((row + 1, col))

        if (solved[row, col] & self.LEFT) and ok(row, col - 1):
            candidates.append((row, col - 1))

        if not candidates:
            return None

        return candidates[randint(0, len(candidates) - 1)]

    def get_neighbors_open(self, cell: Tuple[int, int], solved):
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        # TOP
        if (solved[r, c] & self.TOP) == 0 and r > 0:
            neighbors.append((r - 1, c))
        # RIGHT
        if (solved[r, c] & self.RIGHT) == 0 and c < self.width - 1:
            neighbors.append((r, c + 1))
        # BOTTOM
        if (solved[r, c] & self.BOTTOM) == 0 and r < self.height - 1:
            neighbors.append((r + 1, c))
        # LEFT
        if (solved[r, c] & self.LEFT) == 0 and c > 0:
            neighbors.append((r, c - 1))

        return neighbors

    def bfs(self, solved):
        self.initialize_visited()
        self.apply_logo()

        q: Deque[Tuple[int, int]] = deque()
        self.visited[self.entry] = True
        q.append(self.entry)

        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            self.entry: None}
        while q:
            curr = q.popleft()

            if curr == self.exit:
                path = []
                node = curr
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
