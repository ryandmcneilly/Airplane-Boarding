from new import *

class MIPSolver(Solver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        m, X = build_model(abp)
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
    mip_solution.print_solution()