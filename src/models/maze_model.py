from src.algo.generate_maze import GenerateOutputFile
import sys


class MazeModel:
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.maze = GenerateOutputFile(self.config_file)
        self.regenerate_maze()

        self.path_step: int = 0
        self.path_prev: int = 0
        self.solving: bool = False

    @property
    def path_step(self) -> int:
        return self.__path_step

    @path_step.setter
    def path_step(self, step: int) -> None:
        if step < 0:
            step = 0
        self.__path_step = min(step, len(self.path))

    def regenerate_maze(self):
        maze_file = self.maze.generate_maze()

        try:
            maze_dict: dict = self.parse_maze(maze_file)
        except FileNotFoundError:
            sys.exit(f"\"{maze_file}\" file not found.")

        self.entry: tuple[int, int] = maze_dict.get("entry", (0, 0))
        self.exit: tuple[int, int] = maze_dict.get("exit", (0, 0))
        self.path: list[int] = maze_dict.get("path", (0, 0))
        self.grid: list[list[int]] = maze_dict.get("maze", (0, 0))

        self.width: int = len(self.grid[0])
        self.height: int = len(self.grid)

        self.path_step = 0

    @staticmethod
    def parse_maze(filename: str) -> dict:
        '''Parse file and return maze data as a dict'''
        try:
            data = {}
            array = []
            with open(filename, 'r') as maze_file:
                for line in maze_file:
                    if not line.strip():
                        break
                    row = []
                    for c in line.strip():
                        row.append(int(c, 16))
                    array.append(row)
                data.update({"maze": array})
                data.update(
                    {"entry": tuple(
                        int(c) for c in maze_file.readline().strip().split(",")
                    )}
                )
                data.update(
                    {"exit": tuple(
                        int(c) for c in maze_file.readline().strip().split(",")
                    )}
                )
                data.update({"path": maze_file.readline().strip()})
            return data
        except Exception as e:
            sys.exit(f"Error while parsing maze output file: {e}")
