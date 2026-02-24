import numpy as np
import pandas as pd

from pathlib import Path

from src.complex_case import c, get_centroids_accum, get_centroids, generate_directions, normalize_direction_set, chop_complex, generate_midpoints, find_e_max, find_e_min
from src.borders import build_tiling_domain
from src.algos_quantize_rank_one import find_xy_rtn_complex
from src.generate_data import random_unit_roots, generate_alphabet, random_finite_alphabet


def from_centroid_to_xy(centroid, x, y, t):
    x_hat = chop_complex(centroid * x, t)

    mu = np.vdot(x, x_hat) / np.linalg.norm(x_hat)**2
    y_hat = chop_complex(mu * y, t)

    return x_hat, y_hat


def one_experiment(args):
    n = args.n
    m = args.m
    bit = args.bit
    delta = args.delta
    distrib = args.distrib

    error_delta = {f"{i}": [] for i in range(0, delta + 1)}

    if distrib == "uniform":
        x = np.random.rand(m) + 1j * np.random.rand(m)
        y = np.random.rand(n) + 1j * np.random.rand(n)
    elif distrib == "normal":
        x = np.random.normal(0, 1, m) + 1j * np.random.normal(0, 1, m)
        y = np.random.normal(0, 1, n) + 1j * np.random.normal(0, 1, n)
    elif distrib == "roots_of_unity":
        x = random_unit_roots(m)
        y = random_unit_roots(n)
    elif distrib == "finite_alphabet":
        alphabet = generate_alphabet(32)
        x = random_finite_alphabet(m, alphabet)
        y = random_finite_alphabet(n, alphabet)
    else:
        raise Exception("Wrong distribution")

    print(
        f"Compute quantization error for m={m}, n={n}, t={bit}, distrib={distrib}")

    x_rtn, y_rtn = find_xy_rtn_complex(x, y, bit)
    error_rtn = c(x, y, x_rtn, y_rtn)

    if x.shape <= y.shape:
        normalized_direction_set = normalize_direction_set(
            generate_directions(x))
    else:
        normalized_direction_set = normalize_direction_set(
            generate_directions(y))

    tiling_domain = build_tiling_domain(normalized_direction_set, bit)

    e_min = find_e_min(normalized_direction_set, bit, tiling_domain)
    e_max = find_e_max(normalized_direction_set, bit, tiling_domain)

    centroids_before = get_centroids_accum(
        normalized_direction_set, bit, tiling_domain)

    if x.shape <= y.shape:
        all_xy = [from_centroid_to_xy(centroid, x, y, bit)
                  for centroid in centroids_before]

        error_delta["0"].extend(
            [np.sqrt(c(x, y, x_hat, y_hat) / error_rtn) for (x_hat, y_hat) in all_xy])
    else:
        all_xy = [from_centroid_to_xy(centroid, y, x, bit)
                  for centroid in centroids_before]

        error_delta["0"].extend(
            [np.sqrt(c(x, y, x_hat, y_hat) / error_rtn) for (y_hat, x_hat) in all_xy])

    print("Done for delta = 0")

    for d in range(1, delta + 1):
        midpoint_set = generate_midpoints(bit, e_max, e_min - d)
        current_centroids = get_centroids(
            normalized_direction_set, midpoint_set, tiling_domain)

        if x.shape <= y.shape:
            diff_centroids = list(
                set(current_centroids) - set(centroids_before))
            all_xy = [from_centroid_to_xy(centroid, x, y, bit)
                      for centroid in diff_centroids]

            error_delta[f"{d}"].extend([np.sqrt(c(x, y, x_hat, y_hat) / error_rtn)
                                        for (x_hat, y_hat) in all_xy])
        else:
            diff_centroids = list(
                set(current_centroids) - set(centroids_before))
            all_xy = [from_centroid_to_xy(centroid, y, x, bit)
                      for centroid in diff_centroids]

            error_delta[f"{d}"].extend([np.sqrt(c(x, y, x_hat, y_hat) / error_rtn)
                                        for (y_hat, x_hat) in all_xy])

        centroids_before = current_centroids

        print(f"Done for delta = {d}")

    return error_delta


def dict_to_dataframe(d):
    df = pd.DataFrame([
        {r"$\delta$": key, "Error": val}
        for key, values in d.items()
        for val in values
    ])
    return df


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    save_dir = Path(arguments.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    error_per_delta = one_experiment(arguments)
    df_error_per_delta = dict_to_dataframe(error_per_delta)

    # df_error_per_delta.to_csv(f"{save_dir}/error_per_delta.csv",
    #                           encoding="utf-8", index=False)
