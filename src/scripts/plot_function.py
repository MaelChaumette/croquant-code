import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Polygon as MplPolygon, Wedge
from matplotlib.lines import Line2D

from pathlib import Path

from shapely.geometry import Polygon
from shapely.affinity import scale, rotate

from src.borders import build_tiling_domain
from src.complex_case import C, generate_midpoints, generate_directions, from_direction_midpoints_to_breaklines, get_polygons, find_e_max, find_e_min, normalize_direction_set
from src.plot_utils import configure_plt


configure_plt(fontsize=16)

plt.rcParams.update({
    "text.latex.preamble": r"""
\usepackage[T1]{fontenc}
\usepackage[tt=false, type1=true]{libertine}
\usepackage[libertine]{newtxmath}
""",
})


def rotate90(poly, angle):
    return rotate(poly, angle=angle, origin=(0, 0))


def scale2(poly, power):
    return scale(poly, xfact=2**power, yfact=2**power, origin=(0, 0))


def scale_half(poly, power):
    return scale(poly, xfact=0.5**power, yfact=0.5**power, origin=(0, 0))


def plot_compare_tiling_domains(args):
    size = args.n
    bit = args.bit
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    np.random.seed(args.seed)

    x = np.random.rand(size) + 1j * np.random.rand(size)
    y = np.random.rand(size) + 1j * np.random.rand(size)

    normalized_direction_set = normalize_direction_set(generate_directions(x))

    colors = []

    tiling_domain = build_tiling_domain(normalized_direction_set, bit)
    border = tiling_domain.border
    border_x = [coord[0] for coord in border.exterior.coords]
    border_y = [coord[1] for coord in border.exterior.coords]

    e_max = find_e_max(normalized_direction_set, bit, tiling_domain)
    all_betas_huge = generate_midpoints(bit, e_max, -6)
    # all_betas = generate_midpoints(bit, e_max, -delta)

    breaklines_huge = from_direction_midpoints_to_breaklines(
        normalized_direction_set, all_betas_huge)
    # breaklines = from_direction_midpoints_to_breaklines(
    #     normalized_direction_set, all_betas)

    # zoom_domain = Polygon(
    #     [(0.55, 0.25), (0.75, 0.25), (0.75, 0.45), (0.55, 0.45)])
    # border_x_zoom = [coord[0] for coord in zoom_domain.exterior.coords]
    # border_y_zoom = [coord[1] for coord in zoom_domain.exterior.coords]

    regions = [border]
    for line in sum(breaklines_huge, []):
        new_regions = []
        for reg in regions:
            cut = reg.difference(line.buffer(1e-12))
            if cut.is_empty:
                new_regions.append(reg)
            else:
                if hasattr(cut, "geoms"):
                    new_regions.extend(cut.geoms)
                else:
                    new_regions.append(cut)
        regions = new_regions

    c_values = []
    for reg in regions:
        centroid = reg.representative_point()
        c_val = np.sqrt(np.real(
            C(x, y, centroid.x + 1j * centroid.y, bit)))
        c_values.append(c_val)

    vmin, vmax = min(c_values), max(c_values)
    cmap = plt.get_cmap("cividis")
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    full_regions_values_scaled = []
    for k in range(6):
        for reg, v in zip(regions, c_values):
            if k == 0:
                full_regions_values_scaled.append((reg, v))
            else:
                new_scaled2 = scale2(reg, power=k)
                new_scaled_half = scale_half(reg, power=k)

                full_regions_values_scaled.append((new_scaled2, v))
                full_regions_values_scaled.append((new_scaled_half, v))

    full_regions_values = []
    for l in range(4):
        for reg, v in full_regions_values_scaled:
            new_rotated = rotate90(reg, angle=90 * l)

            full_regions_values.append((new_rotated, v))

    # Plot multiple tiling domains
    fig, ax = plt.subplots()

    display_domain = Polygon([(-2, -2), (2, -2), (2, 2), (-2, 2)])

    for reg, val in full_regions_values:
        visible_reg = reg.intersection(display_domain)
        if visible_reg.is_empty:
            continue

        color = cmap(norm(val))
        ax.add_patch(MplPolygon(list(reg.exterior.coords),
                     facecolor=color, edgecolor="none"))

    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(
        sm, ax=ax, label=r"$\frac{|| x y^H - \hat{x}(\lambda) \hat{y}(\lambda)^H ||}{|| x y^H ||}$")

    # Poly border
    plt.plot(border_x, border_y, color="#FF1924", linewidth=5)
    plt.fill(border_x, border_y, hatch="////",
             edgecolor="#FF1924", facecolor="none", linewidth=0)

    # Ring border
    # u = np.linspace(0, 2, 100)
    # plt.plot(u, np.sqrt(4 - u**2), color="tab:blue",
    #          linewidth=5, linestyle="-.")

    # u = np.linspace(0, 1, 100)
    # plt.plot(u, np.sqrt(1 - u**2), color="tab:blue",
    #          linewidth=5, linestyle="-.")

    # plt.plot([1, 2], [0, 0], color="tab:blue", linewidth=5, linestyle="-.")
    # plt.plot([0, 0], [1, 2], color="tab:blue", linewidth=5, linestyle="-.")

    ring = Wedge(
        center=(0, 0),
        r=2,
        theta1=0,
        theta2=90,
        width=1,
        facecolor="none",
        edgecolor="#0055C9",
        linewidth=5,
        linestyle="--",
        hatch="..."
    )
    ax.add_patch(ring)

    tiling_domain.plot_accumulation_lines(
        normalized_direction_set, filter_lines=False)

    plt.ylim(-2, 2)
    plt.xlim(-2, 2)

    plt.ylabel(r"$\mathrm{Im}(\lambda)$")
    plt.xlabel(r"$\mathrm{Re}(\lambda)$")

    plt.gca().set_aspect("equal", adjustable="box")

    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/invarianceWithBorder_n={size}_t={bit}_seed={args.seed}.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close()


