#!/usr/bin/env python3

import os
import sys
from importlib.metadata import version, PackageNotFoundError



def main() -> None:
    from src import Window, generate_maze

    if len(sys.argv) != 2:
        print("Incorrect usage."
              "Run with: 'python3 a_maze_ing.py [config_file]")
        os._exit(1)
    else:
        config_file = sys.argv[1]

    try:
        maze_file = str(os.environ.get("OUTPUT_FILE"))
    except ValueError:
        print("Error while parsing config file: "
              "Incorrect OUTPUT_FILE value")
        os._exit(1)

    generate_maze(maze_file)
    Window(maze_file, config_file, 1200, 1200)


def get_req_packages(file: str) -> list:
    req = []
    line = 1
    with open(file) as f:
        for line in f:
            req.append(line.strip())
    return req


def check_dependencies(req_filename: str) -> bool:
    req_list = []
    try:
        with open(req_filename) as f:
            req_list = f.read().strip().split("\n")
    except FileNotFoundError:
        print(f"Requirement file '{req_filename}' not found.")
        os._exit(1)
    missing = []
    for package in req_list:
        try:
            version(package)
        except PackageNotFoundError:
            missing.append(package)
    if len(missing) > 0:
        print(f"The following packages could not be found: {', '.join(missing)}\n"
              "Make sure to run the project with 'make'.")
        return False
    else:
        return True

if __name__ == "__main__":
    if check_dependencies("requirements.txt") == True:
        main()
