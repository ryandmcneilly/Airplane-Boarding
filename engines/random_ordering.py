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
