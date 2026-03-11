#!/usr/bin/env python3

import sys
from src import Application
from dotenv import load_dotenv


def get_config_file() -> str:
    if len(sys.argv) != 2:
        sys.exit("Incorrect usage. "
                 "Run with: 'python3 a_maze_ing.py [config_file]")
    return sys.argv[1]


def main() -> None:
    config_file = get_config_file()
    load_dotenv(config_file)
    app = Application(config_file)
    app.run()


if __name__ == "__main__":
    try:
        main()
    except (SystemExit, KeyboardInterrupt) as e:
        print("Exiting program:", e)