def plot_one_tiling_domain(args):
    size = args.n
    bit = args.bit
    delta = args.delta
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    np.random.seed(args.seed)

    x = np.random.rand(size) + 1j * np.random.rand(size)
    y = np.random.rand(size) + 1j * np.random.rand(size)

    normalized_direction_set = normalize_direction_set(generate_directions(x))

    tiling_domain = build_tiling_domain(normalized_direction_set, bit)
    border = tiling_domain.border
    border_x = [coord[0] for coord in border.exterior.coords]
    border_y = [coord[1] for coord in border.exterior.coords]

    e_max = find_e_max(normalized_direction_set, bit, tiling_domain)
    all_betas_huge = generate_midpoints(bit, e_max, -8)
    all_betas = generate_midpoints(bit, e_max, -delta)

    breaklines_huge = from_direction_midpoints_to_breaklines(
        normalized_direction_set, all_betas_huge)
    breaklines = from_direction_midpoints_to_breaklines(
        normalized_direction_set, all_betas)

    zoom_domain = Polygon(
        [(0.55, 0.25), (0.75, 0.25), (0.75, 0.45), (0.55, 0.45)])
    border_x_zoom = [coord[0] for coord in zoom_domain.exterior.coords]
    border_y_zoom = [coord[1] for coord in zoom_domain.exterior.coords]

    regions = [border]
    for line in sum(breaklines_huge, []):
        new_regions = []
        for reg in regions:
            cut = reg.difference(line.buffer(1e-12))
            if cut.is_empty:
                new_regions.append(reg)
            else:
                if hasattr(cut, "geoms"):
                    new_regions.extend(cut.geoms)
                else:
                    new_regions.append(cut)
        regions = new_regions

    c_values = []
    for reg in regions:
        centroid = reg.representative_point()
        c_val = np.sqrt(np.real(
            C(x, y, centroid.x + 1j * centroid.y, bit)))
        c_values.append(c_val)

    vmin, vmax = min(c_values), max(c_values)
    cmap = plt.get_cmap("cividis")
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    full_regions_values_scaled = []
    for k in range(8):
        for reg, v in zip(regions, c_values):
            if k == 0:
                full_regions_values_scaled.append((reg, v))
            else:
                new_scaled2 = scale2(reg, power=k)
                new_scaled_half = scale_half(reg, power=k)

                full_regions_values_scaled.append((new_scaled2, v))
                full_regions_values_scaled.append((new_scaled_half, v))

    full_regions_values = []
    for l in range(4):
        for reg, v in full_regions_values_scaled:
            new_rotated = rotate90(reg, angle=90 * l)

            full_regions_values.append((new_rotated, v))

    fig, ax = plt.subplots()

    display_domain = Polygon([
        (min(border_x + [0]), min(border_y + [0])),
        (max(border_x), min(border_y + [0])),
        (max(border_x), max(border_y)),
        (min(border_x + [0]), max(border_y))
    ])

    for reg, val in full_regions_values:
        visible_reg = reg.intersection(display_domain)
        if visible_reg.is_empty:
            continue

        color = cmap(norm(val))
        ax.add_patch(MplPolygon(list(reg.exterior.coords),
                     facecolor=color, edgecolor="none"))

    tiling_domain.plot_breaklines(sum(breaklines, []))
    tiling_domain.plot_domain()

    if args.draw_zoom:
        plt.plot(border_x_zoom, border_y_zoom,
                 color="#A5CF00", linewidth=3, linestyle="--")

    tiling_domain.plot_accumulation_lines(
        normalized_direction_set, filter_lines=False)

    plt.ylabel(r"$\mathrm{Im}(\lambda)$")
    plt.xlabel(r"$\mathrm{Re}(\lambda)$")

    plt.ylim(min(border_y + [0]), max(border_y))
    plt.xlim(min(border_x + [0]), max(border_x))

    plt.gca().set_aspect("equal", adjustable="box")

    plt.tight_layout()

    plt.savefig(
        f"{save_img_dir}/complexBreakpointsPoly_n={size}_t={bit}_delta={delta}_seed={args.seed}_zoom={args.draw_zoom}.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close()

    if args.draw_zoom:
        # Zoom near an accumulation line
        fig, ax = plt.subplots()

        for reg, val in full_regions_values:
            visible_reg = reg.intersection(zoom_domain)
            if visible_reg.is_empty:
                continue

            color = cmap(norm(val))
            ax.add_patch(MplPolygon(list(reg.exterior.coords),
                                    facecolor=color, edgecolor="none"))

        tiling_domain.plot_breaklines(sum(breaklines_huge, []))

        tiling_domain.plot_accumulation_lines(
            normalized_direction_set, filter_lines=False)

        plt.ylabel(r"$\mathrm{Im}(\lambda)$")
        plt.xlabel(r"$\mathrm{Re}(\lambda)$")

        plt.ylim(0.25, 0.45)
        plt.xlim(0.55, 0.75)

        plt.gca().set_aspect("equal", adjustable="box")

        plt.tight_layout()

        plt.savefig(
            f"{save_img_dir}/complexBreakpointsPolyZoom_n={size}_t={bit}_seed={args.seed}.pdf", bbox_inches="tight", pad_inches=0.03)
        plt.close()


def plot_impact_param(args):
    size = args.n
    bit = args.bit
    save_img_dir = Path(args.save_img_dir)

    save_img_dir.mkdir(exist_ok=True, parents=True)

    np.random.seed(args.seed)

    x = np.random.rand(size) + 1j * np.random.rand(size)
    y = np.random.rand(size) + 1j * np.random.rand(size)

    normalized_direction_set = normalize_direction_set(generate_directions(x))

    tiling_domain = build_tiling_domain(x, bit)
    border = tiling_domain.border
    border_x = [coord[0] for coord in border.exterior.coords]
    border_y = [coord[1] for coord in border.exterior.coords]

    e_max = find_e_max(normalized_direction_set, bit, tiling_domain)
    e_min = find_e_min(normalized_direction_set, bit, tiling_domain)

    for e in [e_min - 3, e_min - 2, e_min - 1, e_min, e_min + 1, e_min + 2][::-1]:
        all_betas = generate_midpoints(bit, e_max, e)

        breaklines = from_direction_midpoints_to_breaklines(
            normalized_direction_set, all_betas)

        polygons = get_polygons(normalized_direction_set,
                                all_betas, tiling_domain)

        c_values = []
        for reg in polygons:
            centroid = reg.representative_point()
            c_val = np.sqrt(np.real(
                C(x, y, centroid.x + 1j * centroid.y, bit)))
            c_values.append(c_val)

        fig, ax = plt.subplots()

        if len(c_values) > 0:
            vmin, vmax = min(c_values), max(c_values)
            cmap = plt.get_cmap("cividis_r")
            norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

            for reg, val in zip(polygons, c_values):
                val = c_values[0]
                visible_reg = reg.intersection(border)
                if visible_reg.is_empty:
                    continue

                # color = cmap(norm(val))
                ax.add_patch(MplPolygon(list(reg.exterior.coords),
                                        facecolor="#595959", edgecolor="none"))

        tiling_domain.plot_domain()
        tiling_domain.plot_breaklines(sum(breaklines, []))
        tiling_domain.plot_accumulation_lines(
            normalized_direction_set, filter_lines=False)

        proxy = Line2D([], [], linewidth=None, color="white")

        plt.ylim(min(border_y) * 1.1, max(border_y) * 1.1)
        plt.xlim(min(border_x) / 1.1, max(border_x) * 1.1)

        plt.ylabel(r"$\mathrm{Im}(\lambda)$")
        plt.xlabel(r"$\mathrm{Re}(\lambda)$")

        plt.legend([proxy], [fr"$e = {e}$"], handlelength=0, handletextpad=0)

        plt.gca().set_aspect("equal", adjustable="box")

        plt.tight_layout()

        plt.savefig(
            f"{save_img_dir}/impactParam_n={size}_t={bit}_e={e}.pdf", bbox_inches="tight", pad_inches=0.03)
        plt.close()


if __name__ == "__main__":
    from src.parse_arguments import get_args
    arguments = get_args()

    if arguments.function in globals():
        globals()[arguments.function](arguments)
