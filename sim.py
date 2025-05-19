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


def test_solvers_on_abp(filepath: AbpFilepath):
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
        )

        with open(
            f"results/{filepath.num_rows}_{filepath.num_columns}/{slug_algorithm}__mp_sp__{filepath.num_rows}_{filepath.num_columns}__{filepath.test_number}.json",
            "w+",
        ) as f:
            json.dump(result, f)


if __name__ == "__main__":
    for num_rows, num_cols in [(20, 2)]:
        for test_number in range(10):
            filepath = AbpFilepath(num_rows, num_cols, test_number)
            test_solvers_on_abp(filepath)
