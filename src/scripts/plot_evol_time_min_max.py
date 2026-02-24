import numpy as np
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


def plot_time_min(args):
    delta = args.delta
    save_dir = args.save_dir
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    all_time, _, param_values = gather_results(
        save_dir, "compare_error_time_algo_rtn.npy")

    all_time = np.stack([
        [all_time[i, j] for j in range(all_time.shape[1])]
        for i in range(all_time.shape[0])
    ])

    time_algo = all_time[:, :, 0, :]
    time_rtn = all_time[:, :, 1, :]

    m_values = param_values["m"]
    n_values = param_values["n"]

    plt.figure(figsize=(7, 5))

    for i, m in enumerate(m_values):
        plt.plot(n_values, np.mean(
            time_algo[i, :, :], axis=1), label=fr"$\max(m, n) = {m}$")

    coefs = np.polyfit(np.log(n_values), np.log(
        np.mean(time_algo[0, :, :], axis=1)), 1)
    poly = np.poly1d(coefs)

    plt.plot(n_values, np.exp(poly(np.log(n_values))),
             label=r"$\mathcal{O}(n^{%.1f})$" % coefs[0], color="black", linestyle="dashed")

    plt.yscale("log")
    plt.xscale("log")

    plt.ylabel("Time (s)")
    plt.xlabel(r"$\min(m, n)$")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/evolTimeMin_m={m_values}_n={n_values}_delta={delta}.pdf")
    plt.close()


def plot_time_max(args):
    delta = args.delta
    save_dir = args.save_dir
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    all_time, _, param_values = gather_results(
        save_dir, "compare_error_time_algo_rtn.npy")

    all_time = np.stack([
        [all_time[i, j] for j in range(all_time.shape[1])]
        for i in range(all_time.shape[0])
    ])

    time_algo = all_time[:, :, 0, :]
    time_rtn = all_time[:, :, 1, :]

    m_values = param_values["m"]
    n_values = param_values["n"]

    plt.figure(figsize=(7, 5))

    time_algo = time_algo[::-1, :, :]
    for i, m in enumerate(m_values[::-1]):
        coefs = np.polyfit(n_values, np.mean(time_algo[i, :, :], axis=1), 1)
        poly = np.poly1d(coefs)

        label = fr"$\max(m, n) = {m}$ (fit: ${coefs[0]:.5f} n + {coefs[1]:.2f}$)"

        plt.plot(n_values, np.mean(
            time_algo[i, :, :], axis=1), label=label)

        plt.plot(n_values, poly(n_values), color="black", linestyle="dashed")

    plt.ylabel("Time (s)")
    plt.xlabel(r"$\max(m, n)$")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/evolTimeMax_m={m_values}_n={n_values}_delta={delta}.pdf")
    plt.close()


def plot_time_delta(args):
    bit = args.bit
    save_dir = args.save_dir
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    all_time, _, param_values = gather_results(
        save_dir, "compare_error_time_algo_rtn.npy")

    all_time = np.stack([
        [all_time[i, j] for j in range(all_time.shape[1])]
        for i in range(all_time.shape[0])
    ])

    time_algo = all_time[:, :, 0, :]
    time_rtn = all_time[:, :, 1, :]

    delta_values = param_values["delta"]
    n_values = param_values["n"]

    plt.figure(figsize=(7, 5))

    for i, n in enumerate(n_values):
        plt.plot(delta_values, np.mean(
            time_algo[:, i, :], axis=1), label=fr"$n = {n}$")

    coefs = np.polyfit(np.log(delta_values), np.log(
        np.mean(time_algo[:, 0, :], axis=1)), 1)
    poly = np.poly1d(coefs)

    plt.plot(delta_values, 2 * np.exp(poly(np.log(delta_values))),
             label=r"$\mathcal{O}(\delta^{%.2f})$" % coefs[0], color="black", linestyle="dashed")

    plt.yscale("log")
    plt.xscale("log")

    plt.ylabel("Time (s)")
    plt.xlabel(r"$\delta$")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/evolTimeDelta_n={n_values}_bit={bit}.pdf")
    plt.close()


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    if arguments.function in globals():
        globals()[arguments.function](arguments)
