"""Configuration model for maze generation."""

from dataclasses import dataclass
import os
from typing import Optional, Tuple


def to_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true"}


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
    def validate_config() -> None:
        """Validate required environment configuration.

        Raises:
            ValueError: If any required key is missing or invalid.
        """
        REQ_KEYS: list[str] = [
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        ]

        for key in REQ_KEYS:
            if key not in os.environ:
                raise ValueError(f"Missing key in config file: {key}")

        # Getting logo data to check endpoints position
        logo_data: list[str] | None = None
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "logo")

            if not os.path.exists(logo_path):
                return
            with open(logo_path, "r") as f:
                logo_data = [
                    line for line in f.read().splitlines() if line.strip()
                ]
        except Exception:
            raise ValueError(
                "Error reading logo data. Do you have permissions?"
            )
        if logo_data:
            logo_h: int = len(logo_data)
            logo_w: int = len(logo_data[0])
        else:
            raise ValueError("No logo data found")

        width_val: str | None = os.environ.get("WIDTH")
        if width_val in ["None", None]:
            raise ValueError("Width cannot be None")
        if not width_val or not width_val.isdigit():
            raise ValueError("Width must be a valid positive integer")
        width: int = int(width_val)
        if width < 1:
            raise ValueError(f"Width below minimum of 1 ({width})")
        if width > 200:
            raise ValueError(f"Width above maximum of 200 ({width})")
        if width < logo_w:
            raise ValueError(
                "Width cannot be smaller than " f"logo width ({logo_w})"
            )

        height_val: str | None = os.environ.get("HEIGHT")
        if height_val in ["None", None]:
            raise ValueError("Height cannot be None")
        if not height_val or not height_val.isdigit():
            raise ValueError("Height must be a valid positive integer")
        height: int = int(height_val)
        if height < 1:
            raise ValueError(f"Height below minimum of 1 ({height})")
        if height > 200:
            raise ValueError(f"Width above maximum of 200 ({height})")
        if height < logo_h:
            raise ValueError(
                "Height cannot be smaller than " f"logo's ({logo_h})"
            )

        off_x: int = (width - logo_w) // 2
        off_y: int = (height - logo_h) // 2

        entry_val: str | None = os.environ.get("ENTRY")
        if not entry_val:
            raise ValueError("Entry cannot be None")
        if "," not in entry_val:
            raise ValueError("Entry coordinates must be separated by a ','")
        entry_val_y, entry_val_x = entry_val.split(",", 1)
        if not entry_val_x.isdigit() or not entry_val_y.isdigit():
            raise ValueError("Entry must be 2 valid positive integers")
        entry_y, entry_x = int(entry_val_y), int(entry_val_x)
        if not 0 <= entry_x < width or not 0 <= entry_y < height:
            raise ValueError("Entry coordinates must fit within the maze")
        if (
            off_x <= entry_x < off_x + logo_w
            and off_y <= entry_y < off_y + logo_h
        ):
            if logo_data[entry_y - off_y][entry_x - off_x] == "1":
                raise ValueError("Entry cannot overlap with logo")

        exit_val: str | None = os.environ.get("EXIT")
        if not exit_val:
            raise ValueError("Exit cannot be None")
        if "," not in exit_val:
            raise ValueError("Exit coordinates must be separated by a ','")
        exit_val_y, exit_val_x = exit_val.split(",", 1)
        if not exit_val_x.isdigit() or not exit_val_y.isdigit():
            raise ValueError("Exit must be 2 valid positive integers")
        exit_y, exit_x = int(exit_val_y), int(exit_val_x)
        if not 0 <= exit_x < width or not 0 <= exit_y < height:
            raise ValueError("Exit coordinates must fit within the maze")
        if (
            off_x <= exit_x < off_x + logo_w
            and off_y <= exit_y < off_y + logo_h
        ):
            if logo_data[exit_y - off_y][exit_x - off_x] == "1":
                raise ValueError("Exit cannot overlap with logo")

        if (entry_y, entry_x) == (exit_y, exit_x):
            raise ValueError("Entry and Exit cannot overlap")

        perfect: str | None = os.environ.get("PERFECT")
        if not perfect:
            raise ValueError("Perfect state cannot be None")
        if perfect.lower() not in ["true", "false", "0", "1"]:
            raise ValueError("Perfect state should be either True or False")

        hex_val: str | None = os.environ.get("HEX")
        if hex_val and hex_val.lower() not in ["true", "false", "0", "1"]:
            raise ValueError("Hex state should be either True or False")

        seed: str | None = os.environ.get("SEED")
        if seed and seed.isdigit():
            if int(seed) < 0:
                raise ValueError(f"Seed below minimum of 0 ({seed})")
        elif seed:
            if seed.lower() != "random":
                raise ValueError(
                    "Seed should be None, 'Random', or a valid integer"
                )

    @staticmethod
    def from_env() -> "MazeConfig":
        height = int(os.environ.get("HEIGHT", 0))
        width = int(os.environ.get("WIDTH", 0))
        entry_part = os.environ.get("ENTRY", "0,0").split(",")
        entry_point = (int(entry_part[0]), int(entry_part[1]))

        exit_parts = os.environ.get("EXIT", "0,0").strip().split(",")
        exit_point = (int(exit_parts[0]), int(exit_parts[1]))

        seed_val = None
        seed_str = os.environ.get("SEED")
        if seed_str and seed_str.strip().lower() != "random":
            seed_val = int(seed_str)

        perfect = to_bool("PERFECT", False)
        is_hex = to_bool("HEX", False)

        return MazeConfig(
            height=height,
            width=width,
            entry=entry_point,
            exit=exit_point,
            seed=seed_val,
            perfect=perfect,
            is_hex=is_hex,
        )
