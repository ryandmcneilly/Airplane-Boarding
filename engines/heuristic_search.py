from engines.max_settle_row import MaxSettleRow
from engines.outside_in_btf import OutsideInBTF
from engines.random_ordering import Random
from engines.two_opt_search import two_opt_search
from util import AirplaneBoardingProblem, Passenger, AbpSolution


def get_best_heuristic(abp: AirplaneBoardingProblem) -> AbpSolution:
    makespan: float = float("inf")
    solution: AbpSolution = ...

    for Heuristic in [MaxSettleRow, OutsideInBTF, Random]:
        heuristic_solution: AbpSolution = Heuristic().solve(abp)
        two_opt_sol: AbpSolution = two_opt_search(abp, heuristic_solution)
        if two_opt_sol.makespan < makespan:
            makespan, solution = two_opt_sol.makespan, two_opt_sol

        print(Heuristic.__name__, f"found solution with {two_opt_sol.makespan:.0f} makespan")

    return solution
