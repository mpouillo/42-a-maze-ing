import numpy as np
from src.algo.generation import MazeGenerator
from src.algo.hex_generation import HexMazeGenerator
from dotenv import load_dotenv
import sys
import os
from typing import Tuple, Optional, Union, List


class GenerateOutputFile:
    def __init__(self, config_file: str) -> None:
        load_dotenv(config_file)
        self.output_file: str = str(os.environ.get("OUTPUT_FILE"))

        self.maze_gen: Union[MazeGenerator, HexMazeGenerator]
        self.maze_gen = MazeGenerator(config_file)

        self.entry: Tuple[int, int] = self.maze_gen.entry
        self.exit_: Tuple[int, int] = self.maze_gen.exit
        self.perfect: bool = self.maze_gen.perfect
        self.hex_: bool = self.maze_gen.hex_

        if self.hex_ is True:
            self.maze_gen = HexMazeGenerator(config_file)

    def write_maze(self, maze: np.ndarray) -> None:
        with open(self.output_file, "w") as f:
            if self.hex_ is True:
                for row in maze:
                    line = "".join(format(int(c) & 0x3F, "02X") for c in row)
                    f.write(line + "\n")
            else:
                for row in maze:
                    # Square mazes use up to 15 (0xF) -> needs 1 hex digit
                    line = "".join(format(int(c) & 0xF, "X") for c in row)
                    f.write(line + "\n")
            f.write("\n")
            f.write(str(self.entry).strip("()"))
            f.write("\n")
            f.write(str(self.exit_).strip("()"))
            f.write("\n")

    def write_resolve(self, maze: np.ndarray) -> None:
        with open(self.output_file, "a") as f:
            if self.hex_ is True:
                assert isinstance(self.maze_gen, HexMazeGenerator)

                row, col = self.entry
                prev: Optional[Tuple[int, int]] = None

                while (row, col) != self.exit_:
                    curr = (row, col)
                    val = int(maze[row, col])

                    if row % 2 == 0:
                        if (
                            (val & self.maze_gen.TOP_RIGHT) == 0
                            and row > 0
                            and (row - 1, col) != prev
                        ):
                            prev = curr
                            row -= 1
                            f.write("A")
                            continue
                        elif (
                            (val & self.maze_gen.RIGHT) == 0
                            and col < self.maze_gen.width - 1
                            and (row, col + 1) != prev
                        ):
                            prev = curr
                            col += 1
                            f.write("B")
                            continue
                        elif (
                            (val & self.maze_gen.BOTTOM_RIGHT) == 0
                            and row < self.maze_gen.height - 1
                            and (row + 1, col) != prev
                        ):
                            prev = curr
                            row += 1
                            f.write("C")
                            continue
                        elif (
                            (val & self.maze_gen.BOTTOM_LEFT) == 0
                            and row < self.maze_gen.height - 1
                            and col > 0
                            and (row + 1, col - 1) != prev
                        ):
                            prev = curr
                            row += 1
                            col -= 1
                            f.write("D")
                            continue
                        elif (
                            (val & self.maze_gen.LEFT) == 0
                            and col > 0
                            and (row, col - 1) != prev
                        ):
                            prev = curr
                            col -= 1
                            f.write("E")
                            continue
                        elif (
                            (val & self.maze_gen.TOP_LEFT) == 0
                            and row > 0
                            and col > 0
                            and (row - 1, col - 1) != prev
                        ):
                            prev = curr
                            row -= 1
                            col -= 1
                            f.write("F")
                            continue
                        break
                    else:
                        if (
                            (val & self.maze_gen.TOP_RIGHT) == 0
                            and row > 0
                            and col < self.maze_gen.width - 1
                            and (row - 1, col + 1) != prev
                        ):
                            prev = curr
                            row -= 1
                            col += 1
                            f.write("A")
                            continue
                        elif (
                            (val & self.maze_gen.RIGHT) == 0
                            and col < self.maze_gen.width - 1
                            and (row, col + 1) != prev
                        ):
                            prev = curr
                            col += 1
                            f.write("B")
                            continue
                        elif (
                            (val & self.maze_gen.BOTTOM_RIGHT) == 0
                            and row < self.maze_gen.height - 1
                            and col < self.maze_gen.width - 1
                            and (row + 1, col + 1) != prev
                        ):
                            prev = curr
                            row += 1
                            col += 1
                            f.write("C")
                            continue
                        elif (
                            (val & self.maze_gen.BOTTOM_LEFT) == 0
                            and row < self.maze_gen.height - 1
                            and (row + 1, col) != prev
                        ):
                            prev = curr
                            row += 1
                            f.write("D")
                            continue
                        elif (
                            (val & self.maze_gen.LEFT) == 0
                            and col > 0
                            and (row, col - 1) != prev
                        ):
                            prev = curr
                            col -= 1
                            f.write("E")
                            continue
                        elif (
                            (val & self.maze_gen.TOP_LEFT) == 0
                            and row > 0
                            and (row - 1, col) != prev
                        ):
                            prev = curr
                            row -= 1
                            f.write("F")
                            continue
                        break

                return

            row, col = self.entry
            prev: Optional[Tuple[int, int]] = None

            while (row, col) != self.exit_:
                if (
                    not (maze[row, col] & (1 << 0))
                    and (row - 1, col) != prev
                ):
                    prev = (row, col)
                    row -= 1
                    f.write("N")
                    continue

                elif (
                    not (maze[row, col] & (1 << 1))
                    and (row, col + 1) != prev
                ):
                    prev = (row, col)
                    col += 1
                    f.write("E")
                    continue

                elif (
                    not (maze[row, col] & (1 << 2))
                    and (row + 1, col) != prev
                ):
                    prev = (row, col)
                    row += 1
                    f.write("S")
                    continue

                elif (
                    not (maze[row, col] & (1 << 3))
                    and (row, col - 1) != prev
                ):
                    prev = (row, col)
                    col -= 1
                    f.write("W")
                    continue

                break

    def write_path(self, path: Optional[List[Tuple[int, int]]]) -> None:
        if not path or len(path) < 2:
            return

        with open(self.output_file, "a") as f:
            if self.hex_ is True:
                row, col = path[0]

                for nxt in path[1:]:
                    nr, nc = nxt

                    if row % 2 == 0:
                        if (nr, nc) == (row - 1, col):
                            f.write("A")
                        elif (nr, nc) == (row, col + 1):
                            f.write("B")
                        elif (nr, nc) == (row + 1, col):
                            f.write("C")
                        elif (nr, nc) == (row + 1, col - 1):
                            f.write("D")
                        elif (nr, nc) == (row, col - 1):
                            f.write("E")
                        elif (nr, nc) == (row - 1, col - 1):
                            f.write("F")
                    else:
                        if (nr, nc) == (row - 1, col + 1):
                            f.write("A")
                        elif (nr, nc) == (row, col + 1):
                            f.write("B")
                        elif (nr, nc) == (row + 1, col + 1):
                            f.write("C")
                        elif (nr, nc) == (row + 1, col):
                            f.write("D")
                        elif (nr, nc) == (row, col - 1):
                            f.write("E")
                        elif (nr, nc) == (row - 1, col):
                            f.write("F")

                    row, col = nr, nc

                return

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

    def generate_maze(self) -> str:
        try:
            maze = self.maze_gen.generate()
            self.write_maze(maze)

            solved = self.maze_gen.solve_deadends()
            self.write_resolve(solved)

            if self.perfect is False:
                maze = self.maze_gen.add_paths(solved, self.output_file)
                self.write_maze(maze)
                solved = self.maze_gen.solve_deadends()
                path = self.maze_gen.bfs(solved)
                self.write_path(path)

            return self.output_file

        except (Exception) as e:
            sys.exit(f"Configuration error: {e}")
