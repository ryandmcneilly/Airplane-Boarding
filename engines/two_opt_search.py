from util import Passenger, AbpSolution, AirplaneBoardingProblem


def two_opt_search(abp: AirplaneBoardingProblem, makespan: int, solution: list[Passenger]):
    found_improvement = True

    while found_improvement:
        found_improvement = False
        for i in range(len(solution)):
            for j in range(i+1, len(solution)):
                new_solution = solution.copy()

                # Swap positions
                new_solution[i], new_solution[j] = new_solution[j], new_solution[i]

                new_makespan = AbpSolution(abp, solution).simulate_boarding()
                if new_makespan < makespan:
                    print(f"Found a better solution in 2-opt: {makespan} -> {new_makespan}")
                    makespan = new_makespan
                    solution = new_solution
                    found_improvement =  True

    return makespan, solution


