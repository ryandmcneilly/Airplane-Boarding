# Hack import trick for relative imports
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import util
from util import *
import random


class Random(AbpSolver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        result = random.sample(abp.passengers, len(abp.passengers))
        return AbpSolution(problem=abp, ordering=result)


if __name__ == "__main__":
    abp = AirplaneBoardingProblem(util.CURRENT_ABP_PROBLEM)
    rand_solver = Random()
    solution = rand_solver.solve(abp)
    solution.visualise_solution()
