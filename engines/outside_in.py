# Given a ABP problem (P, R, S, sigma, {t_{p, i}^m}, {t_p^s})
# R - Rows
# S - Seats
# P - Passengers s.t |P| <= |S|
# r(p) -> Row of passenger p
# s(p) -> seat number of passenger p
# Row r: (r, 1), (r, 2), ..., (r, k_r^1), | | (r, k_r^1 + 1), (r, k_r^1 + 2), ... (r, k_r^1 + k_r^2)
# S_r = S_r^1 U S_r^2
# S = U_{r\in R} S_r
from engines.paper_solve import build_model
from parse import parse_file
from util import visualise_res, print_res


# from util import get_obj_val


def solve(filename: str):
    Passengers, Plane = parse_file(filename)

    # Do not care about the order as there is no passenger inteference within rows / outside the aisle
    result = sorted(Passengers, key=lambda p: (p.row, sum(p.move_times)), reverse=True)

    return result

def get_obj_val(filename, result):
    m, X = build_model(filename)
    for i, p in enumerate(result, start=1):
        X[p, i].lb = 1 # force on
    m.optimize()
    return m.objVal


def main():
    filename = "../data/mp_sp/10_2/m_p_s_p_10_2_0.abp"
    res = solve(filename)
    obj_val = get_obj_val(filename, res)
    print_res(res)
    visualise_res(res, obj_val)


if __name__ == "__main__":
    main()
