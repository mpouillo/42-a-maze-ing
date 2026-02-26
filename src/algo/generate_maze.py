import numpy as np
from src.algo.generation import MazeGenerator
from dotenv import load_dotenv
import sys
import os


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


def write_path(path, output_file):
    with open(output_file, "a") as f:
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            dr, dc = r2 - r1, c2 - c1
            if dr == -1 and dc == 0:
                f.write("N")
            elif dr == 1 and dc == 0:
                f.write("S")
            elif dr == 0 and dc == 1:
                f.write("E")
            elif dr == 0 and dc == -1:
                f.write("W")


def generate_maze(config_file: str) -> str:
    try:
        load_dotenv(config_file)
        output_file: str = str(os.environ.get("OUTPUT_FILE"))
        maze_gen = MazeGenerator(config_file)

        entry: tuple = maze_gen.entry
        exit_: tuple = maze_gen.exit
        perfect: bool = maze_gen.perfect

        maze = maze_gen.generate()
        write_maze(maze, output_file, entry, exit_)

        solved = maze_gen.solve_deadends()
        write_resolve(solved, output_file, entry, exit_)

        if perfect is False:
            maze = maze_gen.add_paths(solved, output_file)
            write_maze(maze, output_file, entry, exit_)
            solved = maze_gen.solve_deadends()
            path = maze_gen.bfs(solved)
            write_path(path, output_file)

        return output_file

    except (Exception) as e:
        sys.exit(f"Configuration error: {e}")
