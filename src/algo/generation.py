from random import randint, seed
import numpy as np
from dotenv import load_dotenv
import os
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
            self.perfect = None

        if self.perfect is None:
            raise ValueError(
                "PERFECT is not a bool : True or False"
            )

    def initialize_grids(self) -> None:
        """Reset maze and visited arrays"""
        # Fill maze with all walls (15 = 1111 binary)
        self.maze = np.full((self.height, self.width), 15, dtype=np.uint8)
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
        self.initialize_grids()
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

    def close_deadend(self, row: int, col: int) -> Tuple:
        """Fill a deadend by adding a wall to the only open side"""
        next_cell = (row, col)
        # If TOP is open, close it (add TOP wall)
        # and add BOTTOM wall to the neighbor above
        while (next_cell != self.entry and
               next_cell != self.exit and
               self.count_walls(next_cell[0], next_cell[1])) == 3:

            row, col = next_cell
            cell_val = self.maze[row, col]

            if not (cell_val & self.TOP):
                self.maze[row, col] |= self.TOP
                if row > 0:
                    self.maze[row - 1, col] |= self.BOTTOM
                    next_cell = (row - 1, col)

            elif not (cell_val & self.RIGHT):
                self.maze[row, col] |= self.RIGHT
                if col < self.width - 1:
                    self.maze[row, col + 1] |= self.LEFT
                    next_cell = (row, col + 1)

            elif not (cell_val & self.BOTTOM):
                self.maze[row, col] |= self.BOTTOM
                if row < self.height - 1:
                    self.maze[row + 1, col] |= self.TOP
                    next_cell = (row + 1, col)

            elif not (cell_val & self.LEFT):
                self.maze[row, col] |= self.LEFT
                if col > 0:
                    self.maze[row, col - 1] |= self.RIGHT
                    next_cell = (row, col - 1)

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
