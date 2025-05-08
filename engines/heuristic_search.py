from engines.max_settle_row import MaxSettleRow
from engines.outside_in_btf import OutsideInBTF
from engines.random_ordering import RandomSolver
from util import AirplaneBoardingProblem, Passenger


def get_best_heuristic(abp: AirplaneBoardingProblem) -> tuple[int, list[Passenger]]:
    makespan: float = float("inf")
    ordering: list[Passenger] = ...
    for Heuristic in [MaxSettleRow, OutsideInBTF, RandomSolver]:
        solution = Heuristic().solve(abp)
        heuristic_makespan = solution.simulate_boarding()
        if heuristic_makespan < makespan:
            makespan, ordering = heuristic_makespan, solution.ordering

        print(Heuristic.__name__, f"found solution with {heuristic_makespan:.0f} makespan")

    return int(makespan), ordering
