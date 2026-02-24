import os
import sys
from dotenv import load_dotenv


class Maze:
    def __init__(self, config: str) -> None:
        load_dotenv(config)

        # Get maze dimensions from config
        try:
            self.MAZE_WIDTH = int(os.environ.get("WIDTH"))
            self.MAZE_HEIGHT = int(os.environ.get("HEIGHT"))
        except ValueError:
            sys.exit("Error while parsing config file")

        # Wall thickness
        try:
            self.LINE_WEIGHT = int(os.environ.get("LINE_WEIGHT"))
        except TypeError:
            self.LINE_WEIGHT = 2
