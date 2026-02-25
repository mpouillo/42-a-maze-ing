#!/usr/bin/env python3

import sys
from importlib.metadata import version, PackageNotFoundError
from src.controllers.maze_controller import MazeController


def get_config_file() -> str:
    if len(sys.argv) != 2:
        sys.exit("Incorrect usage. "
                 "Run with: 'python3 a_maze_ing.py [config_file]")
    return sys.argv[1]


def check_dependencies(req_filename: str) -> bool:
    missing = []
    req_list = []

    try:
        with open(req_filename) as f:
            req_list = f.read().strip().split("\n")
    except FileNotFoundError:
        sys.exit(f"Requirement file '{req_filename}' not found.")

    for package in req_list:
        try:
            version(package)
        except PackageNotFoundError:
            missing.append(package)

    if len(missing) > 0:
        print("The following packages could not be found:",
              ", ".join(missing), "\n"
              "Make sure to run the project with 'make'.")
        return False

    return True


def main() -> None:
    config_file = get_config_file()
    app = MazeController(config_file, 1600, 1200)
    app.run()


if __name__ == "__main__":
    if check_dependencies("requirements.txt") is True:
        try:
            main()
        except (SystemExit, KeyboardInterrupt) as e:
            print("Exiting program:", e)
