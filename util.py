from collections import namedtuple

import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

Passenger = namedtuple("Passenger", ["row", "column", "settle_time", "move_times", "id"])
Plane = namedtuple("Plane", ["num_rows", "num_cols", "num_passengers"])

def visualise_res(res, obj_val=None):
    mapping = {(p.row, p.column): i for i, p in enumerate(res)}

    num_rows = max(row for row, _ in mapping)
    num_cols = max(col for _, col in mapping)

    mid_col = (num_cols // 2) + 1  # Determine where to insert the empty column

    # Create grid with an empty column in the middle
    grid = [[mapping.get((row, col if col < mid_col else col - 1), None) if col != mid_col else None
             for col in range(1, num_cols + 2)]
            for row in range(1, num_rows + 1)]

    unique_chars = {char for row in grid for char in row if char is not None}
    color_map = {char: mcolors.CSS4_COLORS.get("pink") for char in unique_chars}
    empty_col_color = "lightgray"

    n_rows = len(grid)
    n_cols = len(grid[0])

    fig, ax = plt.subplots(figsize=(n_cols, n_rows))

    if obj_val is not None:
        ax.set_title(f"Time to board: {obj_val}")

    # Loop through and plot
    for i in range(n_rows):
        for j in range(n_cols):
            char = grid[i][j]
            color = color_map.get(char, empty_col_color) if char is not None else empty_col_color
            ax.add_patch(plt.Rectangle((j, n_rows - i - 1), 1, 1, color=color))
            if char is not None:
                ax.text(j + 0.5, n_rows - i - 1 + 0.5, char, ha='center', va='center', fontsize=12, color='black')

    # Make plot look pretty
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.show()


def print_res(res: list[Passenger]):
    [print(i, (p.row, p.column, p.move_times[0])) for i, p in enumerate(res)]
