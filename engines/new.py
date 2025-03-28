from collections import namedtuple
from abc import ABC
import time
import random
import gurobipy as gp

Passenger = namedtuple(
    "Passenger", ["row", "column", "settle_time", "move_times", "id"]
)


def time_taken_at_row(p: Passenger, r: int):
    if r <= p.row - 1:
        return p.move_times[r]
    elif r == p.row:
        return p.settle_time
    elif r >= p.row + 1:
        return 0
    assert "Unreachable"


# def build_model(filename: str):
#     m = gp.Model("Paper Airplane Boarding")
#
#     # Sets & Data
#     Passengers, Plane = parse_file(filename)
#     Order = range(1, len(Passengers) + 1)
#     R = range(1, Plane.num_rows + 1)
#
#     # Variables
#     # X[p, i] <=> pi(p) = i
#     X = {(p, i): m.addVar(vtype=gp.GRB.BINARY) for p in Passengers for i in Order}
#
#     # passenger pi^-1(i) arrives at row r
#     TimeArrival = {
#         (i, r): m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0) for i in Order for r in R
#     }
#     # passenger pi^-1(i) finishes actions at row r
#     TimeFinish = {
#         (i, r): m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0) for i in Order for r in R
#     }
#
#     # Makepsan variable. This is bounded below by the last finish time TimeFinish[i, R]
#     CompletionTime = m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0)
#
#     # Objective - Minimise makespan
#     m.setObjective(CompletionTime, gp.GRB.MINIMIZE)
#
#     OrderMustBeFilled = {
#         i: m.addConstr(gp.quicksum(X[p, i] for p in Passengers) == 1) for i in Order
#     }
#
#     # Constraints
#     OnePassengerOnePositionInOrder = {
#         p: m.addConstr(gp.quicksum(X[p, i] for i in Order) == 1) for p in Passengers
#     }
#
#     CompletionTimeSmallestFinish = {
#         i: m.addConstr(CompletionTime >= TimeFinish[i, Plane.num_rows]) for i in Order
#     }
#
#     ArriveNextRowBeforeCurrent = {
#         (i, r): m.addConstr(TimeArrival[i, r + 1] - TimeFinish[i, r] >= 0)
#         for i in Order
#         for r in R[:-1]  # Not concerned with the last row
#     }
#
#     # M = {(p, r, i): compute_M(Passengers, p, r, i) for p in Passengers for r in R for i in Order}
#     M = 10**3
#     VirtualPassing = {
#         (i, r): m.addConstr(
#             TimeArrival[i, r + 1] - TimeFinish[i, r]
#             <= gp.quicksum(M * X[p, i] for p in Passengers if p.row <= r)
#         )
#         for i in Order
#         for r in R[:-1]
#     }
#
#     NaturalAisleOrder = {
#         (i, r): m.addConstr(TimeArrival[i + 1, r] >= TimeFinish[i, r])
#         for i in Order[:-1]
#         for r in R
#     }
#
#     Tau = {(p, r): time_taken_at_row(p, r) for p in Passengers for r in R}
#     MovementCost = {
#         (i, r): m.addConstr(
#             TimeFinish[i, r] - TimeArrival[i, r]
#             >= gp.quicksum(Tau[p, r] * X[p, i] for p in Passengers)
#         )
#         for i in Order
#         for r in R
#     }
#     return m, X


class AirplaneBoardingProblem:
    def __init__(self, filename: str):
        self.num_rows = None
        self.num_cols = None
        self.num_passengers = None

        self.passengers = []

        self.parse_file(filename)

    def parse_file(self, filename: str):
        f = open(filename, "r")
        data = f.readlines()

        self.num_rows = int(data[0].split(" ")[1])
        self.num_cols = int(data[1].split(" ")[1])
        self.num_passengers = int(data[2].split(" ")[1])

        data = data[3:]

        self.passengers = [
            Passenger(
                id=i // 4,
                row=int(data[i].split(" ")[1]),
                column=int(data[i + 1].split(" ")[1]),
                settle_time=float(data[i + 2].split(" ")[1]),
                move_times=(
                    given_times := tuple(
                        float(time) for time in data[i + 3].split(" ")[1:]
                    )
                )
                + tuple(0 for _ in range(self.num_rows - len(given_times))),
            )
            for i in range(0, len(data), 4)
        ]

        f.close()


