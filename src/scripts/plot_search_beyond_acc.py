import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path as MplPath

from pathlib import Path

from src.gather_results import gather_results
from src.plot_utils import configure_plt


configure_plt(fontsize=16)

plt.rcParams.update({
    "text.latex.preamble": r"""
\usepackage[T1]{fontenc}
\usepackage[tt=false, type1=true]{libertine}
\usepackage[libertine]{newtxmath}
\usepackage{amsfonts}
""",
})


def create_hatched_star(ax, x, y, size, color, hatch):
    n_points = 10
    angles = np.linspace(0, 2*np.pi, n_points + 1)

    # Alterner entre rayon externe (branches) et rayon interne (creux)
    radii = np.array([size if i % 2 == 0 else size *
                     0.382 for i in range(n_points + 1)])

    # Calculer les coordonnées x, y
    xs = x + radii * np.sin(angles)
    ys = y + radii * np.cos(angles)

    # Créer le Path
    verts = list(zip(xs, ys))
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * \
        (n_points - 1) + [MplPath.CLOSEPOLY]
    path = MplPath(verts, codes)

    # Créer le patch avec motif
    patch = PathPatch(path, facecolor=color, edgecolor='black',
                      hatch=hatch, linewidth=1., zorder=10)
    ax.add_patch(patch)


