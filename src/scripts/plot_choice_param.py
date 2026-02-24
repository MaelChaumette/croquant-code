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


def plot_choice_param(args):
    save_dir = args.save_dir
    save_img_dir = Path(f"{args.save_img_dir}")

    save_img_dir.mkdir(exist_ok=True, parents=True)

    all_rho, _, param_values = gather_results(
        save_dir, "compare_error_time_algo_rtn.npy")

    all_rho = np.stack([
        [[[all_rho[i, j, k, l] for l in range(all_rho.shape[3])]
          for k in range(all_rho.shape[2])]
         for j in range(all_rho.shape[1])]
        for i in range(all_rho.shape[0])
    ])

    rho_algo = all_rho[:, :, :, :, 0, :]
    rho_rtn = all_rho[:, :, :, :, 1, :]
    time_algo = all_rho[:, :, :, :, 2, :]
    time_rtn = all_rho[:, :, :, :, 3, :]

    for k, distrib in enumerate(param_values["distrib"]):
        plt.figure(figsize=(8, 6))

        rho_algo_distrib = rho_algo[:, k, :, :, :]
        rho_rtn_distrib = rho_rtn[:, k, :, :, :]
        time_algo_distrib = time_algo[:, k, :, :, :]
        time_rtn_distrib = time_rtn[:, k, :, :, :]

        gains_rho = rho_algo_distrib / rho_rtn_distrib
        gains_time = time_algo_distrib / time_rtn_distrib

        gains_time_mean = np.mean(gains_time, axis=3)

        couples = []
        table = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
        hue_order = ["$m=32, n=32$", "$m=32, n=2$",
                     "$m=2, n=32$", "$m=2, n=2$"]
        base_colors = sns.color_palette("Set2", n_colors=len(hue_order))
        colors = ["#FF1924", "#FC9200", "#A5CF00", "#0055C9"]
        colors = dict(zip(hue_order, colors))

        hatches = ["", "///", "\\\\\\", "xxx"]
        hatch_dict = dict(zip(hue_order[::-1], hatches))

        ax = plt.gca()

        all_bp = []
        for i, m in enumerate(param_values["m"]):
            for j, n in enumerate(param_values["n"]):
                mn = f"$m={m}, n={n}$"
                subgains_rho = gains_rho[:, i, j, :]
                subgains_time = gains_time_mean[:, i, j]

                for l in range(subgains_rho.shape[0]):
                    w = 0.1

                    def width(p, w): return 10**(np.log10(p)+w/2.) - \
                        10**(np.log10(p)-w/2.)

                    x_pos = subgains_time[l]
                    color = colors[mn]
                    flierprops = dict(marker='o', markerfacecolor=color,
                                      markeredgecolor=color, alpha=0.6)

                    if l == 0:
                        bp = plt.boxplot(subgains_rho[l, :], positions=[x_pos], widths=width(
                            [x_pos], w), patch_artist=True, boxprops=dict(facecolor=color, alpha=0.6), flierprops=flierprops)
                        all_bp.append(bp["boxes"][0])
                        couples.append(mn)
                    else:
                        bp = plt.boxplot(subgains_rho[l, :], positions=[x_pos], widths=width(
                            [x_pos], w), patch_artist=True, boxprops=dict(facecolor=color, alpha=0.6), flierprops=flierprops)

                    for patch in bp['boxes']:
                        patch.set_hatch(hatch_dict[mn])

                    if mn == "$m=32, n=2$":
                        q3 = bp['boxes'][0].get_path().vertices[2, 1]
                        plt.text(x_pos*1.1, q3, rf"${l}$",
                                 ha='left', va='bottom', fontsize=12,
                                 fontweight='bold', color=color, bbox=dict(boxstyle='round,pad=0.1',
                                                                           facecolor='white',
                                                                           edgecolor='none',
                                                                           alpha=0.75))
                    else:
                        q1 = bp['boxes'][0].get_path().vertices[0, 1]
                        plt.text(x_pos*0.9, q1, rf"${l}$",
                                 ha='right', va='top', fontsize=12,
                                 fontweight='bold', color=color, bbox=dict(boxstyle='round,pad=0.1',
                                                                           facecolor='white',
                                                                           edgecolor='none',
                                                                           alpha=0.75))

        plt.axhline(y=1, color="black", linestyle='--')

        plt.ylabel(r"$\rho_{\delta} / \rho_{\small \textnormal{rtn}}$")
        plt.xlabel(r"$T_{\delta} / T_{\small \textnormal{rtn}}$")

        plt.yscale("log")
        plt.xscale("log")

        # ax.set_xscale('log')
        if distrib == "uniform" or distrib == "normal":
            xlims = ax.get_xlim()
            ax.set_xlim(xlims[0] * 0.6, xlims[1])

        plt.legend(all_bp[::-1], couples[::-1])

        plt.tight_layout()

        plt.savefig(f"{save_img_dir}/choiceParam_distrib={distrib}.pdf",
                    bbox_inches="tight", pad_inches=0.03)
        plt.close()


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    plot_choice_param(arguments)
