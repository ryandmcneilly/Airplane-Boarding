import itertools

from engines.paper_solve import build_model
from parse import parse_file
from util import visualise_res


def solve(filename: str):
    Passengers, Plane = parse_file(filename)

    column_groups = {
        col : [p for p in Passengers if p.column == col]
        for col in range(1, Plane.num_cols + 1)
    }

    num_passengers = sum(len(val) for val in column_groups.values())
    assert num_passengers == Plane.num_passengers

    # Sort each 'column group' by row
    result = list(itertools.chain.from_iterable([
        sorted(passengers, key=lambda p: p.row, reverse=True)
        for col, passengers in column_groups.items()
    ]))

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

    visualise_res(res, obj_val)


if __name__ == "__main__":
    main()