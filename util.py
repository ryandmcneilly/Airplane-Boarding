from collections import namedtuple
from abc import ABC, abstractmethod
import time
import gurobipy as gp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

Passenger = namedtuple(
    "Passenger", ["row", "column", "settle_time", "move_times", "id"]
)


def time_taken_at_row(p: Passenger, r: int) -> int:
    if r <= p.row - 1:
        return p.move_times[r - 1]
    elif r == p.row:
        return p.settle_time
    elif r >= p.row + 1:
        return 0
    assert "Unreachable"


class AirplaneBoardingProblem:
    def __init__(self, filename: str):
        f = open(filename, "r")
        data = f.readlines()

        self.num_rows = int(data[0].split(" ")[1])
        self.num_cols = int(data[1].split(" ")[1])
        self.num_passengers = int(data[2].split(" ")[1])

        data = data[3:]

        self.passengers = [
            Passenger(
                id=i // 4,
                row=int(data[i].split(" ")[1]),
                column=int(data[i + 1].split(" ")[1]),
                settle_time=float(data[i + 2].split(" ")[1]),
                move_times=(
                    given_times := tuple(
                        float(time) for time in data[i + 3].split(" ")[1:]
                    )
                )
                + tuple(0 for _ in range(self.num_rows - len(given_times))),
            )
            for i in range(0, len(data), 4)
        ]

        self.order = range(1, len(self.passengers) + 1)
        self.rows = range(1, self.num_rows + 1)

        f.close()


class AbpSolution:
    def __init__(
        self,
        problem: AirplaneBoardingProblem,
        ordering: list[Passenger | None],
        *,
        makespan=None,
    ):
        self.problem = problem
        self.ordering = ordering

        self.computation_time = None
        self.makespan = makespan or self.simulate_boarding()

    def parse_json(self, filename: str):
        ...

    def simulate_boarding(self):
        abp = self.problem
        passenger_seated_times = [0 for _ in range(abp.num_passengers)]
        # Time a passenger enters a row
        passenger_enter_row = []
        # Stores the latest time a passenger has been in that row (blocking)
        row_blockage = [0 for _ in range(abp.num_rows + 1)]

        for i, p in enumerate(self.ordering):
            passenger_enter_row.append([0 for _ in range(p.row + 1)])

            for row in range(p.row + 1):
                # Maximum of either passenger moving or when the row becomes free
                passenger_enter_row[i][row] = (
                    row_blockage[0]
                    if row == 0
                    else max(
                        passenger_enter_row[i][row - 1] + p.move_times[row - 2],
                        row_blockage[row],
                    )
                )

                if row > 0:
                    row_blockage[row - 1] = passenger_enter_row[i][row]

                if row == p.row:
                    passenger_seated_time = passenger_enter_row[i][row] + p.settle_time
                    row_blockage[row] = passenger_seated_time
                    passenger_seated_times[i] = passenger_seated_time

        makespan = max(passenger_seated_times, default=0)
        return makespan

    def visualise_solution(self):
        self.print_solution()
        mapping = {(p.row, p.column): i for i, p in enumerate(self.ordering)}

        num_rows = max(row for row, _ in mapping)
        num_cols = max(col for _, col in mapping)

        mid_col = (num_cols // 2) + 1  # Determine where to insert the empty column

        # Create grid with an empty column in the middle
        grid = [
            [
                (
                    mapping.get((row, col if col < mid_col else col - 1), None)
                    if col != mid_col
                    else None
                )
                for col in range(1, num_cols + 2)
            ]
            for row in range(1, num_rows + 1)
        ]

        unique_chars = {char for row in grid for char in row if char is not None}
        color_map = {char: mcolors.CSS4_COLORS.get("pink") for char in unique_chars}
        empty_col_color = "lightgray"

        n_rows = len(grid)
        n_cols = len(grid[0])

        fig, ax = plt.subplots(figsize=(n_cols, n_rows))

        ax.set_title(f"Time to board: {self.makespan}")

        # Loop through and plot
        for i in range(n_rows):
            for j in range(n_cols):
                char = grid[i][j]
                color = (
                    color_map.get(char, empty_col_color)
                    if char is not None
                    else empty_col_color
                )
                ax.add_patch(plt.Rectangle((j, n_rows - i - 1), 1, 1, color=color))
                if char is not None:
                    ax.text(
                        j + 0.5,
                        n_rows - i - 1 + 0.5,
                        char,
                        ha="center",
                        va="center",
                        fontsize=12,
                        color="black",
                    )

        # Make plot look pretty
        ax.set_xlim(0, n_cols)
        ax.set_ylim(0, n_rows)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
        plt.show()

    def print_solution(self):
        [
            print(i, (p.row, p.column, p.move_times[0], p.settle_time))
            for i, p in enumerate(self.ordering)
        ]


class Solver(ABC):
    def solve(self, abp: AirplaneBoardingProblem):
        start = time.time()
        solution = self.solve_implementation(abp)
        solution.computation_time = time.time() - start
        solution.type = type(self).__name__
        return solution

    @abstractmethod
    def solve_implementation(
        self,
        abp: AirplaneBoardingProblem,
    ) -> AbpSolution: ...
