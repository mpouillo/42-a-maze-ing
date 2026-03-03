import sys
import os
import numpy as np
from typing import Union, Any, Generator, Tuple, Optional

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

    def save_solution(self, path: Any = None) -> None:
        """Saves the solution string to the existing maze file."""
        if self._solved_maze is not None:
            # 1. Primary solution (Dead-end filling)
            sol_str = self.file_manager.resolve_to_string(
                self._solved_maze, self.generator
            )
            self.file_manager.append_solution(self.output_file, sol_str)

            # 2. BFS solution (Required for imperfect mazes)
            if not self.config.perfect and path:
                bfs_str = self.file_manager.path_to_string(path)
                self.file_manager.append_solution(self.output_file, bfs_str)

    #  VISUALIZATION

    def verify_config(self) -> None:
        print(f"Loaded {self.config.height}x{self.config.width} Maze")
        print(f"Mode: {'HEX' if self.config.is_hex else 'RECT'}")
        print(f"Perfect: {self.config.perfect}")

    def get_generation_steps(
            self
    ) -> Generator[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        Phase 1: Animation of walls being broken.
        """
        step_gen = self.generator.generate_steps()
        for maze, cell in step_gen:
            self._maze = maze
            yield maze, cell

    def get_solving_steps(
            self
    ) -> Generator[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        Phase 2: Animation of dead-ends being filled.
        """
        if self._maze is None:
            self._maze = self.generator.generate()

        solve_gen = self.generator.solve_deadends_steps()
        for solved_grid, cell in solve_gen:
            self._solved_maze = solved_grid
            yield solved_grid, cell

    def get_imperfection_steps(
            self
    ) -> Generator[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        Phase 3 : Animation of loops being added.
        """
        if self.config.perfect:
            return

        if self._solved_maze is None:
            self._solved_maze = self.generator.solve_deadends()

        # Calculate solution length needed for the logic
        sol_str = self.file_manager.resolve_to_string(self._solved_maze,
                                                      self.generator)

        imperfection_gen = self.generator.add_paths_steps(self._solved_maze,
                                                          len(sol_str))
        for maze, cell in imperfection_gen:
            self._maze = maze
            yield maze, cell

    def get_pathfinding_steps(
        self,
        use_optimized_maze: bool = False
    ) -> Generator[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        Phase 4: BFS Exploration.

        Args:
            use_optimized_maze:
                If True, runs BFS on the 'solved' grid (dead-ends filled).
                If False, runs BFS on the raw maze (exploring all dead-ends).
        """
        # 1. Ensure the maze is fully generated first
        if self._maze is None:
            self._maze = self.generator.generate()

            if not self.config.perfect:
                temp_solved = self.generator.solve_deadends()
                sol_str = self.file_manager.resolve_to_string(
                    temp_solved, self.generator
                )
                self._maze = self.generator.add_paths(
                    temp_solved, len(sol_str)
                )

        # 2. Select the grid to run BFS on
        if use_optimized_maze:
            # Check if we have a solved version ready
            if self._solved_maze is None:
                # Assuming simple solve (fill deadends) without BFS,
                # or re-running dead-end filling on the current maze structure
                self._solved_maze = self.generator.solve_deadends()

            target_grid = self._solved_maze
        else:
            target_grid = self._maze

        # 3. Run Generator
        return self.generator.bfs_steps(target_grid)
