#!/usr/bin/env python3

import os
import sys
from importlib.metadata import version, PackageNotFoundError


def main() -> None:
    from src import Window, generate_maze

    if len(sys.argv) != 2:
        sys.exit("Incorrect usage. "
                 "Run with: 'python3 a_maze_ing.py [config_file]")

    else:
        config_file = sys.argv[1]

    try:
        maze_file = str(os.environ.get("OUTPUT_FILE"))
    except ValueError:
        sys.exit("Error while parsing config file: "
                 "Incorrect 'OUTPUT_FILE' value")

    generate_maze(maze_file)
    Window(maze_file, config_file, 1620, 1020)


def check_dependencies(req_filename: str) -> bool:
    req_list = []
    try:
        with open(req_filename) as f:
            req_list = f.read().strip().split("\n")
    except FileNotFoundError:
        sys.exit(f"Requirement file '{req_filename}' not found.")
    missing = []
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
    else:
        return True


if __name__ == "__main__":
    if check_dependencies("requirements.txt") is True:
        try:
            main()
        except (SystemExit, KeyboardInterrupt) as e:
            print("Exiting program:", e)
