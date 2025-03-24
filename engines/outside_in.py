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
from util import Plane, Passenger



def person_to_order(person: Passenger, plane: Plane):
    k_r = plane.num_cols // 2
    if person.column <= k_r:
        return (2*person.column - 1) * plane.num_rows + 1 - person.row
    elif k_r < person.column <= k_r: # currently impossible as k_r^1 = k_r^2
        return (k_r + person.column) * plane.num_rows + 1 - person.row
    elif person.column >= k_r + 1:
        return (k_r - person.column + 1) * plane.num_rows + 1 - person.row
    raise ValueError("Unreachable")

def solve(filename: str):
    Passengers, Plane = parse_file(filename)
    result = [None for _ in range(Plane.num_rows * Plane.num_cols)]
    for p in Passengers:
        order = person_to_order(p, Plane)
        result[order] = p
    return result

def get_obj_val(result):
    m, X = build_model("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")
    for i, p in enumerate(result, start=1):
        X[p, i].lb = 1 # force on
    m.optimize()
    return m.objVal

def main():
    res = solve("../data/mp_sp/10_2/m_p_s_p_10_2_0.abp")
    print(get_obj_val(res))

main()
