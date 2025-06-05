"""File for comparing different models in speed"""

import util
from engines import cp
from engines.cp import CP
from engines.max_settle_row import MaxSettleRow
from engines.mip import MIP
from engines.outside_in_btf import OutsideInBTF
from engines.random_ordering import Random
from util import AirplaneBoardingProblem, AbpFilepath, AbpSolver, AbpSolution
import re
import json

abp_slug = lambda name: name.lower()


def run_solvers_on_abp(filepath: AbpFilepath):
    # Run solvers on filepath and make a json
    solvers: list[AbpSolver] = [CP()]
    # solvers = [MIP()]
    for solver in solvers:
        abp = AirplaneBoardingProblem(filepath)
        solution: AbpSolution = solver.solve(abp)

        instance_name = (
            f"mp_sp__{filepath.num_rows}_{filepath.num_columns}__{filepath.test_number}"
        )
        slug_algorithm = abp_slug(type(solver).__name__)
        result = dict(
            algorithm=slug_algorithm,
            computation_time=solution.computation_time,
            instance_name=instance_name,
            objective_value=solution.makespan,
            order=[p.id for p in solution.ordering if p],
            lower_bound=solution.lower_bound or "N/A",
            upper_bound=solution.upper_bound or "N/A",
            gap=((abs(solution.upper_bound - solution.lower_bound) / abs(solution.upper_bound)) * 100) if solution.lower_bound else "N/A"
        )

        with open(
            f"results/{filepath.num_rows}_{filepath.num_columns}/{slug_algorithm}__mp_sp__{filepath.num_rows}_{filepath.num_columns}__{filepath.test_number}.json",
            "w+",
        ) as f:
            json.dump(result, f)


def print_data_set_results(num_rows: int, num_cols: int):
    folder_path = f"results/{num_rows}_{num_cols}"
    print(f"{'file':38} {'lower_bound':>12} {'upper_bound':>12} {'gap (%)':>8} {'objective':>12} {'time (s)':>10}")

    round_decimal = lambda val: f"{val:.2f}" if not (val in ["N/A", INVALID]) else INVALID
    for filename in sorted(os.listdir(folder_path)):
        if not filename.endswith(".json"):
            continue
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as file:
            data = json.load(file)

            lb = round_decimal(data.get("lower_bound", INVALID))
            ub = round_decimal(data.get("upper_bound", INVALID))
            gap = round_decimal(data.get("gap", INVALID))
            objective_value = round_decimal(data.get("objective_value", INVALID))
            computation_time = round_decimal(data.get("computation_time", INVALID))

            print(f"{filename:38} {lb:>12} {ub:>12} {gap:>8} {objective_value:>12} {computation_time:>10}")

if __name__ == "__main__":
    # [(10, 4), (10, 6), (20, 4), (20, 6), (30, 2), (30, 4), (30, 6)]
    for num_rows, num_cols in [(10, 6)]:
        for test_number in range(10):
            filepath = AbpFilepath(num_rows, num_cols, test_number)
            run_solvers_on_abp(filepath)
    print_data_set_results(20, 2)