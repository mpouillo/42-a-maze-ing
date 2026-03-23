#!/usr/bin/env python3

import sys
import os
from src import Application
from pathlib import Path


def parse_config(config_file: str) -> None:
    valid_keys = [
        "HEIGHT",
        "WIDTH",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SEED",
        "HEX"
    ]

    try:
        with open(config_file, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                if not line.strip():
                    continue
                if len(line.split("#", 1)) != 1:
                    raise ValueError("Inline comments are forbidden")

                split_result: list[str] = [
                    part.strip() for part in line.split("=", 1)
                ]
                if len(split_result) != 2:
                    raise ValueError("Key missing '=' separator")
                key, value = split_result
                if key not in valid_keys:
                    raise ValueError("Invalid key in config file")
                os.environ[key] = value

    except Exception as e:
        sys.exit(f"Error parsing config: {e}")

    # Output path validation
    output_file: str = os.environ.get("OUTPUT_FILE", "")
    if not output_file:
        raise ValueError("Output file cannot be None")
    output_path = Path(output_file)
    if output_path.suffix != ".txt":
        raise ValueError("Output file extension must be .txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.is_dir():
        raise ValueError("Output file is a directory")
    if str(output_path) == config_file:
        raise ValueError(
            f"Cannot write maze output to config file {config_file}"
        )


def get_config_file() -> str:
    """Parse sys args for config filename, check access and return filename."""
    if len(sys.argv) != 2:
        sys.exit(
            "Incorrect usage. "
            "Run with: 'python3 a_maze_ing.py [config_file]"
        )
    if not os.access(sys.argv[1], os.F_OK):
        sys.exit("Error: Config file not found")
    if not os.access(sys.argv[1], os.R_OK):
        sys.exit("Error: Missing permissions to read config file")
    return sys.argv[1]


def main() -> None:
    """Get config from args and run application."""
    config_file = get_config_file()
    parse_config(config_file)
    app = Application(config_file)
    app.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Exiting program:", e)
        os._exit(1)
