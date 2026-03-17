from collections import deque
from heapq import heappush, heappop
from random import randint, seed
import numpy as np
from typing import Any, List, Tuple, Optional, Dict, Generator, Set
from src.maze.maze_config import MazeConfig


class HexGenerator:
    TOP_RIGHT = 1
    RIGHT = 2
    BOTTOM_RIGHT = 4
    BOTTOM_LEFT = 8
    LEFT = 16
    TOP_LEFT = 32
    FULL = 63

    def __init__(self, config: MazeConfig) -> None:
        self.config = config

        self.config.height = config.height
        self.config.width = config.width
        self.config.entry = config.entry
        self.config.exit = config.exit
        self.config.perfect = config.perfect

        # format: (dr, dc): (current_mask, neighbor_mask)
        self._even_neighbors = {
            (-1, 0): (self.TOP_RIGHT, self.BOTTOM_LEFT),
            (0, 1): (self.RIGHT, self.LEFT),
            (1, 0): (self.BOTTOM_RIGHT, self.TOP_LEFT),
            (1, -1): (self.BOTTOM_LEFT, self.TOP_RIGHT),
            (0, -1): (self.LEFT, self.RIGHT),
            (-1, -1): (self.TOP_LEFT, self.BOTTOM_RIGHT),
        }

        self._odd_neighbors = {
            (-1, 1): (self.TOP_RIGHT, self.BOTTOM_LEFT),
            (0, 1): (self.RIGHT, self.LEFT),
            (1, 1): (self.BOTTOM_RIGHT, self.TOP_LEFT),
            (1, 0): (self.BOTTOM_LEFT, self.TOP_RIGHT),
            (0, -1): (self.LEFT, self.RIGHT),
            (-1, 0): (self.TOP_LEFT, self.BOTTOM_RIGHT),
        }

    def initialize_maze(self) -> None:
        if self.config.seed is not None:
            seed(self.config.seed)
        self.maze = np.full(
            (self.config.height, self.config.width), 0x3F, dtype=np.uint8
        )

    def initialize_visited(self) -> None:
        self.visited = np.zeros(
            (self.config.height, self.config.width), dtype=bool
        )

    def set_logo_as_visited(self) -> None:
        """Mark logo area as visited so the maze generates around it"""
        try:
            with open("src/maze/logo.txt", "r") as f:
                logo_rows = [line for line in f.read().splitlines()
                             if line.strip()]
        except FileNotFoundError:
            return

        if not logo_rows:
            return

        center_row = (self.visited.shape[0] - len(logo_rows)) // 2
        center_col = (self.visited.shape[1] - len(logo_rows[0])) // 2

        for row in range(len(logo_rows)):
            for col in range(len(logo_rows[0])):
                if logo_rows[row][col] == "1":
                    self.visited[row + center_row, col + center_col] = True

    def get_unvisited_neighbors(
        self, cell: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Return list of valid unvisited neighbors"""
        r, c = cell
        neighbors = []

        offsets = self._even_neighbors if r % 2 == 0 else self._odd_neighbors

        for dr, dc in offsets.keys():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.config.height and 0 <= nc < self.config.width:
                if not self.visited[nr, nc]:
                    neighbors.append((nr, nc))

        return neighbors

    def remove_wall(
        self, current: Tuple[int, int], next_cell: Tuple[int, int]
    ) -> None:
        """Remove walls between two adjacent cells"""
        cr, cc = current
        nr, nc = next_cell
        dr, dc = nr - cr, nc - cc

        offsets = self._even_neighbors if cr % 2 == 0 else self._odd_neighbors

        if (dr, dc) in offsets:
            curr_mask, next_mask = offsets[(dr, dc)]
            self.maze[current] &= 0xFF & ~curr_mask
            self.maze[next_cell] &= 0xFF & ~next_mask

    def generate_steps(self) -> Generator[Any, None, None]:
        self.initialize_maze()
        self.initialize_visited()
        self.set_logo_as_visited()

        if self.visited[self.config.entry]:
            raise ValueError(f"ENTRY {self.config.entry} inside the logo area")
        if self.visited[self.config.exit]:
            raise ValueError(f"EXIT {self.config.exit} inside the logo area")

        self.visited[self.config.entry] = True
        stack: List[Tuple[int, int]] = [self.config.entry]

        while stack:
            curr_cell = stack.pop()
            neighbors = self.get_unvisited_neighbors(curr_cell)

            if neighbors:
                stack.append(curr_cell)
                next_cell = neighbors[randint(0, len(neighbors) - 1)]

                self.visited[next_cell] = True
                self.remove_wall(curr_cell, next_cell)
                stack.append(next_cell)

                yield self.maze, ("remove", curr_cell, next_cell)

    def generate(self) -> np.ndarray[Any, Any]:
        """Blocking generation (consumes the steps generator)"""
        for _ in self.generate_steps():
            pass
        return self.maze

    def count_walls(
        self, row: int, col: int, maze: np.ndarray[Any, Any]
    ) -> int:
        """Count how many walls a specific cell has"""
        cell_val = maze[row, col]
        # Count set bits efficiently
        return bin(cell_val & self.FULL).count("1")

    def close_deadend(
        self,
        maze: np.ndarray[Any, Any],
        row: int,
        col: int,
    ) -> Generator[Any, None, None]:
        next_cell: Tuple[int, int] = (row, col)

        while (
            next_cell != self.config.entry
            and next_cell != self.config.exit
            and self.count_walls(next_cell[0], next_cell[1], maze) == 5
        ):
            row, col = next_cell
            cell_val = int(maze[row, col])

            # Find the single open direction to backtrack
            offsets = (
                self._even_neighbors if row % 2 == 0 else self._odd_neighbors
            )
            found_open = False

            for (dr, dc), (mask, neighbor_mask) in offsets.items():
                if (cell_val & mask) == 0:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.config.height and (
                        0 <= nc < self.config.width
                    ):
                        maze[row, col] |= mask
                        maze[nr, nc] |= neighbor_mask
                        next_cell = (nr, nc)
                        found_open = True
                        yield maze, (row, col)
                        break

            if not found_open:
                break

    def solve_deadends_steps(self) -> Generator[Any, None, None]:
        """
        Yields map state while removing dead ends.
        """
        maze = self.maze.copy()

        yield maze, self.config.entry

        while True:
            found_deadend = False
            for row in range(self.config.height):
                for col in range(self.config.width):
                    if (
                        (row, col) != self.config.entry
                        and (row, col) != self.config.exit
                        and self.count_walls(row, col, maze) == 5
                    ):
                        for maze, cell in self.close_deadend(maze, row, col):
                            yield maze, cell
                        found_deadend = True
                        yield maze, (row, col)

            if not found_deadend:
                break

    def solve_deadends(self) -> np.ndarray[Any, Any]:
        """Blocking version that consumes the steps generator"""
        last_maze = self.maze.copy()
        for maze_state, _ in self.solve_deadends_steps():
            last_maze = maze_state
        return last_maze

    def add_paths_steps(
        self,
        solved: np.ndarray[Any, Any],
        solution_str_len: int,
    ) -> Generator[Any, None, None]:

        row, col = self.config.entry
        solve_size = max(0, solution_str_len)
        added_path = False
        number_path = 0
        step = 0
        next_pos: Tuple[int, int] = self.config.entry
        prev: Optional[Tuple[int, int]] = None

        while (row, col) != self.config.exit:
            value: bool = randint(0, 3) == 0

            offsets = (
                self._even_neighbors if row % 2 == 0 else self._odd_neighbors
            )
            next_pos = (row, col)

            current_solved_val = int(solved[row, col])

            # Find next step in solved path
            for (dr, dc), (mask, _) in offsets.items():
                nr, nc = row + dr, col + dc
                if (current_solved_val & mask) == 0:
                    if (
                        0 <= nr < self.config.height
                        and 0 <= nc < self.config.width
                    ):
                        if (nr, nc) != prev:
                            next_pos = (nr, nc)
                            break

            prev = (row, col)
            row, col = next_pos
            step += 1

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
                    yield self.maze, ("remove", cell, blocked_cell)
            else:
                added_path = False

    def add_paths(
        self,
        solved: np.ndarray[Any, Any],
        solution_str_len: int,
    ) -> np.ndarray[Any, Any]:
        """Blocking version that consumes the steps generator"""
        for _ in self.add_paths_steps(solved, solution_str_len):
            pass
        return self.maze

    def get_blocked_cell(
        self,
        solved: np.ndarray[Any, Any],
        cell: Tuple[int, int],
    ) -> Optional[Tuple[int, int]]:
        row, col = cell
        candidates: List[Tuple[int, int]] = []

        offsets = self._even_neighbors if row % 2 == 0 else self._odd_neighbors

        cell_val = int(solved[row, col])

        for (dr, dc), (mask, _) in offsets.items():
            # If there IS a wall in the solved maze (deadend or boundary),
            # maybe we can open it to creating a loop?
            if (cell_val & mask) != 0:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.config.height and (
                    0 <= nc < self.config.width
                ):
                    if self.maze[nr, nc] != self.FULL:
                        candidates.append((nr, nc))

        if not candidates:
            return None

        return candidates[randint(0, len(candidates) - 1)]

    def get_neighbors_open(
        self,
        cell: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        offsets = self._even_neighbors if r % 2 == 0 else self._odd_neighbors
        cell_val = int(self.maze[r, c])

        for (dr, dc), (mask, _) in offsets.items():
            if (cell_val & mask) == 0:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.config.height and (
                    0 <= nc < self.config.width
                ):
                    neighbors.append((nr, nc))

        return neighbors

    def bfs(self, max_paths: int = 999) -> Generator[Any, None, None]:
        self.initialize_visited()
        self.set_logo_as_visited()
        self.bfs_paths = []

        discovered = {self.config.entry}
        q = deque([(self.config.entry, [self.config.entry])])

        while q:
            curr, path = q.popleft()

            if curr == self.config.exit:
                self.bfs_paths.append(path)
                if len(self.bfs_paths) >= max_paths:
                    return
                continue

            for nxt in self.get_neighbors_open(curr):
                if nxt not in discovered:
                    discovered.add(nxt)
                    yield ("fill", curr, nxt)
                if nxt not in path:
                    q.append((nxt, path + [nxt]))

    def get_neighbors_open_opti(
        self,
        cell: Tuple[int, int],
        maze: np.ndarray[Any, Any],
    ) -> List[Tuple[int, int]]:
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        offsets = self._even_neighbors if r % 2 == 0 else self._odd_neighbors
        cell_val = int(maze[r, c])

        for (dr, dc), (mask, _) in offsets.items():
            if (cell_val & mask) == 0:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.config.height and (
                    0 <= nc < self.config.width
                ):
                    neighbors.append((nr, nc))
        return neighbors

    def _heuristic(self, cell: Tuple[int, int]) -> int:
        """Manhattan distance to exit."""
        return abs(cell[0] - self.config.exit[0]) + abs(
            cell[1] - self.config.exit[1]
        )

    def bfs_opti(self) -> Generator[Any, None, None]:
        self.initialize_visited()
        self.set_logo_as_visited()
        self.bfs_paths = []
        maze = self.solve_deadends()

        for step in self.multi_path_search(maze):
            yield step

    def _astar_with_forbidden_steps(
        self,
        maze: np.ndarray[Any, Any],
        out_path: List[List[Tuple[int, int]]],
    ) -> Generator[Any, None, None]:
        exit_ = self.config.exit
        start = self.config.entry

        open_heap: List[Any] = []
        heappush(open_heap, (self._heuristic(start), 0, start, None))

        g_best: Dict[Tuple[int, int], int] = {start: 0}
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

        while open_heap:
            _, g, curr, parent = heappop(open_heap)

            if curr in came_from:
                continue
            came_from[curr] = parent

            if curr == exit_:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = exit_
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                out_path.append(path)
                return

            for nxt in self.get_neighbors_open_opti(curr, maze):
                if nxt in came_from:
                    continue
                new_g = g + 1
                if new_g < g_best.get(nxt, 10**9):
                    g_best[nxt] = new_g
                    f_cost = new_g + self._heuristic(nxt)
                    heappush(open_heap, (f_cost, new_g, nxt, curr))
                    yield ("fill", curr, nxt)

    def _astar_longest_steps(
        self,
        maze: np.ndarray[Any, Any],
        out_path: List[List[Tuple[int, int]]],
    ) -> Generator[Any, None, None]:
        exit_ = self.config.exit
        start = self.config.entry

        open_heap: List[Any] = []
        heappush(open_heap, (0, start, None))

        g_best: Dict[Tuple[int, int], int] = {start: 0}
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

        while open_heap:
            neg_g, curr, parent = heappop(open_heap)

            if curr in came_from:
                continue
            came_from[curr] = parent

            if curr == exit_:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = exit_
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                out_path.append(path)
                return

            for nxt in self.get_neighbors_open_opti(curr, maze):
                if nxt in came_from:
                    continue
                new_neg_g = neg_g - 1
                if new_neg_g < g_best.get(nxt, 1):
                    g_best[nxt] = new_neg_g
                    heappush(open_heap, (new_neg_g, nxt, curr))
                    yield ("fill", curr, nxt)

    def _astar_target_length_steps(
        self,
        maze: np.ndarray[Any, Any],
        target_len: int,
        exclude: Set[Tuple[Tuple[int, int], ...]],
        out_path: List[List[Tuple[int, int]]],
    ) -> Generator[Any, None, None]:
        exit_ = self.config.exit
        start = self.config.entry

        open_heap: List[
            Tuple[int, int, Tuple[int, int], Optional[Tuple[int, int]]]
        ] = []
        heappush(
            open_heap,
            (abs(target_len - self._heuristic(start)), 0, start, None),
        )

        g_best: Dict[Tuple[int, int], int] = {start: 0}
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

        best_path: Optional[List[Tuple[int, int]]] = None
        best_deviation = 10**9

        while open_heap:
            _, g, curr, parent = heappop(open_heap)

            if curr in came_from:
                continue
            came_from[curr] = parent

            if curr == exit_:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = exit_
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()

                key = tuple(path)
                deviation = abs(len(path) - target_len)
                if key not in exclude and deviation < best_deviation:
                    best_deviation = deviation
                    best_path = path
                if deviation == 0:
                    break
                continue

            for nxt in self.get_neighbors_open_opti(curr, maze):
                if nxt in came_from:
                    continue
                new_g = g + 1
                if new_g < g_best.get(nxt, 10**9):
                    g_best[nxt] = new_g
                    estimated_total = new_g + self._heuristic(nxt)
                    deviation = abs(estimated_total - target_len)
                    heappush(open_heap, (deviation, new_g, nxt, curr))
                    yield ("fill", curr, nxt)

        if best_path is not None:
            out_path.append(best_path)

    def multi_path_search(
        self,
        maze: np.ndarray[Any, Any],
    ) -> Generator[Any, None, None]:
        self.bfs_paths = []
        exclude: Set[Tuple[Tuple[int, int], ...]] = set()

        first_out: List[List[Tuple[int, int]]] = []
        for step in self._astar_with_forbidden_steps(maze, first_out):
            yield step

        if first_out:
            first = first_out[0]
            self.bfs_paths.append(first)
            exclude.add(tuple(first))

        longest_out: List[List[Tuple[int, int]]] = []
        for step in self._astar_longest_steps(maze, longest_out):
            yield step

        longest = None
        if longest_out and tuple(longest_out[0]) not in exclude:
            longest = longest_out[0]
            exclude.add(tuple(longest))

        if longest is not None:
            shortest_len = len(first)
            longest_len = len(longest)
            length_range = longest_len - shortest_len

            if length_range > 0:
                percentiles = [0.25, 0.50, 0.75]
                targets = [
                    int(shortest_len + p * length_range) for p in percentiles
                ]
                for target in targets:
                    path_out: List[List[Tuple[int, int]]] = []
                    for step in self._astar_target_length_steps(
                        maze, target, exclude, path_out
                    ):
                        yield step

                    if path_out:
                        path = path_out[0]
                        self.bfs_paths.append(path)
                        exclude.add(tuple(path))

            self.bfs_paths.append(longest)
