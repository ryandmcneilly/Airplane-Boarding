import gurobipy as gp
from parse import parse_file
from util import Passenger, Plane, visualise_res


# passengers_computed = set()
# def compute_M(P: list[Passenger], p: Passenger, r: int, i: int):
#     global passengers_computed
#     print(f"Computing {len(passengers_computed) + 1}/{len(P)}")
#     relevant_passengers = [pp for pp in P if pp != p and pp.row > r]
#
#     max_delay = 0
#     for subset_size in range(1, min(i, len(relevant_passengers)) + 1):
#         for PP in combinations(relevant_passengers, subset_size):
#             # delay is movements through rows and settle in time
#             delay = sum(pp.move_times[rr] for pp in PP for rr in range(r, pp.row) if 0 <= rr < len(pp.move_times)) + \
#                 sum(pp.settle_time for pp in PP)
#
#             max_delay = max(delay, max_delay)
#
#     passengers_computed.add(p)
#     return max_delay

def time_taken_at_row(p: Passenger, r: int):
    if r <= p.row - 1:
        return p.move_times[r]
    elif r == p.row:
        return p.settle_time
    elif r >= p.row + 1:
        return 0
    assert "Unreachable"

def build_model(filename: str):
    m = gp.Model("Paper Airplane Boarding")

    # Sets & Data
    Passengers, Plane = parse_file(filename)
    Order = range(1, len(Passengers) + 1)
    R = range(1, Plane.num_rows + 1)

    # Variables
    # X[p, i] <=> pi(p) = i
    X = {(p, i): m.addVar(vtype=gp.GRB.BINARY)
        for p in Passengers for i in Order
    }

    # passenger pi^-1(i) arrives at row r
    TimeArrival = {(i, r): m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0)
        for i in Order for r in R
    }
    # passenger pi^-1(i) finishes actions at row r
    TimeFinish = {(i, r): m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0)
        for i in Order for r in R
    }

    # Makepsan variable. This is bounded below by the last finish time TimeFinish[i, R]
    CompletionTime = m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0)

    # Objective - Minimise makespan
    m.setObjective(CompletionTime, gp.GRB.MINIMIZE)

    OrderMustBeFilled = {i:
        m.addConstr(gp.quicksum(X[p, i] for p in Passengers) == 1)
        for i in Order
    }

    # Constraints
    OnePassengerOnePositionInOrder = {p:
        m.addConstr(gp.quicksum(X[p, i] for i in Order) == 1)
        for p in Passengers
    }

    CompletionTimeSmallestFinish = {i:
        m.addConstr(CompletionTime >= TimeFinish[i, Plane.num_rows])
        for i in Order
    }

    ArriveNextRowBeforeCurrent = {(i, r):
        m.addConstr(TimeArrival[i, r+1] - TimeFinish[i, r] >= 0)
        for i in Order for r in R[:-1] # Not concerned with the last row
    }

    # M = {(p, r, i): compute_M(Passengers, p, r, i) for p in Passengers for r in R for i in Order}
    M = 10 ** 3
    VirtualPassing = {(i, r):
        m.addConstr(TimeArrival[i, r+1] - TimeFinish[i, r] <= gp.quicksum(M * X[p, i] for p in Passengers if p.row <= r))
        for i in Order for r in R[:-1]
    }

    NaturalAisleOrder = {(i, r) :
        m.addConstr(TimeArrival[i+1, r] >= TimeFinish[i, r])
        for i in Order[:-1] for r in R
    }

    Tau = {(p, r): time_taken_at_row(p, r) for p in Passengers for r in R}
    MovementCost = {(i, r):
        m.addConstr(TimeFinish[i, r] - TimeArrival[i, r] >= gp.quicksum(Tau[p, r] * X[p, i] for p in Passengers))
        for i in Order for r in R
    }
    return m, X


def solve(m: gp.Model, X: dict[tuple[int, int], gp.Var]):
    m.optimize()

    result = [None for _ in range(len(set(p for p, i in X)))]
    for (p, i) in X:
            if round(X[p, i].x) == 1:
                result[i - 1] = p
    return result, m.objVal

def main():
    m, X = build_model("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")
    res, obj_val = solve(m, X)


    visualise_res(res, obj_val)
    print(res)

if __name__ == "__main__":
    main()