from new import *

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
