import util
from util import *
import itertools

class MaxSettleRow(AbpSolver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        row_groups = [
            sorted([p for p in abp.passengers if p.row == row], key=lambda p: p.settle_time, reverse=True)
            for row in range(abp.num_rows, 0, -1)
        ]

        result = list(itertools.chain.from_iterable(
            zip(*row_groups)
        ))

        return AbpSolution(abp, result)

if __name__ == "__main__":
    abp = AirplaneBoardingProblem(util.CURRENT_ABP_PROBLEM)

    mip_solver = MaxSettleRow()
    mip_solution = mip_solver.solve(abp)
    mip_solution.visualise_solution()
