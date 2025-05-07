from engines.heuristic_search import get_best_heuristic
from util import *

class MIPSolver(Solver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        m = gp.Model("Paper Airplane Boarding")

        heuristic_makespan, heuristic_solution = get_best_heuristic(abp)

        # Variables --------------------------------------
        X = {
            (p, i): m.addVar(vtype=gp.GRB.BINARY, name=f"X_{p},{i}")
            for p in abp.passengers
            for i in abp.order
        }

        # Hot start solution with best heuristic
        for p, i in X:
            X[p, i].Start = heuristic_solution[i - 1] == p


        TimeArrival = {
            (i, r): m.addVar(vtype=gp.GRB.CONTINUOUS)
            for i in abp.order
            for r in abp.rows
        }

        TimeFinish = {
            (i, r): m.addVar(vtype=gp.GRB.CONTINUOUS)
            for i in abp.order
            for r in abp.rows
        }

        CompletionTime = m.addVar(vtype=gp.GRB.CONTINUOUS)

        # Objective --------------------------------------
        m.setObjective(CompletionTime, gp.GRB.MINIMIZE)

        # Subject to --------------------------------------
        OrderMustBeFilled = {
            i: m.addConstr(gp.quicksum(X[p, i] for p in abp.passengers) == 1)
            for i in abp.order
        }

        # Constraints
        OnePassengerOnePositionInOrder = {
            p: m.addConstr(gp.quicksum(X[p, i] for i in abp.order) == 1)
            for p in abp.passengers
        }

        CompletionTimeSmallestFinish = {
            i: m.addConstr(CompletionTime >= TimeFinish[i, abp.num_rows]) for i in abp.order
        }

        ArriveNextRowBeforeCurrent = {
            (i, r): m.addConstr(TimeArrival[i, r + 1] - TimeFinish[i, r] >= 0)
            for i in abp.order
            for r in abp.rows[:-1]  # Not concerned with the last row
        }

        VirtualPassing = {
            (i, r): m.addConstr(
                TimeArrival[i, r + 1] - TimeFinish[i, r]
                <= gp.quicksum(heuristic_makespan * X[p, i] for p in abp.passengers if p.row <= r)
            )
            for i in abp.order
            for r in abp.rows[:-1]
        }

        NaturalAisleOrder = {
            (i, r): m.addConstr(TimeArrival[i + 1, r] >= TimeFinish[i, r])
            for i in abp.order[:-1]
            for r in abp.rows
        }

        Tau = {(p, r): time_taken_at_row(p, r) for p in abp.passengers for r in abp.rows}
        MovementCost = {
            (i, r): m.addConstr(
                TimeFinish[i, r] - TimeArrival[i, r]
                >= gp.quicksum(Tau[p, r] * X[p, i] for p in abp.passengers)
            )
            for i in abp.order
            for r in abp.rows
        }

        m.setParam("OutputFlag", 0)
        m.optimize()

        result = [None for _ in range(len(set(p for p, i in X)))]
        for (p, i) in X:
            if round(X[p, i].x) == 1:
                result[i - 1] = p

        return AbpSolution(abp, result, makespan=m.objVal)


if __name__ == "__main__":
    abp = AirplaneBoardingProblem("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")

    mip_solver = MIPSolver()
    mip_solution = mip_solver.solve(abp)
    print(f"Solved in {mip_solution.computation_time:.2f}s")

    mip_solution.print_solution()