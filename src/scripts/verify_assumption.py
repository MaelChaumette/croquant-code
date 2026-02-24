import numpy as np

from tqdm import tqdm

from fractions import Fraction

from math import ceil

from src.borders import build_tiling_domain
from src.complex_case import get_centroids_accum, generate_directions, normalize_direction_set, chop_complex
from src.generate_data import generate_alphabet, random_finite_alphabet, random_unit_roots


def v2(n):
    n = abs(n)

    return (n & -n).bit_length() - 1


def check_form_cond1(im1, im2, t):
    frac = Fraction.from_float(abs(im1)) / Fraction.from_float(abs(im2))

    p = frac.numerator
    q = frac.denominator

    v2_num = v2(p)
    v2_den = v2(q)

    m_num = p >> v2_num
    m_den = q >> v2_den

    low = (1 << t) + 1
    high = (1 << (t + 1)) - 1

    admis_low = max(ceil(low // m_num), ceil(low // m_den))
    admis_high = min((high // m_num), (high // m_den))

    if admis_low > admis_high:
        return False

    m = admis_low if admis_low % 2 == 1 else admis_low + 1
    if m > admis_high:
        return False

    return True


def check_form_cond2(re, t):
    frac = Fraction.from_float(abs(re))

    p = frac.numerator
    q = frac.denominator

    v2_num = v2(p)
    v2_den = v2(q)

    m_num = p >> v2_num
    m_den = q >> v2_den

    if m_den != 1:
        return False

    low = (1 << t) + 1
    high = (1 << (t + 1)) - 1

    if not (low <= m_num <= high):
        return False

    return True


def check_assumption_x(normalized_direction_set, t):
    for z in normalized_direction_set:
        for z_1 in normalized_direction_set:
            if z_1 == z:
                continue

            if np.imag(z.conj() * z_1) == 0:
                continue
            for z_2 in normalized_direction_set:
                if z_2 == z or z_2 == z_1:
                    continue

                if np.imag(z.conj() * z_2) == 0:
                    continue

                if check_form_cond1(np.imag(z.conj() * z_1), np.imag(z.conj() * z_2), t):
                    return True

    return False


def check_assumption_y(normalized_direction_set_x, x, y, t):
    tiling_domain = build_tiling_domain(normalized_direction_set_x, t)
    centroids_accum = get_centroids_accum(
        normalized_direction_set_x, t, tiling_domain)
    for c in centroids_accum:
        x_hat = chop_complex(c * x, t)
        mu = np.vdot(x, x_hat) / (np.linalg.norm(x_hat, ord=2)**2)

        normalized_direction_set_y = normalize_direction_set(
            generate_directions(y))
        for z in normalized_direction_set_y:
            if np.real(mu * z) == 0:
                return True

            if check_form_cond2(np.real(mu * z), t):
                return True

    return False


def check_assumption(x, y, t):
    direction_set = generate_directions(x)
    normalized_direction_set = normalize_direction_set(direction_set)

    return check_assumption_x(normalized_direction_set, t) or check_assumption_y(normalized_direction_set, x, y, t)


def count_failures(max_trials, m, n, t, distrib):
    count = 0
    rng = np.random.default_rng()
    pbar = tqdm(range(max_trials), desc=f"m={m}, n={n}, distrib={distrib}")
    for i in pbar:
        if distrib == "uniform":
            x = np.random.rand(m) + 1j * np.random.rand(m)
            y = np.random.rand(n) + 1j * np.random.rand(n)
        elif distrib == "normal":
            x = np.random.normal(0, 1, m) + 1j * np.random.normal(0, 1, m)
            y = np.random.normal(0, 1, n) + 1j * np.random.normal(0, 1, n)
        elif distrib == "finite_alphabet":
            alphabet = generate_alphabet(32)
            x = random_finite_alphabet(m, alphabet)
            y = random_finite_alphabet(n, alphabet)
        elif distrib == "roots_of_unity":
            x = random_unit_roots(m, 32)
            y = random_unit_roots(n, 32)
        else:
            raise ValueError(f"Unknown distribution: {distrib}")

        if x.shape > y.shape:
            x, y = y, x

        if check_assumption(x, y, t):
            count += 1

        pbar.set_postfix({"prop": f"{count / (i + 1):.4f}"})

    return count / max_trials


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    m = arguments.m
    n = arguments.n
    t = arguments.bit
    num_trials = arguments.max_points
    distrib = arguments.distrib

    prop = count_failures(num_trials, m, n, t, distrib)
    print(
        f"Estimated probability of failure for m={m}, n={n}, distrib={distrib}: {100 * prop:.2f}%")
