import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

from src.gather_results import gather_results
from src.plot_utils import configure_plt


configure_plt(fontsize=16)

plt.rcParams.update({
    "text.latex.preamble": r"""
\usepackage[T1]{fontenc}
\usepackage[tt=false, type1=true]{libertine}
\usepackage[libertine]{newtxmath}
""",
})


def plot_error_fft_t(args):
    size = args.n
    delta = args.delta
    save_dir = args.save_dir
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    all_errors, _, param_values = gather_results(
        save_dir, "compare_error_fft.npy")

    t_values = param_values["bit"]

    all_errors = np.stack(all_errors)

    cost_ltr = all_errors[:, 0, :]
    cost_pairwise = all_errors[:, 1, :]
    cost_rtn = all_errors[:, 2, :]
    cost_stochastic = all_errors[:, 3, :]
    cost_fixed = all_errors[:, 4, :]

    # colors = sns.color_palette("Set2", n_colors=3)
    colors = ["#FC9200", "#A5CF00", "#0055C9"]

    plt.figure(figsize=(10, 7))

    # # Fixed
    # mean_fixed = np.mean(cost_fixed, axis=1)
    # err_fixed = 1.96 * np.std(cost_fixed, axis=1) / \
    #     np.sqrt(cost_fixed.shape[1])
    # coefs_fixed = np.polyfit(t_values, np.log2(mean_fixed), 1)
    # alpha, beta = round(coefs_fixed[0], 1), round(2**coefs_fixed[1], 1)

    # label_fixed = fr"Fixed-point (fit: ${beta} \times 2^{{{alpha} t}}$)"
    # plt.plot(t_values, mean_fixed, marker="s", markersize=8, label=label_fixed)

    # Stochastic
    mean_stochastic = np.mean(cost_stochastic, axis=1)
    err_stochastic = 1.96 * np.std(cost_stochastic, axis=1) / \
        np.sqrt(cost_stochastic.shape[1])
    coefs_stochastic = np.polyfit(t_values, np.log2(mean_stochastic), 1)
    alpha, beta = round(coefs_stochastic[0], 1), round(
        2**coefs_stochastic[1], 1)

    label_stochastic = fr"Stochastic (fit: ${beta} \times 2^{{{alpha} t}}$)"
    plt.plot(t_values, mean_stochastic, marker="s", markersize=8,
             label=label_stochastic, color=colors[0], linestyle="--")

    # RTN
    mean_rtn = np.mean(cost_rtn, axis=1)
    err_rtn = 1.96 * np.std(cost_rtn, axis=1) / np.sqrt(cost_rtn.shape[1])
    coefs_rtn = np.polyfit(t_values, np.log2(mean_rtn), 1)
    alpha, beta = round(coefs_rtn[0], 1), round(2**coefs_rtn[1], 1)

    label_rtn = fr"RTN (fit: ${beta} \times 2^{{{alpha} t}}$)"
    plt.plot(t_values, mean_rtn, marker="o", markersize=8,
             label=label_rtn, color=colors[1], linestyle=":")

    # Pairwise
    # mean_pairwise = np.mean(cost_pairwise, axis=1)
    # err_pairwise = np.std(cost_pairwise, axis=1) / \
    #     np.sqrt(cost_pairwise.shape[1])
    # coefs_pairwise = np.polyfit(t_values, np.log2(mean_pairwise), 1)
    # alpha, beta = round(coefs_pairwise[0], 1), round(2**coefs_pairwise[1], 1)

    # label_pairwise = fr"Pairwise (fit: ${beta} \times 2^{{{alpha} t}}$)"
    # plt.plot(t_values, mean_pairwise, marker="*", markersize=8, label=label_pairwise)

    # Left-to-Right
    mean_ltr = np.mean(cost_ltr, axis=1)
    err_ltr = 1.96 * np.std(cost_ltr, axis=1) / np.sqrt(cost_ltr.shape[1])
    coefs_ltr = np.polyfit(t_values, np.log2(mean_ltr), 1)
    alpha, beta = round(coefs_ltr[0], 1), round(2**coefs_ltr[1], 1)

    label_ltr = fr"LTR (fit: ${beta} \times 2^{{{alpha} t}}$)"
    plt.plot(t_values, mean_ltr, marker="*", markersize=11,
             label=label_ltr, color=colors[2])

    plt.ylabel(r"$\rho_{\small \textnormal{fft}}$")
    plt.xlabel(r"$t$")

    plt.yscale("log")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/errorFFT_t_n={size}_t={t_values}_delta={delta}.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close()


def plot_error_fft_n(args):
    bit = args.bit
    delta = args.delta
    save_dir = args.save_dir
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    all_errors, _, param_values = gather_results(
        save_dir, "compare_error_fft.npy")

    n_values = param_values["size"]

    all_errors = np.stack(all_errors)

    cost_ltr = all_errors[:, 0, :]
    cost_pairwise = all_errors[:, 1, :]
    cost_rtn = all_errors[:, 2, :]
    cost_stochastic = all_errors[:, 3, :]
    cost_fixed = all_errors[:, 4, :]

    colors = sns.color_palette("Set2", n_colors=3)
    colors = ["#FC9200", "#A5CF00", "#0055C9"]

    plt.figure(figsize=(10, 7))

    # # Fixed
    # mean_fixed = np.mean(cost_fixed, axis=1)
    # err_fixed = 1.96 * np.std(cost_fixed, axis=1) / \
    #     np.sqrt(cost_fixed.shape[1])
    # plt.errorbar(n_values, mean_fixed, yerr=err_fixed,
    #              label="Fixed-point", marker="s", markersize=8)

    # Stochastic
    mean_stochastic = np.mean(cost_stochastic, axis=1)
    err_stochastic = 1.96 * np.std(cost_stochastic, axis=1) / \
        np.sqrt(cost_stochastic.shape[1])
    plt.errorbar(n_values, mean_stochastic, yerr=err_stochastic,
                 label="Stochastic", marker="s", markersize=8, color=colors[0], linestyle="--")

    # RTN
    mean_rtn = np.mean(cost_rtn, axis=1)
    err_rtn = 1.96 * np.std(cost_rtn, axis=1) / np.sqrt(cost_rtn.shape[1])
    plt.errorbar(n_values, mean_rtn, yerr=err_rtn, label="RTN",
                 marker="o", markersize=8, color=colors[1], linestyle=":")

    # # Pairwise
    # mean_pairwise = np.mean(cost_pairwise, axis=1)
    # err_pairwise = 1.96 * np.std(cost_pairwise, axis=1) / \
    #     np.sqrt(cost_pairwise.shape[1])
    # plt.errorbar(n_values, mean_pairwise, yerr=err_pairwise,
    #              label="Pairwise", marker="*", color="C3", markersize=8)

    # Left-to-Right
    mean_ltr = np.mean(cost_ltr, axis=1)
    err_ltr = 1.96 * np.std(cost_ltr, axis=1) / np.sqrt(cost_ltr.shape[1])
    plt.errorbar(n_values, mean_ltr, yerr=err_ltr, label="LTR",
                 marker="*", markersize=11, color=colors[2])

    plt.ylabel(r"$\rho_{\small \textnormal{fft}}$")
    plt.xlabel(r"$n$")

    plt.yscale("log")
    plt.xscale("log")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/errorFFT_n_n={n_values}_t={bit}_delta={delta}.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close()


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    if arguments.function in globals():
        globals()[arguments.function](arguments)
