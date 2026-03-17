import os
import numpy as np
from typing import Union, Generator, Tuple, Optional, TypeAlias, Any

from .maze_config import MazeConfig
from .sqr_generation import SqrGenerator
from .hex_generation import HexGenerator
from .file_manager import MazeFileManager

StepList: TypeAlias = list[dict[tuple[int, int], int]]
StepGenerator: TypeAlias = Generator[
    Tuple[str, Tuple[int, int], Tuple[int, int]], None, None
]


class MazeGenerator:
    """
    Main controller for Maze Generation.
    Acts as a bridge between the Algorithm and the Display/File System.
    """

    def __init__(self) -> None:
        try:
            self.config = MazeConfig.from_env()
        except Exception as e:
            raise ValueError(f"Configuration error: {e}")

        # Components
        self.file_manager = MazeFileManager(self.config)
        self.output_file = str(os.environ.get("OUTPUT_FILE", "maze.txt"))

        # Select Strategy
        if self.config.is_hex:
            self.generator: Union[SqrGenerator, HexGenerator] = (
                HexGenerator(self.config)
            )
        else:
            self.generator = SqrGenerator(self.config)

        if self.config.is_hex:

            self.maze: np.ndarray[Any, Any] = np.full(
                (self.config.height, self.config.width), 0x3F, dtype=np.uint8
            )
        else:
            self.maze = np.full(
                (self.config.height, self.config.width), 0xF, dtype=np.uint8
            )
        self.solved_maze: Optional[np.ndarray[Any, Any]] = None

        self.gen_steps: list[Any] = []
        self.solve_steps: list[Any] = []
        self.valid_paths: list[Any] = []

        self.generator.initialize_maze()

    # FILE OPERATIONS;

    def initialize_maze(self) -> None:
        if self.config.is_hex:
            self.maze = np.full(
                (self.config.height, self.config.width), 0x3F, dtype=np.uint8
            )
        else:
            self.maze = np.full(
                (self.config.height, self.config.width), 0xF, dtype=np.uint8
            )

    def generate_new_maze(self) -> None:
        self.gen_steps = list(self.get_generation_steps())
        self.save_current_maze()
        self.solve_steps = list(self.generator.bfs_opti())
        self.valid_paths = sorted(
            self.generator.bfs_paths, key=lambda path: len(path)
        )
        self.save_solution(self.valid_paths[0])

    def get_generation_steps(self) -> StepGenerator:
        step_gen = self.generator.generate_steps()
        for maze, info in step_gen:
            self.maze = maze
            yield info

        if self.config.perfect is False:
            self.solved_maze = self.generator.solve_deadends()
            sol_str = self.file_manager.resolve_to_string(
                self.solved_maze, self.generator
            )

            imper_gen = self.generator.add_paths_steps(
                self.solved_maze, len(sol_str)
            )
            for maze, info in imper_gen:
                self.maze = maze
                yield info

    def save_current_maze(self) -> None:
        self.file_manager.write_maze(self.output_file, self.maze)

    def save_solution(
        self, path: Optional[list[Tuple[int, int]]] = None
    ) -> None:

        bfs_str = self.file_manager.path_to_string(path)
        self.file_manager.append_solution(self.output_file, bfs_str)
