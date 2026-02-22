from PIL import Image, ImageDraw
import numpy as np
from algo.generation import MazeGenerator
import os


def draw_maze(maze, cell_size=20):
    height, width = maze.shape
    img = Image.new("RGB", (width * cell_size, height * cell_size), "white")
    draw = ImageDraw.Draw(img)

    for r in range(height):
        for c in range(width):
            val = maze[r, c]
            x1, y1 = c * cell_size, r * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size

            if val & (1 << 0):
                draw.line([(x1, y1), (x2, y1)], fill="black", width=2)
            if val & (1 << 1):
                draw.line([(x2, y1), (x2, y2)], fill="black", width=2)
            if val & (1 << 2):
                draw.line([(x1, y2), (x2, y2)], fill="black", width=2)
            if val & (1 << 3):
                draw.line([(x1, y1), (x1, y2)], fill="black", width=2)

    img.show()


def create_grid(width, height):
    maze = np.array([[0x0 for _ in range(width)] for _ in range(height)])
    maze[0, :] |= (1 << 0)
    maze[height - 1, :] |= (1 << 2)
    maze[:, 0] |= (1 << 3)
    maze[:, height - 1] |= (1 << 1)
    return maze


def cell_to_hex(cell):
    return format(cell & 0xF, "X")


def write_maze(maze, filename):
    with open(filename, "w") as f:
        for row in maze:
            f.write("".join(cell_to_hex(c) for c in row) + "\n")
        f.write("\n")
        f.write(str(ENTRY).strip("()"))
        f.write("\n")
        f.write(str(EXIT).strip("()"))
        f.write("\n")


ENTRY = tuple(int(n) for n in os.environ.get("ENTRY").strip().split(','))
EXIT = tuple(int(n) for n in os.environ.get("EXIT").strip().split(','))


def write_resolve(maze, filename):
    with open(filename, "a") as f:
        row, col = ENTRY
        prev = None

        while (row, col) != EXIT:

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


def generate_maze():
    filename = "output_maze.txt"
    maze = MazeGenerator()
    write_maze(maze.generate(), filename)
    solve_maze = maze.solve_deadends()
    write_resolve(solve_maze, filename)
    return filename
