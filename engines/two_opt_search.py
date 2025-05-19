from util import Passenger, AbpSolution, AirplaneBoardingProblem


def two_opt_search(abp: AirplaneBoardingProblem, solution: AbpSolution):
    found_improvement = True
    curr_solution = solution
    makespans = [curr_solution.makespan]
    while found_improvement:
        found_improvement = False
        for i in range(len(curr_solution.ordering)):
            for j in range(i+1, len(curr_solution.ordering)):
                # Swap positions
                new_ordering = curr_solution.ordering.copy()
                new_ordering[i], new_ordering[j] = new_ordering[j], new_ordering[i]

                new_solution = AbpSolution(abp, new_ordering)
                if new_solution.makespan < curr_solution.makespan:
                    makespans.append(new_solution.makespan)
                    curr_solution = new_solution
                    found_improvement =  True

    if len(makespans) > 1:
        print(f"Found a better solution in 2-opt: {' -> '.join(map(str, makespans))}")
    return curr_solution


