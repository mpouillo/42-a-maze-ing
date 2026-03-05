from collections import deque
from random import randint, seed
from typing import Any, List, Tuple, Optional, Deque, Dict, Generator
from typing import TypeAlias
import numpy as np
from src.models.maze.maze_config import MazeConfig

StepGenerator: TypeAlias = Generator[
    Tuple[np.ndarray, Tuple[int, int]], None, None
]


class MazeGenerator:

    TOP = 1
    RIGHT = 2
    BOTTOM = 4
    LEFT = 8
    FULL = 15

    def __init__(self, config: MazeConfig) -> None:
        self.config = config

        self.height = config.height
        self.width = config.width
        self.entry = config.entry
        self.exit = config.exit
        self.perfect = config.perfect

        if config.seed is not None:
            seed(config.seed)

    def initialize_maze_grid(self) -> None:
        self.maze = np.full((self.height, self.width), 0xF, dtype=np.uint8)

    def initialize_visited(self) -> None:
        self.visited = np.zeros((self.height, self.width), dtype=bool)

    def set_logo_as_visited(self) -> None:
        """Mark logo area as visited so the maze generates around it"""
        with open("src/algo/logo.txt", "r") as f:
            logo = f.read()

        logo_rows = list(logo.strip().split('\n'))
        if not logo_rows:
            return

        center_row = (self.visited.shape[0] - len(logo_rows)) // 2
        center_col = (self.visited.shape[1] - len(logo_rows[0])) // 2

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

    def generate_steps(self) -> StepGenerator:
        self.initialize_maze_grid()
        self.initialize_visited()
        self.set_logo_as_visited()

        if self.visited[self.entry]:
            raise ValueError(f"ENTRY {self.entry} inside the logo area")
        if self.visited[self.exit]:
            raise ValueError(f"EXIT {self.exit} inside the logo area")

        self.visited[self.entry] = True
        stack: List[Tuple[int, int]] = [self.entry]

        yield self.maze, self.entry

        while stack:
            curr_cell = stack.pop()
            neighbors = self.get_unvisited_neighbors(curr_cell)

            if neighbors:
                stack.append(curr_cell)
                next_cell = neighbors[randint(0, len(neighbors) - 1)]

                self.visited[next_cell] = True
                self.remove_wall(curr_cell, next_cell)

                stack.append(next_cell)

                yield self.maze, next_cell

    def generate(self) -> np.ndarray[Any, Any]:
        for _ in self.generate_steps():
            pass
        return self.maze

    def count_walls(self, row: int, col: int,
                    maze: np.ndarray[Any, Any]) -> int:
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

    def close_deadend(
            self, maze: np.ndarray[Any, Any],
            row: int, col: int
    ) -> StepGenerator:
        """Fill a deadend by adding a wall to the only open side"""
        next_cell = (row, col)
        while (
            next_cell != self.entry
            and next_cell != self.exit
            and self.count_walls(next_cell[0], next_cell[1], maze) == 3
        ):
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
            yield maze, (row, col)

    def solve_deadends_steps(
        self
    ) -> StepGenerator:
        """
        Removes dead ends to find the solution.
        """
        maze = self.maze.copy()

        yield maze, self.entry

        while True:
            found_deadend = False
            for row in range(self.height):
                for col in range(self.width):
                    if ((row, col) != self.entry and
                            (row, col) != self.exit and
                            self.count_walls(row, col, maze) == 3):
                        for maze, cell in self.close_deadend(maze, row, col):
                            yield maze, cell
                        found_deadend = True

                        yield maze, (row, col)

            if not found_deadend:
                break

    def solve_deadends(self) -> np.ndarray[Any, Any]:
        """
        Removes dead ends to find the solution.
        """
        last_maze = self.maze.copy()
        for maze_state, _ in self.solve_deadends_steps():
            last_maze = maze_state
        return last_maze

    def add_paths_steps(
        self, solved: np.ndarray[Any, Any], solution_str_len: int
    ) -> StepGenerator:
        row, col = self.entry

        solve_size = max(0, solution_str_len)

        added_path = False
        number_path = 0
        step = 0
        next_pos: Tuple[int, int] = self.entry
        prev: Optional[Tuple[int, int]] = None

        yield self.maze, (row, col)

        while (row, col) != self.exit:
            value: bool = (randint(0, 3) == 0)
            curr = (row, col)

            if not (solved[row, col] & self.TOP) and (row - 1, col) != prev:
                next_pos = (row - 1, col)
            elif not (solved[row, col] & self.RIGHT) and (row, col+1) != prev:
                next_pos = (row, col + 1)
            elif not (solved[row, col] & self.BOTTOM) and (row+1, col) != prev:
                next_pos = (row + 1, col)
            elif not (solved[row, col] & self.LEFT) and (row, col - 1) != prev:
                next_pos = (row, col - 1)

            prev = curr
            row, col = next_pos
            step += 1

            yield self.maze, (row, col)

            if (value is True and added_path is False) or (
                solve_size > 0
                and step == int(solve_size / 2)
                and number_path == 0
            ):
                cell = (row, col)
                blocked_cell = self.get_blocked_cell(solved, cell)
                if blocked_cell is not None:
                    added_path = True
                    self.remove_wall(cell, blocked_cell)
                    number_path += 1
                    yield self.maze, blocked_cell
            else:
                added_path = False

    def add_paths(self, solved: np.ndarray[Any, Any],
                  solution_str_len: int) -> np.ndarray[Any, Any]:
        """Version bloquante qui consomme le générateur"""
        for _ in self.add_paths_steps(solved, solution_str_len):
            pass
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

    def get_neighbors_open(
        self,
        cell: Tuple[int, int],
        solved: np.ndarray[Any, Any],
    ) -> List[Tuple[int, int]]:
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        if (solved[r, c] & self.TOP) == 0 and r > 0:
            neighbors.append((r - 1, c))
        if (solved[r, c] & self.RIGHT) == 0 and c < self.width - 1:
            neighbors.append((r, c + 1))
        if (solved[r, c] & self.BOTTOM) == 0 and r < self.height - 1:
            neighbors.append((r + 1, c))
        if (solved[r, c] & self.LEFT) == 0 and c > 0:
            neighbors.append((r, c - 1))

        return neighbors

    def bfs_steps(
        self, solved: np.ndarray[Any, Any]
    ) -> StepGenerator:
        """
        Yields the maze state at each step of the BFS exploration.
        Allows visualizing the 'wave' of exploration.
        """
        self.initialize_visited()
        self.set_logo_as_visited()

        q: Deque[Tuple[int, int]] = deque()

        # Mark entry as visited and add to queue
        self.visited[self.entry] = True
        q.append(self.entry)

        # Yield initial state
        yield self.maze, self.entry

        while q:
            curr = q.popleft()

            # Yield the current cell being processed (popped from queue)
            yield self.maze, curr

            if curr == self.exit:
                return

            neighbors = self.get_neighbors_open(curr, solved)
            for nxt in neighbors:
                if not self.visited[nxt]:
                    self.visited[nxt] = True
                    q.append(nxt)
                    yield self.maze, nxt

    def bfs(self,
            solved: np.ndarray[Any, Any]) -> Optional[List[Tuple[int, int]]]:
        """
        Standard BFS to find the shortest path from Entry to Exit.
        Returns the path as a list of coordinates.
        """
        self.initialize_visited()
        self.set_logo_as_visited()

        q: Deque[Tuple[int, int]] = deque()
        self.visited[self.entry] = True
        q.append(self.entry)

        # Dictionary to store the path: child -> parent
        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            self.entry: None
        }

        while q:
            curr = q.popleft()

            if curr == self.exit:
                # Reconstruct path by backtracking from Exit to Entry
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