def plot_error_per_delta(args):
    save_dir = args.save_dir
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    df_error_per_delta, _, param_values = gather_results(
        save_dir, "error_per_delta.csv")

    all_pairs = ["$m=32, n=32$", "$m=32, n=2$",
                 "$m=2, n=32$", "$m=2, n=2$"]
    hue_order = ["$m=2, n=2$", "$m=2, n=32$",
                 "$m=32, n=2$", "$m=32, n=32$"]
    base_colors = sns.color_palette("Set2", n_colors=len(all_pairs))
    colors = ["#FF1924", "#FC9200", "#A5CF00", "#0055C9"]
    palette = dict(zip(all_pairs, colors))

    hatches = ["", "///", "\\\\\\", "xxx"]
    hatch_dict = dict(zip(hue_order, hatches))

    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    for i, distrib in enumerate(["uniform", "roots_of_unity"]):
        df_filter = df_error_per_delta.loc[(df_error_per_delta["distrib"] == distrib)].drop([
            "distrib"], axis=1)

        df_filter["mn"] = df_filter.apply(
            lambda row: f"$m={int(row.m)}, n={int(row.n)}$", axis=1)

        df_filter.sort_values(by=r"$\delta$", inplace=True)

        delta_order = list(df_filter[r"$\delta$"].unique())

        sns.violinplot(data=df_filter, x=r"$\delta$", y="Error", hue="mn",
                       cut=0, hue_order=hue_order, palette=palette, ax=axes[i])

        n_deltas = len(delta_order)
        n_hues = len(hue_order)
        for j, collection in enumerate(axes[i].collections):
            hue_idx = j % n_hues
            mn = hue_order[hue_idx]
            collection.set_hatch(hatch_dict[mn])
            collection.set_edgecolor('black')
            collection.set_linewidth(0.8)

        for mn_idx, mn in enumerate(hue_order):
            df_mn = df_filter[df_filter["mn"] == mn]

            min_row = df_mn.loc[df_mn["Error"].idxmin()]
            optimal_delta = min_row[r"$\delta$"]

            delta_idx = list(delta_order).index(optimal_delta)

            n_hue = len(hue_order)
            offset = 0.8 / n_hue

            x_pos = delta_idx + (mn_idx - (n_hue - 1) / 2) * offset
            y_max = df_mn[df_mn[r"$\delta$"] == optimal_delta]["Error"].min()

            axes[i].scatter(x_pos, y_max - 0.15, marker="*", s=1,
                            color=palette[mn], edgecolors="black", linewidths=0.5, zorder=10)

            create_hatched_star(
                axes[i], x_pos, y_max - 0.15, size=0.1, color=palette[mn], hatch=hatch_dict[mn])

        new_labels = []
        for delta_val in delta_order:
            if delta_val == 0:
                new_labels.append(r"$\Lambda_{\mathbb{A}}$")
            else:
                new_labels.append(rf"$\tilde{{\Lambda}}_{{{int(delta_val)}}}$")
        axes[i].set_xticklabels(new_labels)

        axes[i].axhline(y=1, color="black", linestyle="dashed")

        axes[i].set_ylabel(r"$\sqrt{f(\lambda) / f(1)}$")

    axes[0].set_xlabel("")
    axes[1].set_xlabel("")
    axes[0].legend_.remove()
    axes[1].legend_.remove()

    legend_elements = [
        Patch(facecolor=palette[mn], edgecolor='black', hatch=hatch_dict[mn],
              linewidth=0.8, label=mn)
        for mn in hue_order
    ]

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles=legend_elements, title="", loc="lower center",
               ncol=len(all_pairs), bbox_to_anchor=(0.5, -0.04))

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.11)
    fig.savefig(f"{save_img_dir}/error_per_delta.pdf", bbox_inches="tight")
    plt.close()

    ################## Unused plot code #######################
    # fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    # for i, distrib in enumerate(["normal", "finite_alphabet"]):
    #     df_filter = df_error_per_delta.loc[(df_error_per_delta["distrib"] == distrib)].drop([
    #         "distrib"], axis=1)

    #     df_filter["mn"] = df_filter.apply(
    #         lambda row: f"$m={int(row.m)}, n={int(row.n)}$", axis=1)

    #     df_filter.sort_values(by=r"$\delta$", inplace=True)

    #     delta_order = list(df_filter[r"$\delta$"].unique())

    #     sns.violinplot(data=df_filter, x=r"$\delta$", y="Error", hue="mn",
    #                    cut=0, hue_order=hue_order, palette=palette, ax=axes[i])

    #     for mn_idx, mn in enumerate(hue_order):
    #         df_mn = df_filter[df_filter["mn"] == mn]

    #         min_row = df_mn.loc[df_mn["Error"].idxmin()]
    #         optimal_delta = min_row[r"$\delta$"]

    #         delta_idx = list(delta_order).index(optimal_delta)

    #         n_hue = len(hue_order)
    #         offset = 0.8 / n_hue

    #         x_pos = delta_idx + (mn_idx - (n_hue - 1) / 2) * offset
    #         y_max = df_mn[df_mn[r"$\delta$"] == optimal_delta]["Error"].min()

    #         axes[i].scatter(x_pos, y_max - 0.15, marker="*", s=200,
    #                         color=palette[mn], edgecolors="black", linewidths=0.5, zorder=10)

    #     new_labels = []
    #     for delta_val in delta_order:
    #         if delta_val == 0:
    #             new_labels.append(r"$\Lambda_{\mathbb{A}}$")
    #         else:
    #             new_labels.append(rf"$\tilde{{\Lambda}}_{{{int(delta_val)}}}$")
    #     axes[i].set_xticklabels(new_labels)

    #     axes[i].axhline(y=1, color="black", linestyle="dashed")

    #     axes[i].set_ylabel(r"$\sqrt{f(\lambda) / f(1)}$")

    # axes[0].set_xlabel("")
    # axes[1].set_xlabel("")
    # axes[0].legend_.remove()
    # axes[1].legend_.remove()

    # handles, labels = axes[0].get_legend_handles_labels()
    # fig.legend(handles, labels, title="", loc="lower center",
    #            ncol=len(all_pairs), bbox_to_anchor=(0.5, -0.04))

    # fig.tight_layout()
    # fig.subplots_adjust(bottom=0.11)
    # fig.savefig(f"{save_img_dir}/error_per_delta_unused.pdf",
    #             bbox_inches="tight")
    # plt.close()


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    plot_error_per_delta(arguments)
