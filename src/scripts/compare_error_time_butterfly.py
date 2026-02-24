import time
import numpy as np

from scipy.sparse.linalg import norm

from lazylinop.butterfly import ksd, Chain

from tqdm import tqdm

from pathlib import Path

from src.algos_quantize_butterfly import (
    butterfly_quantize_ltr,
    butterfly_quantize_pairwise,
    butterfly_quantize_rtn,
    butterfly_quantize_stochastic,
    butterfly_quantize_fixed
)
from src.fft import apply_soft_thresholding


def evaluate(butterflies, butterflies_hat):
    result = butterflies[0]
    result_hat = butterflies_hat[0]
    for butterfly, butterfly_hat in zip(butterflies[1:], butterflies_hat[1:]):
        result = result @ butterfly
        result_hat = result_hat @ butterfly_hat

    return norm(result - result_hat) / norm(result_hat)


def one_experiment(args):
    size = args.n
    bit = args.bit
    delta = args.delta
    max_points = args.max_points

    error_ltr = np.zeros(max_points)
    error_pairwise = np.zeros(max_points)
    error_rtn = np.zeros(max_points)
    error_stochastic = np.zeros(max_points)
    error_fixed = np.zeros(max_points)

    time_ltr = np.zeros(max_points)
    time_pairwise = np.zeros(max_points)

    sd_chain = Chain.square_dyadic((size, size))

    for j in tqdm(range(max_points), desc=f"n={size}, t={bit}, delta={delta}"):
        A = np.random.randn(size, size) + 1j * np.random.randn(size, size)

        csr_A = apply_soft_thresholding(ksd(A, sd_chain), 1e-6)

        start = time.time()
        csr_A_ltr = butterfly_quantize_ltr(csr_A, bit, delta=delta)
        time_ltr[j] = time.time() - start

        start = time.time()
        csr_A_pairwise = butterfly_quantize_pairwise(csr_A, bit, delta=delta)
        time_pairwise[j] = time.time() - start

        csr_A_rtn = butterfly_quantize_rtn(csr_A, bit)
        csr_A_stochastic = butterfly_quantize_stochastic(csr_A, bit)
        csr_A_fixed = butterfly_quantize_fixed(csr_A, bit)

        error_ltr[j] = evaluate(csr_A_ltr, csr_A)
        error_pairwise[j] = evaluate(csr_A_pairwise, csr_A)
        error_rtn[j] = evaluate(csr_A_rtn, csr_A)
        error_stochastic[j] = evaluate(csr_A_stochastic, csr_A)
        error_fixed[j] = evaluate(csr_A_fixed, csr_A)

    return error_ltr, error_pairwise, error_rtn, error_stochastic, error_fixed, time_ltr, time_pairwise


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    save_dir = Path(arguments.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    (
        error_ltr, error_pairwise, error_rtn, error_stochastic, error_fixed, time_ltr, time_pairwise
    ) = one_experiment(arguments)

    with open(f"{save_dir}/compare_error_time_butterfly.npy", "wb") as f:
        np.save(f, np.stack((
            error_ltr, error_pairwise, error_rtn, error_stochastic, error_fixed, time_ltr, time_pairwise
        )))
