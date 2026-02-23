#!/usr/bin/env python3

import sys
import os
from src import Window, generate_maze


def main() -> None:
    if len(sys.argv) != 2:
        print("Incorrect usage."
              "Run with: 'python3 a_maze_ing.py [config_file]")
        os._exit(1)
    else:
        config_file = sys.argv[1]

    try:
        maze_file = str(os.environ.get("OUTPUT_FILE"))
    except ValueError:
        print("Error while parsing config file: "
              "Incorrect OUTPUT_FILE value")
        os._exit(1)

    generate_maze(maze_file)
    Window(maze_file, config_file, 1400, 1400)


if __name__ == "__main__":
    main()