class AbpSolution:
    def __init__(self, problem: AirplaneBoardingProblem, ordering: list[Passenger]):
        self.problem = problem
        self.ordering = ordering

        self.computation_time = None
        self.makespan = self._calc_makespan()

    def _calc_makespan(self):
        m = gp.Model("Paper Airplane Boarding")

        # Sets & Data
        # Passengers, Plane = parse_file(filename)
        Passengers = self.problem.passengers
        Order = range(1, len(Passengers) + 1)
        R = range(1, self.problem.num_rows + 1)

        # Variables
        # X[p, i] <=> pi(p) = i
        X = {(p, i): m.addVar(vtype=gp.GRB.BINARY) for p in Passengers for i in Order}

        # passenger pi^-1(i) arrives at row r
        TimeArrival = {
            (i, r): m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0) for i in Order for r in R
        }
        # passenger pi^-1(i) finishes actions at row r
        TimeFinish = {
            (i, r): m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0) for i in Order for r in R
        }

        # Makepsan variable. This is bounded below by the last finish time TimeFinish[i, R]
        CompletionTime = m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0)

        # Objective - Minimise makespan
        m.setObjective(CompletionTime, gp.GRB.MINIMIZE)

        OrderMustBeFilled = {
            i: m.addConstr(gp.quicksum(X[p, i] for p in Passengers) == 1) for i in Order
        }

        # Constraints
        OnePassengerOnePositionInOrder = {
            p: m.addConstr(gp.quicksum(X[p, i] for i in Order) == 1) for p in Passengers
        }

        CompletionTimeSmallestFinish = {
            i: m.addConstr(CompletionTime >= TimeFinish[i, self.problem.num_rows])
            for i in Order
        }

        ArriveNextRowBeforeCurrent = {
            (i, r): m.addConstr(TimeArrival[i, r + 1] - TimeFinish[i, r] >= 0)
            for i in Order
            for r in R[:-1]  # Not concerned with the last row
        }

        # M = {(p, r, i): compute_M(Passengers, p, r, i) for p in Passengers for r in R for i in Order}
        M = 10**3
        VirtualPassing = {
            (i, r): m.addConstr(
                TimeArrival[i, r + 1] - TimeFinish[i, r]
                <= gp.quicksum(M * X[p, i] for p in Passengers if p.row <= r)
            )
            for i in Order
            for r in R[:-1]
        }

        NaturalAisleOrder = {
            (i, r): m.addConstr(TimeArrival[i + 1, r] >= TimeFinish[i, r])
            for i in Order[:-1]
            for r in R
        }

        Tau = {(p, r): time_taken_at_row(p, r) for p in Passengers for r in R}
        MovementCost = {
            (i, r): m.addConstr(
                TimeFinish[i, r] - TimeArrival[i, r]
                >= gp.quicksum(Tau[p, r] * X[p, i] for p in Passengers)
            )
            for i in Order
            for r in R
        }


        for (p, i) in X:
            X[p, i].lb = (self.ordering[i - 1] == p)

        m.optimize()

        return m.objVal


class Solver(ABC):
    def solve(self, abp: AirplaneBoardingProblem):
        start = time.time()
        solution = self.solve_implementation(abp)
        solution.computation_time = time.time() - start
        solution.type = type(self).__name__
        return solution

    def solve_implementation(
        self, abp: AirplaneBoardingProblem
    ) -> AbpSolution:
        raise NotImplementedError


class RandomSolver(Solver):
    def solve_implementation(
        self, abp: AirplaneBoardingProblem
    ) -> AbpSolution:
        result = random.sample(abp.passengers, len(abp.passengers))
        return AbpSolution(problem=abp, ordering=result)


if __name__ == "__main__":
    abp = AirplaneBoardingProblem("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")
    rand_solver = RandomSolver()
    solution = rand_solver.solve(abp)
    print(solution.makespan)


