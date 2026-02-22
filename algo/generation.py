from random import randint, seed
import numpy as np
from dotenv import load_dotenv
import os
import sys
from typing import Any, List, Tuple


load_dotenv("config.txt")


class MazeGenerator:

    TOP = 1
    RIGHT = 2
    BOTTOM = 4
    LEFT = 8
    FULL = 15

    def __init__(self) -> None:
        self.load_config()
        seed(self.seed)

    def load_config(self) -> None:
        try:
            self.height = int(str(os.environ.get("HEIGHT")))
            self.width = int(str(os.environ.get("WIDTH")))

            entry_str = str(os.environ.get("ENTRY")).strip().split(',')
            self.entry = (int(entry_str[0]), int(entry_str[1]))

            exit_str = str(os.environ.get("EXIT")).strip().split(',')
            self.exit = (int(exit_str[0]), int(exit_str[1]))

            self.seed = int(str(os.environ.get("SEED")))
        except (ValueError, IndexError) as e:
            sys.exit(f"Configuration error: {e}")

    def initialize_grids(self) -> None:
        """Reset maze and visited arrays"""
        # Fill maze with all walls (15 = 1111 binary)
        self.maze = np.full((self.height, self.width), 15, dtype=np.uint8)
        self.visited = np.zeros((self.height, self.width), dtype=bool)

    def apply_logo(self) -> None:
        """Mark logo area as visited so the maze generates around it"""
        with open("algo/logo.txt", "r") as f:
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
        self.initialize_grids()
        self.apply_logo()

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

    def count_walls(self, row: int, col: int) -> int:
        """Count how many walls a specific cell has"""
        cell_val = self.maze[row, col]
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

    def close_deadend(self, row: int, col: int) -> None:
        """Fill a deadend by adding a wall to the only open side"""
        cell_val = self.maze[row, col]

        # If TOP is open, close it (add TOP wall)
        # and add BOTTOM wall to the neighbor above
        if not (cell_val & self.TOP):
            self.maze[row, col] |= self.TOP
            if row > 0:
                self.maze[row - 1, col] |= self.BOTTOM

        elif not (cell_val & self.RIGHT):
            self.maze[row, col] |= self.RIGHT
            if col < self.width - 1:
                self.maze[row, col + 1] |= self.LEFT

        elif not (cell_val & self.BOTTOM):
            self.maze[row, col] |= self.BOTTOM
            if row < self.height - 1:
                self.maze[row + 1, col] |= self.TOP

        elif not (cell_val & self.LEFT):
            self.maze[row, col] |= self.LEFT
            if col > 0:
                self.maze[row, col - 1] |= self.RIGHT

    def solve_deadends(self) -> np.ndarray[Any, Any]:
        """
        Removes dead ends to find the solution.
        """
        if self.maze is None:
            return self.maze

        while True:
            found_deadend = False
            for row in range(self.height):
                for col in range(self.width):
                    if ((row, col) != self.entry and
                            (row, col) != self.exit and
                            self.count_walls(row, col) == 3):
                        self.close_deadend(row, col)
                        found_deadend = True
            if not found_deadend:
                break
        return self.maze


if __name__ == "__main__":
    gen = MazeGenerator()
    maze = gen.generate()
    print("Maze Generated.")
    gen.solve_deadends()
    print("Maze Solved.")
