#!/usr/bin/env python3

from src import DisplayMaze

if __name__ == "__main__":
    visualizer = DisplayMaze("config.txt", "output_maze.txt")
    visualizer.run_maze_display()
