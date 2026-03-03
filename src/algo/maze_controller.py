import sys
import os
from typing import Union, Any

from src.algo.maze_config import MazeConfig
from src.algo.generation import MazeGenerator
from src.algo.hex_generation import HexMazeGenerator
from src.algo.file_manager import MazeFileManager


class MazeController:
    """
    Main controller for Maze Generation.
    Orchestrates: Config -> Generator -> File Output.
    """
    def __init__(self, config_file: str) -> None:
        # 1. Load Configuration
        try:
            self.config = MazeConfig.from_env(config_file)
        except Exception as e:
            sys.exit(f"Configuration error: {e}")

        # 2. Setup File Manager
        self.output_file = str(os.environ.get("OUTPUT_FILE", "maze.txt"))
        self.file_manager = MazeFileManager(self.config)

        # 3. Setup Logic Generator
        if self.config.is_hex:
            self.generator: Union[
                MazeGenerator, HexMazeGenerator
            ] = HexMazeGenerator(self.config)
        else:
            self.generator = MazeGenerator(self.config)

    def generate_maze(self) -> str:
        """
        Runs the standard workflow: Generate -> Write ->
          Solve -> Write Solution.
        """
        try:
            # Step 1: Generate the maze structure
            maze = self.generator.generate()
            self.file_manager.write_maze(self.output_file, maze)

            # Step 2: Solve the perfect maze (dead-end filling)
            # We solve it immediately to ensure valid entry/exit path exists
            solved_grid = self.generator.solve_deadends()

            # Convert grid-based solution to string format (Directions)
            solution_str = self.file_manager.resolve_to_string(
                solved_grid, self.generator
            )
            self.file_manager.append_solution(self.output_file, solution_str)

            # Step 3: Handle "Imperfect" mode (Add loops)
            if not self.config.perfect:
                # Add extra paths to create loops
                maze = self.generator.add_paths(solved_grid, len(solution_str))

                # Overwrite file with new loopy structure
                self.file_manager.write_maze(self.output_file, maze)

                # Re-solve using BFS (optimal for graphs with cycles)
                solved_grid = self.generator.solve_deadends()
                path = self.generator.bfs(solved_grid)

                # Append new BFS path
                final_path_str = self.file_manager.path_to_string(path)
                self.file_manager.append_solution(self.output_file,
                                                  final_path_str)

            return self.output_file

        except Exception as e:
            sys.exit(f"Generation process failed: {e}")

    def get_step_generator(self) -> Any:
        """
        Returns the Python generator that yields maze states step-by-step.
        Use this for the Display/GUI to animate generation.
        """
        return self.generator.generate_steps()
