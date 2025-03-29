from new import *
import itertools

class OutsideInBTF(Solver):
    def solve_implementation(self, abp: AirplaneBoardingProblem) -> AbpSolution:
        column_groups = [
            [p for p in abp.passengers if p.column == col]
            for col in range(1, abp.num_cols + 1)
        ]

        result = list(itertools.chain.from_iterable([
            sorted(column_groups[col], key=lambda p: p.row, reverse=True)
            for col in range(len(column_groups))
        ]))

        return AbpSolution(abp, result)

if __name__ == "__main__":
    abp = AirplaneBoardingProblem("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")

    outside_in_btf = OutsideInBTF()
    sol = outside_in_btf.solve(abp)
    sol.visualise_solution()
