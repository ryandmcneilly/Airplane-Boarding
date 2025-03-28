from paper_solve import build_model, solve
import engines.max_settle_row
from util import visualise_res, print_res


def main():
    filename = "../data/mp_sp/10_2/m_p_s_p_10_2_0.abp"
    m, X = build_model(filename)

    res = engines.max_settle_row.solve(filename)
    # Hot start
    for (p, i) in X:
        X[p, i].Start = (res[i-1] == p)

    res, obj_val = solve(m, X)
    print_res(res)
    visualise_res(res, obj_val)


if __name__ == "__main__":
    main()