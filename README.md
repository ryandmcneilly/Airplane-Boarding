# Airplane Boarding
This repository builds a Constraint programming approach to the Airplane Boarding Problem as described in [Minimizing Airplane Boarding Time](https://pubsonline.informs.org/doi/10.1287/trsc.2021.1098). 
### Problem Description
The problem is to find the boarding order of passengers which has minimum boarding time (makespan). What makes this problem interesting is each passenger has varying settle-in times into their seat $t^s_p$  for passenger $p \in \mathcal{P}$ , as well as varying move times $t^{m}_{p, r}$ for passenger $p \in \mathcal{P}$ in row $r \in \mathcal{R}$ . Passengers have pre-allocated seats in the plane, namely $\text{row}_p$ and $\text{col}_p$. 
### Entry Points
Models can be found in `engines/` with their own respective entry points. This entry point can be ran with
```shell
python3 engines/[...].py
```
which runs the instance `util.CURRENT_ABP_PROBLEM`.

The engines are as follows:
- `engines/cp.py` - Constraint Programming model using OR-Tools CP-SAT solver. This makes use `Interval` variables and `NoOverlap` constraints, and forms the main purpose of this repository. Times out after 10 minutes (600 seconds).
- `engines/mip.py` - Mixed Integer Programming model using Gurobi 12.0.1 as described in the original [paper](https://pubsonline.informs.org/doi/10.1287/trsc.2021.1098). Times out after 10 minutes (600 seconds).
- `engines/outside_in_btf.py` - Heuristic solution where passengers board in groups of $|\mathcal{R}|$ where groups are defined by $\text{col}_p$, then within groups in descending order by $\text{row}_p$. 
- `engines/max_settle_row.py` - Heuristic solution as described in the paper.
- `engines/random_ordering.py` - Heuristic solution gets a random ordering of passengers, used to compare against other strategies.
### Results
Results can be found in `/results`. CP model outperformed the MIP model 37 out of 40 times, comparing optimality gap and breaking ties (optimality) by computation time.
### Requirements
- Python 3.10 $\geq$ 
- Valid license of Gurobi
- Ensure all python packages found in `requirements.txt` are installed.
	- This can be done with `pip install -r requirements.txt`, preferably done with a virtual environment.

