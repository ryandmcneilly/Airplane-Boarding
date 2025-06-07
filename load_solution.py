import json

import util
import os

from engines.cp import CP
from util import AbpSolver


class LoadSolver(util.AbpSolver):
    @staticmethod
    def load_solution(filepath: util.AbpFilepath, solver: AbpSolver):
        solver_name = solver.__name__.lower()
        num_rows, num_columns, test_num = filepath
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(
            script_dir,
            f"results/{num_rows}_{num_columns}/{solver_name}__mp_sp__{num_rows}_{num_columns}__{test_num}.json",
        )
        f = open(filename, "r")
        json_data = json.load(f)
        f.close()
        return json_data


    def solve_implementation(self, abp: util.AirplaneBoardingProblem, solver=CP) -> util.AbpSolution:
        json_data = self.load_solution(abp.filepath, solver)
        ordering = [next(p for p in abp.passengers if p.id == id) for id in json_data["order"]]
        makespan = json_data["objective_value"] * 10
        return util.AbpSolution(abp, ordering, makespan=makespan)



if __name__ == "__main__":
    solver = LoadSolver()
    abp = util.AirplaneBoardingProblem(util.CURRENT_ABP_PROBLEM)
    sol: util.AbpSolution = solver.solve_implementation(abp)
    sol.make_solution_plot()
