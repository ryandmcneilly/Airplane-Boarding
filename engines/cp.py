from ortools.sat.python import cp_model

from util import Solver, AirplaneBoardingProblem, AbpSolution, Passenger, time_taken_at_row


def earliest_arrival_time_to_row(passengers: list[Passenger], row: int) -> int:
    # Smallest arrival time for any passenger to that given row
    return min(
        sum(time_taken_at_row(passenger, r) for r in range(row)) # Dont want to include time taken at that row, just the cumsum to get to it
        for passenger in passengers if passenger.row >= row      # We only care about passengers that will go to that row
    )

def latest_finish_time_at_row(passengers: list[Passenger], row: int) -> int:
    return 1000 # fix this


class CPSolver(Solver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        m = cp_model.CpModel()

        # If passenger p is allocated to position i
        X = {(p, i): m.new_bool_var(name=f"X_{p},{i}") for p in abp.passengers for i in abp.order}

        # Makespan variable
        CMax = m.new_int_var(0, 100000, name="CMax")

        # Time p arrives r
        TA = {(i, r):
            m.new_int_var(
                lb=int(earliest_arrival_time_to_row(abp.passengers, r)),
                ub=latest_finish_time_at_row(abp.passengers, r),
                name=f"TA_{i},{r}")
            for i in abp.order for r in abp.rows
        }

        # Interval variable for how long p is at r
        IPR = {(i, p, r):
            m.new_optional_fixed_size_interval_var(
                   start=TA[i, r],
                   size=int(time_taken_at_row(p, r)),
                   is_present=X[p, i],
                   name=f"IPR_{p},{r}"
            )
            for p in abp.passengers for r in abp.rows if p.row >= r for i in abp.order
        }

        PlacePassengerInQueue = {p:
            m.add_exactly_one([X[p, i] for i in abp.order])
            for p in abp.passengers
        }

        EachQueuePositionIsFilled = {i:
            m.add_exactly_one([X[p, i] for p in abp.passengers])
            for i in abp.order
        }

        # Ensure no row has two passengers
        NoOverlapAtRow = {r:
            m.add_no_overlap(
                [IPR[i, p, r] for p in abp.passengers if p.row >= r for i in abp.order]
            ) for r in abp.rows
        }

        OrderPreserved = {(i, r):
            m.add(TA[i-1, r] <= TA[i, r]) for i in abp.order[1:] for r in abp.rows
        }

        finish_times = [
            TA[i, p.row] + int(time_taken_at_row(p, p.row))
            for p in abp.passengers for i in abp.order
        ]

        SetMakeSpan = m.add_max_equality(CMax, finish_times)

        # Objective
        m.minimize(CMax)

        solver = cp_model.CpSolver()
        status = solver.solve(m)

        result = [None for _ in range(len(abp.passengers))]
        for (p, i) in X:
            if solver.value(X[p, i]):
                result[i-1] = p
        return AbpSolution(abp, result, makespan=solver.value(CMax))



if __name__ == "__main__":
    abp = AirplaneBoardingProblem("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")

    cp_solver = CPSolver()
    cp_solution = cp_solver.solve(abp)
    cp_solution.print_solution()
    cp_solution.visualise_solution()

