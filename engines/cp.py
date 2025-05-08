from ortools.sat.python import cp_model

from engines.heuristic_search import get_best_heuristic
from util import (
    Solver,
    AirplaneBoardingProblem,
    AbpSolution,
    Passenger,
    time_taken_at_row,
)


def earliest_finish_time_to_row(passenger: Passenger, row: int) -> int:
    # Smallest arrival time for any passenger to that given row
    return int(sum(
        time_taken_at_row(passenger, r) for r in range(1, row + 1)
    ))




class CPSolver(Solver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        m = cp_model.CpModel()

        heuristic_makespan, heuristic_solution = get_best_heuristic(abp)

        R0 = [0] + list(abp.rows)

        # Variables --------------------------------------
        CMax = m.new_int_var(lb=max(earliest_finish_time_to_row(p, abp.num_rows) for p in abp.passengers), ub=heuristic_makespan, name="CMax")
        m.add_hint(CMax, heuristic_makespan)

        TF = {
            (p, r): m.new_int_var(lb=earliest_finish_time_to_row(p, r) if r <= p.row else 0, ub=heuristic_makespan, name=f"TF_({p.row},{p.column}),{r}")
            for p in abp.passengers
            for r in R0
        }
        for i, p in enumerate(heuristic_solution.ordering):
            for r in range(p.row):
                m.add_hint(TF[p, r], heuristic_solution.passenger_enter_row[i][r+1])


        W = {
            (p, r): m.new_int_var(lb=0, ub=heuristic_makespan, name=f"W_({p.row},{p.column}), {r}")
            for p in abp.passengers
            for r in R0
            if r <= p.row
        }

        I = {
            (p, r): m.new_interval_var(
                start=TF[p, r - 1], end=TF[p, r], size=W[p, r], name=f"I_({p.row},{p.column}),{r}"
            )
            for p in abp.passengers
            for r in abp.rows
            if r <= p.row
        }

        # Subject to --------------------------------------
        SetW = {
            (p, r): m.add(W[p, r] == TF[p, r] - TF[p, r - 1])
            for p in abp.passengers
            for r in abp.rows
            if r <= p.row
        }

        passenger_at_row_cost = {
            (p, r): int(time_taken_at_row(p, r))
            for p in abp.passengers
            for r in abp.rows
        }

        PreserveOrder = {
            (p, r): m.add(TF[p, r] >= TF[p, r - 1] + passenger_at_row_cost[p, r])
            for p in abp.passengers
            for r in abp.rows
        }

        NoOverlap = {
            r: m.add_no_overlap([I[p, r] for p in abp.passengers if (p, r) in I])
            for r in abp.rows
        }

        SetMakeSpan = m.add_max_equality(CMax, TF.values())

        # Objective --------------------------------------
        m.minimize(CMax)

        # Result --------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True
        solver.solve(m)

        result = [
            p
            for (p, r), time in sorted(
                TF.items(), key=lambda item: solver.value(item[1])
            )
            if r == 1
        ]
        return AbpSolution(abp, result, makespan=solver.value(CMax))


if __name__ == "__main__":
    abp = AirplaneBoardingProblem(f"../data/mp_sp/10_2/mp_sp__10_2__1.json")
    cp_solver = CPSolver()

    cp_solution = cp_solver.solve(abp)
    print(f"Solved in {cp_solution.computation_time:.2f}s")
    print("Makespan", cp_solution.makespan)
