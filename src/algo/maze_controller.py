import sys
import os
import numpy as np
from typing import Union, Generator, Tuple, Optional

from src.algo.maze_config import MazeConfig
from src.algo.generation import MazeGenerator
from src.algo.hex_generation import HexMazeGenerator
from src.algo.file_manager import MazeFileManager


class MazeController:
    """
    Main controller for Maze Generation.
    Acts as a bridge between the Algorithm and the Display/File System.
    """
    def __init__(self, config_file: str) -> None:
        try:
            self.config = MazeConfig.from_env(config_file)
        except Exception as e:
            sys.exit(f"Configuration error: {e}")

        # Components
        self.file_manager = MazeFileManager(self.config)
        self.output_file = str(os.environ.get("OUTPUT_FILE", "maze.txt"))

        # Select Strategy
        if self.config.is_hex:
            self.generator: Union[MazeGenerator, HexMazeGenerator] = \
                HexMazeGenerator(self.config)
        else:
            self.generator = MazeGenerator(self.config)

        self._maze: Optional[np.ndarray] = None
        self._solved_maze: Optional[np.ndarray] = None

    # FILE OPERATIONS

    def save_current_maze(self) -> None:
        """Saves the current state of the maze to the output file."""
        if self._maze is not None:
            self.file_manager.write_maze(self.output_file, self._maze)

    def save_solution(self,
                      path: Optional[list[Tuple[int, int]]] = None) -> None:
        """Saves the solution string to the output file."""

        if path is None:
            path = self.solve_maze()

        bfs_str = self.file_manager.path_to_string(path)
        self.file_manager.append_solution(self.output_file, bfs_str)

    def solve_maze(self) -> Optional[list[Tuple[int, int]]]:
        """
        Calcule la solution finale
        """
        if self._maze is None:
            self._maze = self.generator.generate()

            if not self.config.perfect:
                self._solved_maze = self.generator.solve_deadends()
                sol_str = self.file_manager.resolve_to_string(
                   self._solved_maze, self.generator
                )
                self._maze = self.generator.add_paths(
                   self._solved_maze, len(sol_str)
                )

        path = self.generator.bfs(self._maze)
        return path

    #  VISUALIZATION

    def verify_config(self) -> None:
        print(f"Loaded {self.config.height}x{self.config.width} Maze")
        print(f"Mode: {'HEX' if self.config.is_hex else 'RECT'}")
        print(f"Perfect: {self.config.perfect}")

    def get_generation_steps(
            self
    ) -> Generator[Tuple[np.ndarray, Tuple[int, int]], None, None]:
        """
        Phase 1: Animation of walls being broken.
        """
        step_gen = self.generator.generate_steps()
        for maze, cell in step_gen:
            self._maze = maze
            yield maze, cell

        if self.config.perfect is False:
            self._solved_maze = self.generator.solve_deadends()
            sol_str = self.file_manager.resolve_to_string(self._solved_maze,
                                                          self.generator)

            imper_gen = self.generator.add_paths_steps(self._solved_maze,
                                                       len(sol_str))
            for maze, cell in imper_gen:
                self._maze = maze
                yield maze, cell
        self.save_current_maze()
        self.save_solution()

    def get_solving_steps(
            self
    ) -> Generator[Tuple[int, int], None, None]:
        """
        Phase 2: Animation of solving.
        """
        if self._maze is None:
            self._maze = self.generator.generate()

        if self.config.perfect is False:
            solve_gen = self.generator.bfs_steps(self._maze)
        else:
            solve_gen = self.generator.solve_deadends_steps()
        for _, cell in solve_gen:
            yield cell
