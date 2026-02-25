import sys


class MazeModel:
    def __init__(self, maze_file: str) -> None:
        self.load_maze_data(maze_file)
        self.path_step = 0
        self.path_prev = 0
        self.solving = False

    def load_maze_data(self, maze_file: str):
        try:
            maze_dict = self.parse_maze(maze_file)
        except FileNotFoundError:
            sys.exit(f"\"{maze_file}\" file not found.")

        self.entry = maze_dict.get("entry")
        self.exit = maze_dict.get("exit")
        self.path = maze_dict.get("path")
        self.grid = maze_dict.get("maze")

        self.width = len(self.grid[0])
        self.height = len(self.grid)

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
