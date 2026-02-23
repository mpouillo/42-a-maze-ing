#!/usr/bin/env python3

from src import Window, generate_maze


def main() -> None:
    maze_file = generate_maze("output_maze.txt")
    config_file = "config.txt"
    Window(maze_file, config_file, 1400, 1400)


if __name__ == "__main__":
    main()
