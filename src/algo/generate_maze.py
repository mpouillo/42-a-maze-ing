import numpy as np
from src.algo.generation import MazeGenerator
import sys


def cell_to_hex(cell: int) -> str:
    return format(cell & 0xF, "X")


def write_maze(maze: np.ndarray, filename: str, entry, exit_) -> None:
    with open(filename, "w") as f:
        for row in maze:
            f.write("".join(cell_to_hex(c) for c in row) + "\n")
        f.write("\n")
        f.write(str(entry).strip("()"))
        f.write("\n")
        f.write(str(exit_).strip("()"))
        f.write("\n")


def write_resolve(maze: np.ndarray, filename: str, entry, exit_) -> None:
    with open(filename, "a") as f:
        row, col = entry
        prev = None

        while (row, col) != exit_:

            if not maze[row, col] & (1 << 0) and (row-1, col) != prev:
                prev = (row, col)
                row -= 1
                f.write("N")
                continue

            if not maze[row, col] & (1 << 1) and (row, col+1) != prev:
                prev = (row, col)
                col += 1
                f.write("E")
                continue

            if not maze[row, col] & (1 << 2) and (row+1, col) != prev:
                prev = (row, col)
                row += 1
                f.write("S")
                continue

            if not maze[row, col] & (1 << 3) and (row, col-1) != prev:
                prev = (row, col)
                col -= 1
                f.write("W")
                continue


def generate_maze(filename: str) -> str:
    try:
        maze_gen = MazeGenerator()

        entry = maze_gen.entry
        exit_ = maze_gen.exit

        maze = maze_gen.generate()
        write_maze(maze, filename, entry, exit_)

        solved = maze_gen.solve_deadends()
        write_resolve(solved, filename, entry, exit_)
        return filename

    except (ValueError, IndexError) as e:
        sys.exit(f"Configuration error: {e}")
