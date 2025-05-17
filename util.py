import json
import os.path
from collections import namedtuple
from abc import ABC, abstractmethod
import time
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import plotly.express as px

Passenger = namedtuple(
    "Passenger", ["row", "column", "settle_time", "move_times", "id"]
)

AbpFilePath = namedtuple(
    "AbpFilePath", ["num_rows", "k", "test_number"]
)
CURRENT_ABP_PROBLEM = AbpFilePath(num_rows=10, k=2, test_number=0)


def time_taken_at_row(p: Passenger, r: int) -> int:
    if r <= p.row - 1:
        return int(p.move_times[r - 1])
    elif r == p.row:
        return int(p.settle_time)
    elif r >= p.row + 1:
        return 0
    assert "Unreachable"


class AirplaneBoardingProblem:
    def __init__(self, filepath: AbpFilePath):
        num_rows, k, test_num = filepath
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, f"data/mp_sp/{num_rows}_{k}/mp_sp__{num_rows}_{k}__{test_num}.json")
        f = open(filename, "r")
        json_data = json.load(f)
        self.filepath = filepath
        self.num_rows: int = len(json_data["n_seats_row"])
        self.num_cols: int = len(json_data["n_seats_row"][0])
        self.num_passengers: int = len(json_data["times_move"])

        self.passengers: list[Passenger] = [
            Passenger(
                id=i,
                row=json_data["pax_seats"][i][0] + 1,
                column=json_data["pax_seats"][i][1] + 1,
                settle_time=int(10 * json_data["times_clear"][i]),
                move_times=(
                    given_times := tuple(
                        10 * m_time for m_time in json_data["times_move"][i]
                    )
                )
                + tuple(0 for _ in range(self.num_rows - len(given_times))),
            )
            for i in range(self.num_passengers)
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

    def simulate_boarding(self) -> int:
        abp = self.problem
        passenger_seated_times = [0 for _ in range(abp.num_passengers)]
        # Time a passenger enters a row
        self.passenger_enter_row = []
        # Stores the latest time a passenger has been in that row (blocking)
        row_blockage = [0 for _ in range(abp.num_rows + 1)]

        for i, p in enumerate(self.ordering):
            self.passenger_enter_row.append([0 for _ in range(p.row + 1)])

            for row in range(p.row + 1):
                # Maximum of either passenger moving or when the row becomes free
                self.passenger_enter_row[i][row] = (
                    row_blockage[0]
                    if row == 0
                    else max(
                        self.passenger_enter_row[i][row - 1] + p.move_times[row - 2],
                        row_blockage[row],
                    )
                )

                if row > 0:
                    row_blockage[row - 1] = self.passenger_enter_row[i][row]

                if row == p.row:
                    passenger_seated_time = (
                        self.passenger_enter_row[i][row] + p.settle_time
                    )
                    row_blockage[row] = passenger_seated_time
                    passenger_seated_times[i] = passenger_seated_time

        makespan = max(passenger_seated_times, default=0)
        return int(makespan)

    def make_solution_plot(self):
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

    def make_gantt_chart(self):
        df = pd.DataFrame(
            [
                dict(
                    Task=f"Passenger {p.row, p.column}",
                    Start=self.passenger_enter_row[i][r],
                    Delta=self.passenger_enter_row[i][r + 1],
                    Resource=f"Row {r+1}",
                )
                for i, p in enumerate(self.ordering)
                for r in range(len(self.passenger_enter_row[i]) - 1)
            ]
        )
        df["Finish"] = df["Delta"] - df["Start"]

        filepath = self.problem.filepath
        title = f"ABP problem: Rows={filepath.num_rows}, k={filepath.k}, TestNumber={filepath.test_number}"
        fig = px.bar(
            df, base="Start", x="Finish", y="Resource", color="Task", orientation="h", title=title
        )

        fig.update_yaxes(autorange="reversed")
        fig.show()

    def visualise_solution(self):
        self.simulate_boarding()
        # self.print_solution()
        # self.make_solution_plot()
        self.make_gantt_chart()
        print(f"Solved in {self.computation_time:.2f}s")
        print("Makespan", self.makespan / 10)

    def print_solution(self):
        print("Found solution with makespan", self.makespan / 10)
        [
            print(i, (p.row, p.column, p.move_times[0], p.settle_time))
            for i, p in enumerate(self.ordering)
        ]


class AbpSolver(ABC):
    def solve(self, abp: AirplaneBoardingProblem) -> AbpSolution:
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
