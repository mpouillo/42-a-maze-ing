from collections import deque
from heapq import heappush, heappop
from random import randint, seed
from typing import Any, List, Tuple, Optional, Deque, Dict, Generator, Set
from typing import TypeAlias
import numpy as np
from collections import deque, defaultdict
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

        self.config.height = config.height
        self.config.width = config.width

        self.config.entry = config.entry
        self.config.exit = config.exit
        self.config.perfect = config.perfect

        if config.seed is not None:
            seed(config.seed)

    def initialize_maze(self) -> None:
        self.maze = np.full((self.config.height, self.config.width),
                            0xF, dtype=np.uint8)

    def initialize_visited(self) -> None:
        self.visited = np.zeros((self.config.height, self.config.width),
                                dtype=bool)

    def set_logo_as_visited(self) -> None:
        """Mark logo area as visited so the maze generates around it"""
        with open("src/models/maze/logo.txt", "r") as f:
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
        if row < self.config.height - 1 and not self.visited[row + 1, col]:
            neighbors.append((row + 1, col))
        # Left
        if col > 0 and not self.visited[row, col - 1]:
            neighbors.append((row, col - 1))
        # Right
        if col < self.config.width - 1 and not self.visited[row, col + 1]:
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
    ):
        """Fill a deadend by adding a wall to the only open side"""
        next_cell = (row, col)
        while (
            next_cell != self.config.entry
            and next_cell != self.config.exit
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
                if col < self.config.width - 1:
                    maze[row, col + 1] |= self.LEFT
                    next_cell = (row, col + 1)

            elif not (cell_val & self.BOTTOM):
                maze[row, col] |= self.BOTTOM
                if row < self.config.height - 1:
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

        yield maze, self.config.entry

        while True:
            found_deadend = False
            for row in range(self.config.height):
                for col in range(self.config.width):

                    if ((row, col) != self.config.entry and
                            (row, col) != self.config.exit and
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
        row, col = self.config.entry

        solve_size = max(0, solution_str_len)

        added_path = False
        number_path = 0
        step = 0
        next_pos: Tuple[int, int] = self.config.entry
        prev: Optional[Tuple[int, int]] = None

        while (row, col) != self.config.exit:
            value: bool = (randint(0, 4) == 0)
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

    def add_paths(self, solved: np.ndarray[Any, Any],
                  solution_str_len: int) -> np.ndarray[Any, Any]:
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
                0 <= r < self.config.height
                and 0 <= c < self.config.width
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

    def get_neighbors_open(self, cell: Tuple[int, int]):
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        if (self.maze[r, c] & self.TOP) == 0 and r > 0:
            neighbors.append((r - 1, c))
        if (self.maze[r, c] & self.RIGHT) == 0 and c < self.config.width - 1:
            neighbors.append((r, c + 1))
        if (self.maze[r, c] & self.BOTTOM) == 0 and r < self.config.height - 1:
            neighbors.append((r + 1, c))
        if (self.maze[r, c] & self.LEFT) == 0 and c > 0:
            neighbors.append((r, c - 1))

        return neighbors

    def bfs(self, max_paths=999):
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

    def get_neighbors_open_opti(self, cell: Tuple[int, int], maze):
        r, c = cell
        neighbors: List[Tuple[int, int]] = []

        if (maze[r, c] & self.TOP) == 0 and r > 0:
            neighbors.append((r - 1, c))
        if (maze[r, c] & self.RIGHT) == 0 and c < self.config.width - 1:
            neighbors.append((r, c + 1))
        if (maze[r, c] & self.BOTTOM) == 0 and r < self.config.height - 1:
            neighbors.append((r + 1, c))
        if (maze[r, c] & self.LEFT) == 0 and c > 0:
            neighbors.append((r, c - 1))
        return neighbors

    def _heuristic(self, cell: Tuple[int, int]) -> int:
        """Manhattan distance to exit."""
        return (abs(cell[0] - self.config.exit[0])
                + abs(cell[1] - self.config.exit[1]))

    def bfs_opti(self, max_paths=10):
        self.initialize_visited()
        self.set_logo_as_visited()
        self.bfs_paths = []
        maze = self.solve_deadends()

        for step in self.multi_path_search(maze, max_paths=max_paths):
            yield step

    def _yield_path(
        self,
        path: List[Tuple[int, int]],
    ) -> Generator[Any, None, None]:
        for i in range(1, len(path)):
            yield ("fill", path[i - 1], path[i])
        yield ("path_found", path[-1], path[-1])

    def _astar_with_forbidden_steps(
        self,
        maze: np.ndarray,
        start: Tuple[int, int],
        out_path: List[List[Tuple[int, int]]],
    ) -> Generator[Any, None, None]:
        exit_ = self.config.exit

        open_heap: List[Tuple[int, int, Tuple[int, int], Optional[Tuple[int, int]]]] = []
        heappush(open_heap, (self._heuristic(start), 0, start, None))

        g_best: Dict[Tuple[int, int], int] = {start: 0}
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

        while open_heap:
            _, g, curr, parent = heappop(open_heap)

            if curr in came_from:
                continue
            came_from[curr] = parent

            if parent is not None:
                yield ("fill", parent, curr)

            if curr == exit_:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = exit_
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                out_path.append(path)
                for step in self._yield_path(path):
                    yield step
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
        maze: np.ndarray,
        out_path: List[List[Tuple[int, int]]],
    ) -> Generator[Any, None, None]:
        exit_ = self.config.exit
        start = self.config.entry

        open_heap: List[Tuple[int, Tuple[int, int], Optional[Tuple[int, int]]]] = []
        heappush(open_heap, (0, start, None))

        g_best: Dict[Tuple[int, int], int] = {start: 0}
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

        while open_heap:
            neg_g, curr, parent = heappop(open_heap)

            if curr in came_from:
                continue
            came_from[curr] = parent

            if parent is not None:
                yield ("fill", parent, curr)

            if curr == exit_:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = exit_
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                out_path.append(path)
                for step in self._yield_path(path):
                    yield step
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
        maze: np.ndarray,
        target_len: int,
        exclude: Set[Tuple[Tuple[int, int], ...]],
        out_path: List[List[Tuple[int, int]]],
    ) -> Generator[Any, None, None]:
        exit_ = self.config.exit
        start = self.config.entry

        open_heap: List[Tuple[int, int, Tuple[int, int], Optional[Tuple[int, int]]]] = []
        heappush(open_heap, (abs(target_len - self._heuristic(start)), 0, start, None))

        g_best: Dict[Tuple[int, int], int] = {start: 0}
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

        best_path: Optional[List[Tuple[int, int]]] = None
        best_deviation = 10**9

        while open_heap:
            _, g, curr, parent = heappop(open_heap)

            if curr in came_from:
                continue
            came_from[curr] = parent

            if parent is not None:
                yield ("fill", parent, curr)

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
            for step in self._yield_path(best_path):
                yield step

    def _yen_fallback(
        self,
        maze: np.ndarray,
        needed: int,
    ) -> Generator[Any, None, None]:
        if not self.bfs_paths:
            return

        candidates: List[Tuple[int, List[Tuple[int, int]]]] = []
        candidate_set: Set[Tuple[Tuple[int, int], ...]] = {
            tuple(p) for p in self.bfs_paths
        }

        while len(self.bfs_paths) < needed:
            for k_path in list(self.bfs_paths):
                for spur_idx in range(len(k_path) - 1):
                    spur_node = k_path[spur_idx]
                    root_path = k_path[:spur_idx + 1]

                    spur_out: List[List[Tuple[int, int]]] = []
                    for step in self._astar_with_forbidden_steps(
                        maze, spur_node, spur_out
                    ):
                        yield step

                    if not spur_out:
                        continue

                    total_path = root_path + spur_out[0][1:]
                    total_key = tuple(total_path)

                    if total_key not in candidate_set:
                        candidate_set.add(total_key)
                        heappush(candidates, (len(total_path), total_path))

            if not candidates:
                break

            _, best = heappop(candidates)
            self.bfs_paths.append(best)
            for step in self._yield_path(best):
                yield step

    def multi_path_search(
        self,
        maze: np.ndarray,
        max_paths: int = 5,
    ) -> Generator[Any, None, None]:
        self.bfs_paths = []
        exclude: Set[Tuple[Tuple[int, int], ...]] = set()

        first_out: List[List[Tuple[int, int]]] = []
        for step in self._astar_with_forbidden_steps(
            maze, self.config.entry, first_out
        ):
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
            shortest_len  = len(first)
            longest_len   = len(longest)
            length_range  = longest_len - shortest_len

            if length_range > 0:
                percentiles = [0.25, 0.50, 0.75]
                targets = [
                    int(shortest_len + p * length_range)
                    for p in percentiles
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

        if len(self.bfs_paths) < 2:
            for step in self._yen_fallback(maze, needed=2):
                yield step

        for path in self.bfs_paths:
            yield ("path_found", path[-1], path[-1])
