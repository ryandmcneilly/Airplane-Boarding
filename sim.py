"""File for comparing different models in speed"""
import util
from engines import cp
from engines.cp import CPAbpSolver
from engines.max_settle_row import MaxSettleRow
from engines.mip import MIPAbpSolver
from engines.outside_in_btf import OutsideInBTF
from engines.random_ordering import RandomAbpSolver
from util import AirplaneBoardingProblem, AbpFilePath, AbpSolver, AbpSolution


def main():
    solvers: list[AbpSolver] = [CPAbpSolver(), RandomAbpSolver(), MaxSettleRow(), OutsideInBTF()]
    solutions = [[] for _ in range(len(solvers))]
    for i, solver in enumerate(solvers):
        for test_num in range(10):
            abp = AirplaneBoardingProblem(AbpFilePath(10, 2, test_num))
            solution: AbpSolution = solver.solve(abp)
            solutions[i].append(solution)

    for i, solver in enumerate(solvers):
        print(solver.__name__)
        for solution in solutions[i]:
            print(f"    {i}: {solution.makespan}")
        print(f"    avg: {sum(solution.makespan for solution in solutions) / len(solutions[i])}")


if __name__ == "__main__":
    main()