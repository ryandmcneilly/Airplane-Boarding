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

abp_slug = lambda name: re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def test_solvers_on_abp(filepath: AbpFilepath):
    # Run solvers on filepath and make a json
    # solvers: list[AbpSolver] = [OutsideInBTF(), MaxSettleRow(), Random(), CP()]
    solvers = [MIP()]
    for solver in solvers:
        abp = AirplaneBoardingProblem(filepath)
        solution: AbpSolution = solver.solve(abp)

        instance_name = f"mp_sp__{filepath.num_rows}_{filepath.num_columns}__{filepath.test_number}"
        slug_algorithm = abp_slug(type(solver).__name__)
        result = dict(
            algorithm=slug_algorithm,
            computation_time=solution.computation_time,
            instance_name=instance_name,
            objective_value=solution.makespan,
            order=[p.id for p in solution.ordering if p],
        )

        with open(f"results/{filepath.num_rows}_{filepath.num_columns}/{slug_algorithm}__mp_sp__{filepath.num_rows}_{filepath.num_columns}__{filepath.test_number}.json", "w+") as f:
            json.dump(result, f)






# def main():
#     solvers: list[AbpSolver] = [MIPAbpSolver()]
#     solutions: list[list[AbpSolution]] = [[] for _ in range(len(solvers))]
#     for i, solver in enumerate(solvers):
#         for test_num in range(1):
#             abp = AirplaneBoardingProblem(AbpFilePath(10, 2, test_num+1))
#             solution: AbpSolution = solver.solve(abp)
#             solutions[i].append(solution)
#
#     for i, solver in enumerate(solvers):
#         filepath: AbpFilePath = solutions[i][0].problem.filepath
#         results_file = open(f"./results/{type(solver).__name__}/{filepath.num_rows}_{filepath.num_columns}.abp", "w+")
#         results_file.write(type(solver).__name__ + "\n")
#         print(type(solver).__name__)
#         for test_num, solution in enumerate(solutions[i]):
#             print(f"    {test_num}: {'TIMED OUT SOLUTION' * solution.timed_out} {solution.computation_time}")
#             results_file.write(f"\t{test_num}: {'TIMED OUT SOLUTION' * solution.timed_out} {solution.computation_time}")
#
#         print(f"    avg: {sum(solution.computation_time for solution in solutions[i]) / len(solutions[i])}")
#         results_file.write(f"\tavg: {sum(solution.computation_time for solution in solutions[i]) / len(solutions[i])}")


if __name__ == "__main__":
    for num_rows in [10]:
        for num_cols in [2, 4, 6]:
            for test_number in range(10):
                filepath = AbpFilepath(num_rows, num_cols, test_number)
                test_solvers_on_abp(filepath)
