import numpy as np

from pathlib import Path

from tqdm import tqdm

from src.fft import get_fft_butterflies, cost_fft
from src.algos_quantize_butterfly import (
    butterfly_quantize_ltr,
    butterfly_quantize_pairwise,
    butterfly_quantize_rtn,
    butterfly_quantize_stochastic,
    butterfly_quantize_fixed
)


def one_experiment(args):
    size = args.n
    bit = args.bit
    delta = args.delta
    max_points = args.max_points

    cost_fft_ltr = np.zeros(max_points)
    cost_fft_pairwise = np.zeros(max_points)
    cost_fft_rtn = np.zeros(max_points)
    cost_fft_stochastic = np.zeros(max_points)
    cost_fft_fixed = np.zeros(max_points)

    butterflies = get_fft_butterflies(size)

    butterflies_ltr = butterfly_quantize_ltr(butterflies, bit, delta)
    butterflies_pairwise = butterfly_quantize_pairwise(butterflies, bit, delta)
    butterflies_rtn = butterfly_quantize_rtn(butterflies, bit)
    butterflies_stochastic = butterfly_quantize_stochastic(butterflies, bit)
    butterflies_fixed = butterfly_quantize_fixed(butterflies, bit)

    for j in tqdm(range(max_points), desc=f"n={size}, t={bit}, delta={delta}"):
        cost_fft_ltr[j] = cost_fft(butterflies, butterflies_ltr)
        cost_fft_pairwise[j] = cost_fft(butterflies, butterflies_pairwise)
        cost_fft_rtn[j] = cost_fft(butterflies, butterflies_rtn)
        cost_fft_stochastic[j] = cost_fft(butterflies, butterflies_stochastic)
        cost_fft_fixed[j] = cost_fft(butterflies, butterflies_fixed)

    return cost_fft_ltr, cost_fft_pairwise, cost_fft_rtn, cost_fft_stochastic, cost_fft_fixed


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    save_dir = Path(arguments.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    (
        cost_fft_ltr,
        cost_fft_pairwise,
        cost_fft_rtn,
        cost_fft_stochastic,
        cost_fft_fixed
    ) = one_experiment(arguments)

    with open(f"{save_dir}/compare_error_fft.npy", "wb") as f:
        np.save(f, np.stack((
            cost_fft_ltr, cost_fft_pairwise, cost_fft_rtn, cost_fft_stochastic, cost_fft_fixed
        )))
