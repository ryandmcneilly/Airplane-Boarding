from engines.max_settle_row import MaxSettleRow
from engines.outside_in_btf import OutsideInBTF
from engines.random_ordering import RandomSolver
from util import AirplaneBoardingProblem, Passenger, AbpSolution


def get_best_heuristic(abp: AirplaneBoardingProblem) -> AbpSolution:
    makespan: float = float("inf")
    solution: AbpSolution = ...

    for Heuristic in [MaxSettleRow, OutsideInBTF, RandomSolver]:
        heuristic_solution: AbpSolution = Heuristic().solve(abp)
        if heuristic_solution.makespan < makespan:
            makespan, solution = heuristic_solution.makespan, heuristic_solution

        print(Heuristic.__name__, f"found solution with {heuristic_solution.makespan:.0f} makespan")

    return solution
