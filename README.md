*This project has been created as part of the 42 curriculum by mpouillo, acampion.*

# 42-A-Maze-ing

### Description

The goal of *A-Maze-ing* is to create our own maze generator and display its result. This project requires learning algorithms for both generation and solving, library frameworks (Mlx) and how to structure a semi-large project.

This project is done in Python 3.10+. The maze generator takes a configuration file, generates a maze and writes it to a file using a hexadecimal wall representation.

#### Configuration file

| Key               | Description                   | Example               |
| ----------------- | ----------------------------- | --------------------- |
| WIDTH             | Maze width (number of cells)  | WIDTH=20              |
| HEIGHT            | Maze height                   | WIDTH=20              |
| ENTRY             | Entry coordinates (y, x)      | ENTRY=0,0             |
| EXIT              | Exit coordinates (y, x)       | EXIT=19,19            |
| OUTPUT_FILE       | Output filename               | OUTPUT_FILE=maze.txt  |
| PERFECT           | Perfect maze? (only 1 path)   | PERFECT=True          |
| SEED (*optional*) | Set seed for generation       | SEED=42               |
| HEX (*optional*)  | Hex maze? (hexagonal walls)   | HEX=False             |

#### Display

A visual display with user interaction is also available.<br>
The display uses the MiniLibX (Mlx) library to connect to display drivers and provide a visual representation of the maze.

Available user interactions:
- Updating configuration (does not change the local config file)
- Changing maze walls color
- Switching between 'demo' (regular display) and 'play' mode.
- Displaying viualizations for generation and solving.
- Toggle between multiple possible paths (if the maze is not perfect)

#### Algorithms

TODO
<!--Which algorithm and why we chose it-->
<!--Which algorithm and why we chose it-->
<!--Which algorithm and why we chose it-->
<!--Which algorithm and why we chose it-->
<!--Which algorithm and why we chose it-->
<!--Which algorithm and why we chose it-->

#### MazeGenerator class

The MazeGenerator class is a standalone module that can be imported and used in any project.<br>
The package is available as `mazegen-1.0.0-py3-none-any.whl` at the root of the project files.

TODO: MazeGenerator Readme
<!--MazeGenerator readme-->
<!--MazeGenerator readme-->
<!--MazeGenerator readme-->
<!--MazeGenerator readme-->
<!--MazeGenerator readme-->
<!--MazeGenerator readme-->
<!--MazeGenerator readme-->


#### Bonuses

- Menus and scenes
- Interactive display
- Hexagonal maze support
- Buttons, with hover animation
- Live configuration editing
- Animated maze generation
- Animated maze solving
- Multiple toggleable paths between entry and exit
- Play mode!

### Instructions

Install and run the project using the provided Makefile:

```shell
$> make install
# Installation... (may take a minute or two)
# ...
$> make run
# Starting 'a_maze_ing.py'...
```

Alternatively, you can run `make` to install, then run `make` again to run the project.<br>
Environment files automatically get installed in `/tmp/<your_user>_miniconda/`.

To check source code for programmatic and stylistic errors, run:

```shell
$> make lint
# Running mypy...
# ...
$> make lint-strict
# Running mypy --strict...
# ...
```

To remove any temporary files (`__pycache__` or `.mypy_cache`), run:

```shell
$> make clean
# Cleaning cache files...
```

To clean up installed environment files, run:

```shell
$> make fclean
# Removing Miniconda directory...
```

### Contribution

[<img src="https://contrib.rocks/image?repo=mpouillo/42-a-maze-ing">](https://github.com/mpouillo/42-a-maze-ing/graphs/contributors)

- **mpouillo**:

    - Makefile
    - Main program structure (MVC)
    - Display (Mlx)

- **acampion**:

    - Maze data manager
    - Maze generation
    - Maze solving

#### Notes

We divided the tasks at the very start of the project, allowing us to work mostly autonomously yet stay organized and make steady progress. Communication was required to merge the two parts of our project, but it went without a hitch.

While the current structure works decently well, it is far from optimal. However, it would require a full rewrite of the current code. Potential optimizations would include:

- Using numpy more to manage Mlx image buffers.
- Precomputing all maze cell configurations to write them faster to the buffer.
- Using pydantics to minimize error risk.

Beside the MiniLibX, no external tools were used.

### Resources

- Included Mlx man documentation
- [Unofficial Mlx docs](https://harm-smits.github.io/42docs/libs/minilibx)
- [XLIB mask documentation (for Mlx hooks)](https://tronche.com/gui/x/xlib/events/mask.html)
- AI was used to help structure the project (especially the MVC structure) and assist with adapting the square maze display into a hexagonal display.
