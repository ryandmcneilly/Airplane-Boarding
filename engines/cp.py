import copy

from ortools.sat.python import cp_model

import util
from engines import mip
from engines.heuristic_search import get_best_heuristic
from util import (
    AbpSolver,
    AirplaneBoardingProblem,
    AbpSolution,
    Passenger,
    time_taken_at_row,
    discretise,
    TIME_LIMIT,
)


def get_wait_times(abp: AirplaneBoardingProblem, sol: AbpSolution):
    m, X, TF = mip.MIP.build_model(abp)
    for i, p in enumerate(sol.ordering, start=1):
        X[p, i].lb = 1

    m.params.TimeLimit = TIME_LIMIT

    m.optimize()

    # Translate TF[i, r] to TF[p, r]
    return {
        (next(p for p in abp.passengers if round(X[p, i].x) == 1), r): discretise(v.x)
        for (i, r), v in TF.items()
    }


def earliest_finish_time_to_row(passenger: Passenger, row: int) -> int:
    # Smallest arrival time for passenger to that given row
    return int(sum(time_taken_at_row(passenger, r) for r in range(1, row + 1)))


def constant_move_times_per_passenger_abp(abp: AirplaneBoardingProblem):
    new_passengers = [
        Passenger(
            row=p.row,
            column=p.column,
            move_times=(min(move_time for move_time in p.move_times),)
            * len(p.move_times),
            settle_time=p.settle_time,
            id=p.id,
        )
        for p in abp.passengers
    ]

    slow_abp = copy.copy(abp)
    slow_abp.passengers = new_passengers
    return slow_abp


class CP(AbpSolver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        slow_abp: AirplaneBoardingProblem = constant_move_times_per_passenger_abp(abp)

        lb_solution = get_best_heuristic(slow_abp)
        print(f"Lower bound solution of: {lb_solution.makespan}")

        ub_solution: AbpSolution = get_best_heuristic(abp)
        print(f"Upper bound solution of: {ub_solution.makespan}")
        heuristic_finish_times = get_wait_times(abp, ub_solution)

        m = cp_model.CpModel()

        R0 = [0] + list(abp.rows)

        # Variables --------------------------------------
        CMax = m.new_int_var(
            lb=discretise(lb_solution.makespan),
            ub=discretise(ub_solution.makespan),
            name="CMax",
        )
        m.add_hint(CMax, discretise(ub_solution.makespan))

        TF = {
            (p, r): m.new_int_var(
                lb=earliest_finish_time_to_row(p, r),
                ub=discretise(ub_solution.makespan),
                name=f"TF_({p.row},{p.column}),{r}",
            )
            for p in abp.passengers
            for r in R0
            if r <= p.row
        }
        for p, r in TF:
            if r > 0:
                m.add_hint(TF[p, r], heuristic_finish_times[p, r])

        W = {
            (p, r): m.new_int_var(
                lb=time_taken_at_row(p, r),
                ub=discretise(ub_solution.makespan),
                name=f"W_({p.row},{p.column}), {r}",
            )
            for p in abp.passengers
            for r in R0
            if r < p.row
        }
        for p, r in W:
            if r > 1:
                m.add_hint(
                    W[p, r],
                    heuristic_finish_times[p, r] - heuristic_finish_times[p, r - 1],
                )

        I = {
            (p, r): m.new_interval_var(
                start=TF[p, r - 1],
                end=TF[p, r],
                size=W[p, r] if r < p.row else p.settle_time,
                name=f"I_({p.row},{p.column}),{r}",
            )
            for p in abp.passengers
            for r in abp.rows
            if r <= p.row
        }

        # Subject to --------------------------------------
        NoOverlap = {
            r: m.add_no_overlap(I[p, r] for p in abp.passengers if (p, r) in I)
            for r in abp.rows
        }

        SetMakeSpan = m.add_max_equality(CMax, TF.values())

        # Objective --------------------------------------
        m.minimize(CMax)

        # Result --------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.linearization_level = 0  # no_lp
        solver.parameters.log_search_progress = True
        solver.parameters.num_workers = 8
        solver.parameters.max_time_in_seconds = TIME_LIMIT
        status = solver.solve(m)

        result = [
            p
            for (p, r), time in sorted(
                TF.items(), key=lambda item: solver.value(item[1])
            )
            if r == 0
        ]

        finish_times = {
            (p, r): solver.value(TF[p, r])
            for p in result
            for r in abp.rows
            if r <= p.row
        }
        return AbpSolution(
            abp,
            result,
            makespan=solver.value(CMax),
            finish_times=finish_times,
            range_=(solver.best_objective_bound / 10, solver.objective_value / 10),
        )


if __name__ == "__main__":
    abp = AirplaneBoardingProblem(util.CURRENT_ABP_PROBLEM)
    cp_solver = CP()

    cp_solution = cp_solver.solve(abp)
    cp_solution.visualise_solution()
