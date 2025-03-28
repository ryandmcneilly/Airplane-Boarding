from paper_solve import build_model, solve
import engines.max_settle_row
from util import visualise_grid


def main():
    filename = "../data/mp_sp/10_2/m_p_s_p_10_2_0.abp"
    m, X = build_model(filename)

    res = engines.max_settle_row.solve(filename)
    # Hot start
    for (p, i) in X:
        X[p, i].Start = (res[i-1] == p)

    res = solve(m, X)
    print(res)

if __name__ == "__main__":
    visualise_grid([[i*j + j for i in range(10)] for j in range(10)])
    main()