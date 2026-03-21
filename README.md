*This project has been created as part of the 42 curriculum by mpouillo, acampion.*

# 42-A-Maze-ing

### Description

The goal of *A-Maze-ing* is to create our own maze generator and display its result. This project requires learning algorithms for both generation and solving, library frameworks (MiniLibX) and how to structure a semi-large project.

This project is done in Python 3.10+. The maze generator takes a configuration file, generates a maze and writes it to a file using a hexadecimal wall representation.

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

### Configuration file

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

### Display

A visual display with user interaction is also available.<br>
The display uses the MiniLibX (MLX) library to connect to display drivers and provide a visual representation of the maze.

Available user interactions:
- Updating configuration (does not change the local config file)
- Changing maze walls color
- Switching between 'demo' (regular display) and 'play' mode.
- Displaying viualizations for generation and solving.
- Toggle between multiple possible paths (if the maze is not perfect)

### Algorithms

**Maze Generation: Randomized Depth-First Search (DFS)**

The maze is generated using a randomized version of the Depth-First Search (DFS) algorithm, often called the "recursive backtracker" method.

-   **Why this choice?** This algorithm is relatively simple to implement and produces high-quality mazes with long, winding corridors and few short dead ends. It guarantees that every cell in the maze is reachable, which is a key requirement. The use of a stack makes it memory-efficient for large mazes.

**Maze Solving: A* Search and Dead-End Filling**

For solving the maze, a combination of two techniques is used:

1.  **Dead-End Filling**: Before searching for a path, the algorithm first identifies and fills all dead ends in the maze. This is done by repeatedly finding cells with three walls and closing off their only exit until no more dead ends can be found. This process simplifies the maze, leaving only valid paths and loops.

2.  **A\* Search Algorithm**: After the maze is simplified, the A\* algorithm is used to find multiple paths between the entry and exit points.
    -   It first finds the shortest path.
    -   Then, it finds the longest possible path.
    -   Finally, it searches for several paths of intermediate lengths.

-   **Why this choice?** The A\* algorithm is highly efficient for pathfinding because it uses a heuristic (in this case, the Manhattan distance to the exit) to prioritize searching in the most promising direction. This makes it much faster than a simple Breadth-First Search (BFS) for finding the shortest path. Combining it with the dead-end filling pre-process and adapting it to find paths of varying lengths provides a powerful and flexible solution for both perfect and imperfect mazes.

**Creating Imperfect Mazes: Adding New Paths**

When the `PERFECT` configuration is set to `False`, the generator intentionally creates loops and alternative routes by adding new paths after the initial generation.

-   **How it's implemented:** This is achieved by "carving" new passages through existing walls. The process targets the longest dead-end paths found during the dead-end filling stage. By removing a wall at the end of a long dead-end, it connects to an adjacent corridor, effectively creating a loop or shortcut. This method ensures that new paths are meaningful and integrated into the maze structure, leading to more complex and interesting imperfect mazes.

### MazeGenerator Documentation

The MazeGenerator class is a standalone module that can be imported and used in any project.<br>
The package is available as `mazegen-1.0.0-py3-none-any.whl` at the root of the project files and can also be recreated by doing `make build_pkg`

It's the main interface for creating, solving, and managing mazes. It can generate both square and hexagonal mazes, find solutions, and save the results.


#### 1. Instantiation and Basic Usage

To use the `MazeGenerator`, you first need to set up the configuration using environment variables. Then, you can instantiate the class and call its methods to generate and access maze data.

##### Configuration

The generator is configured via environment variables. These are loaded from a `config.txt` file at the root of the project when running the application, but you can also set them manually in your script.


##### Example

Here is a basic example of how to generate a 10x10 square maze and save it.

```python
import os
from src.models.maze import MazeGenerator

# --- 1. Set up configuration ---
# The generator reads these from the environment.
os.environ['WIDTH'] = '10'
os.environ['HEIGHT'] = '10'
os.environ['ENTRY'] = '0,0'
os.environ['EXIT'] = '9,9'
os.environ['PERFECT'] = 'True'
os.environ['OUTPUT_FILE'] = 'my_maze.txt'

# --- 2. Instantiate the generator ---
# This will automatically load the configuration from the environment.
try:
    maze_generator = MazeGenerator()
except ValueError as e:
    print(f"Error initializing generator: {e}")
    exit()

# --- 3. Generate the maze ---
# This populates the maze data and saves it to the output file.
maze_generator.generate_new_maze()

print(f"Maze generated and saved to {maze_generator.output_file}")
```

#### 2. Accessing Maze Data

After calling `generate_new_maze()`, you can access the generated maze structure and its solutions directly from the `MazeGenerator` instance.

##### Accessing the Maze Structure

The maze is stored as a NumPy array where each cell is an integer representing its walls.

-   **`maze_generator.maze`**: A `numpy.ndarray` representing the final maze structure.
    -   For square mazes, walls are represented by a 4-bit integer (`NESW`).
    -   For hexagonal mazes, walls are represented by a 6-bit integer.

```python
# Access the generated maze grid
maze_grid = maze_generator.maze
print("Generated Maze Grid (first 5 rows):")
print(maze_grid[:5])
```

// ...existing code...
##### Accessing Solutions

The generator finds one or more valid paths from the entry to the exit.

-   **`maze_generator.valid_paths`**: A list of all found paths. Each path is a list of `(row, col)` coordinate tuples. The list is sorted by path length, with the shortest path first.

You can also save a specific solution path directly to the output file.

```python
# Get the shortest solution path
if maze_generator.valid_paths:
    shortest_path_coords = maze_generator.valid_paths[0]

    print(f"\nFound {len(maze_generator.valid_paths)} solution(s).")
    print(f"Shortest path has {len(shortest_path_coords)} steps.")

    # The save_solution method converts the coordinate path into a
    # directional string and appends it to the output file.
    maze_generator.save_solution(shortest_path_coords)
    print(f"Shortest solution saved to {maze_generator.output_file}.")
else:
    print("No solution was found.")
```


### Bonuses

- Menus and scenes
- Interactive display
- Hexagonal maze support
- Buttons, with hover animation
- Live configuration editing
- Animated maze generation
- Animated maze solving
- Multiple toggleable paths between entry and exit
- Play mode!

### Contribution

[<img src="https://contrib.rocks/image?repo=mpouillo/42-a-maze-ing">](https://github.com/mpouillo/42-a-maze-ing/graphs/contributors)

- **mpouillo**:

    - Makefile
    - Main program structure (MVC)
    - Display (MLX)

- **acampion**:

    - Maze data manager
    - Maze generation
    - Maze solving

### Notes

We divided the tasks at the very start of the project, allowing us to work mostly autonomously yet stay organized and make steady progress. Communication was required to merge the two parts of our project, but it went without a hitch.

While the current structure works decently well, it is far from optimal. However, it would require a full rewrite of the current code. Potential optimizations would include:

- Using numpy more to manage MLX image buffers.
- Precomputing all maze cell configurations to write them faster to the buffer.
- Using pydantics to minimize error risk.

Beside the MiniLibX, no external tools were used.

### Resources

- Included MLX man documentation
- [Unofficial MLX docs](https://harm-smits.github.io/42docs/libs/minilibx)
- [XLIB mask documentation (for MLX hooks)](https://tronche.com/gui/x/xlib/events/mask.html)
- AI was used to help structure the project (especially the MVC structure) and assist with adapting the square maze display into a hexagonal display.
