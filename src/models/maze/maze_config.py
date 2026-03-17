"""Configuration model for maze generation."""

from dataclasses import dataclass
import os
from typing import Optional, Tuple


@dataclass
class MazeConfig:
    """Validated maze parameters."""

    height: int
    width: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    seed: Optional[int]
    perfect: bool
    is_hex: bool

    @staticmethod
    def from_env() -> "MazeConfig":
        """
        create a MazeConfig instance from a .env file.
        Performs all validation logic before creating the object.
        """

        # 1. Dimensions
        try:
            height = int(os.environ.get("HEIGHT", 0))
            width = int(os.environ.get("WIDTH", 0))
        except ValueError:
            raise ValueError("HEIGHT and WIDTH must be integers")

        if height <= 0 or width <= 0:
            raise ValueError("HEIGHT and WIDTH must be positive")

        # 2. Entry Point
        try:
            entry_part = str(os.environ.get("ENTRY", "0,0")).strip().split(",")
            if len(entry_part) != 2:
                raise ValueError("Format error")
            entry = (int(entry_part[0]), int(entry_part[1]))
        except ValueError:
            raise ValueError("ENTRY must be 'row,col'")

        # 3. Exit Point
        try:
            exit_parts = str(os.environ.get("EXIT", "0,0")).strip().split(",")
            if len(exit_parts) != 2:
                raise ValueError("Format error")
            exit_point = (int(exit_parts[0]), int(exit_parts[1]))
        except ValueError:
            raise ValueError("EXIT must be 'row,col'")

        # 4. Logical Validation
        if entry == exit_point:
            raise ValueError("The ENTRY cant be at the same place as the EXIT")

        erow, ecol = entry
        if not (0 <= erow < height and 0 <= ecol < width):
            raise ValueError(
                f"ENTRY {entry} is outside maze bounds" f" ({height}x{width})"
            )

        xrow, xcol = exit_point
        if not (0 <= xrow < height and 0 <= xcol < width):
            raise ValueError(
                f"EXIT {exit_point} is outside maze bounds"
                f" ({height}x{width})"
            )

        # 5. Seed
        seed_val: Optional[int] = None
        seed_env = os.environ.get("SEED")
        if seed_env:
            try:
                seed_val = int(seed_env)
            except ValueError:
                seed_val = None

        # 6. Boolean Flags
        perfect_str = str(os.environ.get("PERFECT", "True"))
        if perfect_str in ["False", "0"]:
            perfect = False
        elif perfect_str in ["True", "1"]:
            perfect = True
        else:
            raise ValueError("PERFECT is not a bool : True(1) or False(0)")

        hex_str = str(os.environ.get("HEX", "False"))
        if hex_str in ["False", "0"]:
            is_hex = False
        elif hex_str in ["True", "1"]:
            is_hex = True
        else:
            raise ValueError("HEX is not a bool : True(1) or False(0)")

        return MazeConfig(
            height=height,
            width=width,
            entry=entry,
            exit=exit_point,
            seed=seed_val,
            perfect=perfect,
            is_hex=is_hex,
        )
