import time
import numpy as np

from tqdm import tqdm

from pathlib import Path

from src.complex_case import c
from src.algos_quantize_rank_one import find_xy_complex, find_xy_rtn_complex
from src.generate_data import random_unit_roots, generate_alphabet, random_finite_alphabet


def one_experiment(args):
    m = args.m
    n = args.n
    bit = args.bit
    delta = args.delta
    max_points = args.max_points

    rho_algo = np.zeros(max_points)
    rho_rtn = np.zeros(max_points)
    time_algo = np.zeros(max_points)
    time_rtn = np.zeros(max_points)

    for j in tqdm(range(max_points), desc=f"m={m}, n={n}, t={bit}, distrib={args.distrib}, delta={delta}"):
        if args.distrib == "uniform":
            x = np.random.rand(m) + 1j * np.random.rand(m)
            y = np.random.rand(n) + 1j * np.random.rand(n)
        elif args.distrib == "normal":
            x = np.random.normal(0, 1, m) + 1j * np.random.normal(0, 1, m)
            y = np.random.normal(0, 1, n) + 1j * np.random.normal(0, 1, n)
        elif args.distrib == "finite_alphabet":
            alphabet = generate_alphabet(32)
            x = random_finite_alphabet(m, alphabet)
            y = random_finite_alphabet(n, alphabet)
        elif args.distrib == "roots_of_unity":
            x = random_unit_roots(m)
            y = random_unit_roots(n)
        else:
            raise Exception("Wrong distribution")

        norm_prod = np.linalg.norm(x) * np.linalg.norm(y)

        start = time.time()
        x_approx, y_approx, _, _ = find_xy_complex(x, y, bit, delta=delta)
        time_algo[j] = time.time() - start

        start = time.time()
        x_rtn, y_rtn = find_xy_rtn_complex(x, y, bit)
        time_rtn[j] = time.time() - start

        rho_algo[j] = np.sqrt(c(x, y, x_approx, y_approx)) / norm_prod
        rho_rtn[j] = np.sqrt(c(x, y, x_rtn, y_rtn)) / norm_prod

    return rho_algo, rho_rtn, time_algo, time_rtn


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    save_dir = Path(arguments.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    rho_algo, rho_rtn, time_algo, time_rtn = one_experiment(arguments)

    with open(f"{save_dir}/compare_error_time_algo_rtn.npy", "wb") as f:
        np.save(f, np.stack((rho_algo, rho_rtn, time_algo, time_rtn)))
