from ortools.sat.python import cp_model

import util
from engines.heuristic_search import get_best_heuristic
from engines.two_opt_search import two_opt_search
from util import (
    AbpSolver,
    AirplaneBoardingProblem,
    AbpSolution,
    Passenger,
    time_taken_at_row,
)


def earliest_finish_time_to_row(passenger: Passenger, row: int) -> int:
    # Smallest arrival time for any passenger to that given row
    return int(sum(time_taken_at_row(passenger, r) for r in range(1, row + 1)))

# def lower_bound_on_boarding(abp: AirplaneBoardingProblem):
#     # Assume every passenger has move speeds as the slowest passenger
#     smallest_move_time = min(time for p in abp.passengers for time in p.move_times if time > 0)
#     smallest_settle_time = min(p.settle_time for p in abp.passengers)
#
#     new_passengers = [
#         Passenger(
#             row=row,
#             column=col,
#             move_times=[smallest_move_time]
#
#         )
#         for row in abp.rows for col in range(1, abp.num_cols+1)
#     ]


class CP(AbpSolver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        m = cp_model.CpModel()

        heuristic_solution: AbpSolution = two_opt_search(abp, get_best_heuristic(abp))

        R0 = [0] + list(abp.rows)

        # Variables --------------------------------------
        CMax = m.new_int_var(
            lb=max(
                earliest_finish_time_to_row(p, abp.num_rows) for p in abp.passengers
            ),
            ub=heuristic_solution.makespan,
            name="CMax",
        )
        m.add_hint(CMax, heuristic_solution.makespan)

        TF = {
            (p, r): m.new_int_var(
                lb=earliest_finish_time_to_row(p, r),
                ub=heuristic_solution.makespan,
                name=f"TF_({p.row},{p.column}),{r}",
            )
            for p in abp.passengers
            for r in R0
            if r <= p.row
        }
        for i, p in enumerate(heuristic_solution.ordering):
            for r in range(p.row):
                m.add_hint(TF[p, r], heuristic_solution.passenger_enter_row[i][r + 1])

        W = {
            (p, r): m.new_int_var(
                lb=time_taken_at_row(p, r),
                ub=heuristic_solution.makespan,
                name=f"W_({p.row},{p.column}), {r}",
            )
            for p in abp.passengers
            for r in R0
            if r <= p.row
        }

        I = {
            (p, r): m.new_interval_var(
                start=TF[p, r - 1],
                end=TF[p, r],
                size=W[p, r],
                name=f"I_({p.row},{p.column}),{r}",
            )
            for p in abp.passengers
            for r in abp.rows
            if r <= p.row
        }

        # Subject to --------------------------------------
        PreserveOrder = {
            (p, r): m.add(TF[p, r] >= TF[p, r - 1] + time_taken_at_row(p, r))
            for p in abp.passengers
            for r in abp.rows
            if r <= p.row
        }

        PreserveOrder = {
            (p, r): m.add(W[p, r] >= time_taken_at_row(p, r))
            for p in abp.passengers
            for r in abp.rows
            if r <= p.row
        }

        NoOverlap = {
            r: m.add_no_overlap(I[p, r] for p in abp.passengers if (p, r) in I)
            for r in abp.rows
        }

        SetMakeSpan = m.add_max_equality(CMax, TF.values())

        # Objective --------------------------------------
        m.minimize(CMax)

        # Result --------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True
        solver.parameters.num_workers = 8
        solver.parameters.max_time_in_seconds = 60 * 60
        status = solver.solve(m)

        result = [
            p
            for (p, r), time in sorted(
                TF.items(), key=lambda item: solver.value(item[1])
            )
            if r == 1
        ]
        return AbpSolution(abp, result, makespan=solver.value(CMax), timed_out=status == cp_model.FEASIBLE)


if __name__ == "__main__":
    abp = AirplaneBoardingProblem(util.CURRENT_ABP_PROBLEM)
    cp_solver = CP()

    cp_solution = cp_solver.solve(abp)
    cp_solution.visualise_solution()

