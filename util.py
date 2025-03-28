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
    grid = [[mapping[row,col] for row in range(1, num_rows+1)] for col in range(1, num_cols+1) ]


    # give some random colours
    unique_chars = set(char for row in grid for char in row)

    color_map = {char: mcolors.CSS4_COLORS.get("pink") for char in unique_chars}

    # color_map = {char: random.choice(list(mcolors.CSS4_COLORS.values())) for char in unique_chars}

    n_rows = len(grid)
    n_cols = len(grid[0])

    fig, ax = plt.subplots(figsize=(n_cols, n_rows))

    if obj_val is not None:
        ax.set_title(f"Time to board: {obj_val}")

    # loop through and plot
    for i in range(n_rows):
        for j in range(n_cols):
            char = grid[i][j]
            # colour and label
            ax.add_patch(plt.Rectangle((j, n_rows - i - 1), 1, 1, color=color_map[char]))
            ax.text(j + 0.5, n_rows - i - 1 + 0.5, char, ha='center', va='center', fontsize=12, color='black')

    # make plot look pretty
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.show()

def print_res(res: list[Passenger]):
    [print(i, (p.row, p.column, p.move_times[0])) for i, p in enumerate(res)]
