# Hack import trick for relative imports
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import util
from util import *
import itertools


class OutsideInBTF(AbpSolver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        column_groups = [
            [p for p in abp.passengers if p.column == col]
            for col in range(1, abp.num_cols + 1)
        ]

        result = list(
            itertools.chain.from_iterable(
                [
                    sorted(column_groups[col], key=lambda p: p.row, reverse=True)
                    for col in range(len(column_groups))
                ]
            )
        )

        return AbpSolution(abp, result)


if __name__ == "__main__":
    abp = AirplaneBoardingProblem(util.CURRENT_ABP_PROBLEM)

    outside_in_btf = OutsideInBTF()
    sol = outside_in_btf.solve(abp)
    sol.visualise_solution()
