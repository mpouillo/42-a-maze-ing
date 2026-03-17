# MazeGenerator Documentation

The `MazeGenerator` class is the main interface for creating, solving, and managing mazes. It can generate both square and hexagonal mazes, find solutions, and save the results.

## 1. Instantiation and Basic Usage

To use the `MazeGenerator`, you first need to set up the configuration using environment variables. Then, you can instantiate the class and call its methods to generate and access maze data.

### Configuration

The generator is configured via environment variables. These are loaded from a `config.txt` file at the root of the project when running the application, but you can also set them manually in your script.

| Key         | Description                | Example      |
|-------------|----------------------------|--------------|
| `WIDTH`     | Maze width in cells        | `20`         |
| `HEIGHT`    | Maze height in cells       | `20`         |
| `ENTRY`     | Entry coordinates (row,col)| `0,0`        |
| `EXIT`      | Exit coordinates (row,col) | `19,19`      |
| `PERFECT`   | `True` for a single path   | `True`       |
| `SEED`      | Seed for random generation | `42`         |
| `HEX`       | `True` for hexagonal maze  | `False`      |
| `OUTPUT_FILE`| File to save the maze to   | `maze.txt`  |

### Example

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

## 2. Accessing Maze Data

After calling `generate_new_maze()`, you can access the generated maze structure and its solutions directly from the `MazeGenerator` instance.

### Accessing the Maze Structure

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

### Accessing Solutions

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