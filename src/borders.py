import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import LinearRing, LineString, Polygon, Point
from shapely.affinity import rotate


def polygon_from_lines(lines):
    """
    From a list of lines, returns the polygon generated with the intersections
    """
    points = []
    for i in range(len(lines)):
        p = lines[i].intersection(lines[(i+1) % len(lines)])
        if not p.is_empty:
            points.append((p.x, p.y))

    return Polygon(points)


def polygon_to_lines(polygon):
    """
    Returns the sides of the polygon
    """
    exterior_coords = list(polygon.exterior.coords)
    lines = []
    for i in range(len(exterior_coords) - 1):
        line = LineString([exterior_coords[i], exterior_coords[i + 1]])
        lines.append(line)
    return lines


class Ring:
    """
    Class for the ring border defined by two circles of radii 1 and 2 restricted to the top-right quadrant.
    """

    def compute_polygons(self, all_affine_functions):
        """
        From a list of breaklines, computes the associated accumulation lines,
        the smallest distance between breaklines and accumulation lines and adds the ring border to the list of breaklines.

        all_affine_functions is a list of list of tuples (a, b) defining the lines y = a x + b or x = b if a is 'inf'.
        each list corresponds to one accumulation line.

        Parameters
        ----------
        all_affine_functions: List of list of tuples defining the breaklines.
            list[list[tuple(float, float)]]

        Returns
        -------
        lines: List of shapely LineString corresponding to the breaklines and the ring border.
            list[shapely.geometry.LineString]
        accum_lines: List of shapely LineString corresponding to the accumulation lines.
            list[shapely.geometry.LineString]
        all_min_a_pos: List of smallest slopes among the breaklines for each accumulation line.
            list[float]
        all_min_b_pos: List of smallest intercepts among the breaklines for each accumulation line.
            list[float]
        """
        x_range = (-2, 2)
        x_vals = np.array(x_range)
        lines = []
        all_min_b_pos = [np.inf] * len(all_affine_functions)
        all_min_a_pos = [np.inf] * len(all_affine_functions)
        accum_lines = []
        for i, affine_functions in enumerate(all_affine_functions):
            for a, b in affine_functions:
                if isinstance(a, str):
                    lines.append(LineString([(b, -2), (b, 2)]))
                else:
                    y_vals = a * x_vals + b
                    lines.append(LineString(
                        [(x_vals[0], y_vals[0]), (x_vals[1], y_vals[1])]))

                # Limit affine lines
                if b > 0 and b < all_min_b_pos[i]:
                    all_min_b_pos[i] = b
                    all_min_a_pos[i] = a

            accum_lines.append(LineString(
                [(0, 0), (2, 2 * affine_functions[0][0])]))

        # Add the two circles
        theta = np.linspace(0, 2 * np.pi, 100)
        inner_circle = LinearRing(
            [(1 * np.cos(t), 1 * np.sin(t)) for t in theta])
        outer_circle = LinearRing(
            [(2 * np.cos(t), 2 * np.sin(t)) for t in theta])
        lines.extend([inner_circle, outer_circle])

        # Add the two axes
        x_axis = LineString([(0, 0), (2, 0)])
        y_axis = LineString([(0, 0), (0, 2)])
        lines.extend([x_axis, y_axis])

        return lines, accum_lines, all_min_a_pos, all_min_b_pos

    def filter_polygons(self, polygons):
        """
        Filters the polygons to only keep those that are inside the ring border.

        Parameters
        ----------
        polygons: List of shapely Polygons to filter.
            list[shapely.geometry.Polygon]

        Returns
        -------
        filtered_polygons: List of shapely Polygons inside the ring border.
            list[shapely.geometry.Polygon]
        """
        # Computes the ring border
        theta = np.linspace(0, 2 * np.pi, 100)
        inner_circle = LinearRing(
            [(1 * np.cos(t), 1 * np.sin(t)) for t in theta])
        outer_circle = LinearRing(
            [(2 * np.cos(t), 2 * np.sin(t)) for t in theta])

        border = Polygon(outer_circle).difference(Polygon(inner_circle))

        # Filters polygons to be inside the two circles
        polygons_within_ring = [
            poly for poly in polygons if border.contains(poly.centroid)
        ]

        # Filters polygons to be inside the right-up corner
        return [
            poly for poly in polygons_within_ring if poly.centroid.x > 0 and poly.centroid.y > 0
        ]

    def add_breakpoints_accum(self, x_scale):
        """
        Returns the intersection between the accumulation line associated to x_scale and the ring border.

        Parameters
        ----------
        x_scale: Scaling factor defining the accumulation line.
            complex

        Returns
        -------
        breakpoints: List of complex numbers corresponding to the intersection points.
            list[complex]
        """
        a = np.real(x_scale)
        b = np.imag(x_scale)

        return [
            b / np.abs(x_scale) + 1j * a / np.abs(x_scale),
            2 * b / np.abs(x_scale) + 1j * 2 * a / np.abs(x_scale)
        ]

    def filter_breakpoints(self, x, y):
        """
        Checks if the point (x, y) is inside the ring border.

        Parameters
        ----------
        x: x-coordinate of the point.
            float
        y: y-coordinate of the point.
            float

        Returns
        -------
        is_inside: True if the point is inside the ring border, False otherwise.
            bool
        """
        return 1 <= np.sqrt(y**2 + x**2) <= 2 and y >= 0 and x >= 0

    def filter_quadrant(self, x, y, ring_inner=1, ring_outer=2):
        """
        Filters the points to only keep those that are inside the ring border and the right-up corner.

        Parameters
        ----------
        x: x-coordinates of the points.
            numpy.ndarray
        y: y-coordinates of the points.
            numpy.ndarray
        ring_inner: Inner radius of the ring border.
            float
        ring_outer: Outer radius of the ring border.
            float

        Returns
        -------
        filtered_x: x-coordinates of the points inside the ring border.
            numpy.ndarray
        filtered_y: y-coordinates of the points inside the ring border.
            numpy.ndarray
        """
        i1 = np.where(y > 0)[0]
        i2 = np.where(y < ring_outer)[0]
        i3 = np.where(x > 0)[0]
        i4 = np.where(x < ring_outer)[0]
        i5 = np.where(x**2 + y**2 < ring_outer**2)[0]
        i6 = np.where(x**2 + y**2 > ring_inner**2)[0]

        i12 = np.intersect1d(i1, i2)
        i34 = np.intersect1d(i3, i4)
        i56 = np.intersect1d(i5, i6)

        i14 = np.intersect1d(i12, i34)
        i16 = np.intersect1d(i14, i56)

        return (x[i16], y[i16])

    def plot_affine_functions(self, affine_functions, ring_outer=2):
        """
        Plots the breaklines and keeps them in the ring border.

        Parameters
        ----------
        affine_functions: List of tuples defining the breaklines.
            list[tuple(float, float)]
        ring_outer: Outer radius of the ring border.
            float
        """
        x_vals = np.linspace(-ring_outer, ring_outer, 1000)
        for a, b in affine_functions:
            if type(a) == str:
                x_vals = b * np.ones_like(x_vals)
                y_vals = np.linspace(-ring_outer, ring_outer, 1000)
            else:
                y_vals = a * x_vals + b

            # Filter x and y values to be in the ring and the right-up corner
            x_keep, y_keep = self.filter_quadrant(x_vals, y_vals)

            plt.plot(x_keep, y_keep, color="black", linewidth=0.5)

    def plot_accumulation_lines(self, z):
        """
        Plots the accumulation lines associated to each element of z.

        Parameters
        ----------
        z: List of complex numbers defining the accumulation lines.
            numpy.ndarray
        """
        x_vals = np.linspace(-2, 2, 100)

        lines = []
        for zi in z:
            lines.append(np.real(zi) / np.imag(zi))
            plt.plot(x_vals, (np.real(zi) / np.imag(zi))
                     * x_vals, color="tab:orange", linewidth=0.5)

        return lines


def build_tiling_domain(normalized_direction_set, t):
    """
    Builds the tiling domain (trapezoid or L-shape) according to the normalized direction set and the number of significand bits t.

    Parameters
    ----------
    normalized_direction_set: Set of normalized directions.
        list[complex]
    t: Number of significand bits.
        int

    Returns
    -------
    TilingDomain object corresponding to the tiling domain.
        TilingDomain
    """
    z_ref = normalized_direction_set[0]

    y_vals = np.linspace(-100, 100, 2)
    base_A_z = LineString([(0, y_vals[0]), (0, y_vals[1])])

    # The two non-parallel sides of the trapezoid
    A_z = rotate(base_A_z, -np.degrees(np.angle(z_ref)), origin=(0, 0))
    A_iz = rotate(A_z, 90, origin=(0, 0))

    new_normalized_set = []
    for z in normalized_direction_set:
        if np.abs(np.angle(z) - np.angle(z_ref)) % (np.pi/2) <= 1e-2:
            continue
        if np.abs(np.angle(z) % (np.pi/2) - np.angle(z_ref) % (np.pi/2)) <= 1e-2:
            continue

        new_normalized_set.append(z)

    beta = (2**t + 1) * 2**(-t)

    if len(new_normalized_set) == 0:  # L-shape case
        base_D_z_beta_2 = LineString(
            [(0.5 * beta / np.abs(z_ref), -100), (0.5 * beta / np.abs(z_ref), 100)])
        base_D_z_beta = LineString(
            [(beta / np.abs(z_ref), -100), (beta / np.abs(z_ref), 100)])

        D_z_beta_2 = rotate(
            base_D_z_beta_2, 90 - np.degrees(np.angle(z_ref)), origin=(0, 0))
        D_z_beta = rotate(
            base_D_z_beta, 90 - np.degrees(np.angle(z_ref)), origin=(0, 0))

        D_iz_beta = rotate(D_z_beta, 90, origin=(0, 0))
        D_iz_beta_2 = rotate(D_z_beta_2, 90, origin=(0, 0))

        long_lines_border = [A_iz, D_iz_beta_2,
                             D_z_beta_2, A_z, D_z_beta, D_iz_beta]
    else:  # Trapezoid case
        z_ref2 = new_normalized_set[0]

        base_D_iz_bis_beta_2 = LineString(
            [(0.5 * beta / np.abs(z_ref2), -100), (0.5 * beta / np.abs(z_ref2), 100)])
        base_D_iz_bis_beta = LineString(
            [(beta / np.abs(z_ref2), -100), (beta / np.abs(z_ref2), 100)])

        D_iz_bis_beta_2 = rotate(
            base_D_iz_bis_beta_2, 90 - np.degrees(np.angle(z_ref2)), origin=(0, 0))
        D_iz_bis_beta = rotate(base_D_iz_bis_beta, 90 -
                               np.degrees(np.angle(z_ref2)), origin=(0, 0))

        long_lines_border = [A_z, D_iz_bis_beta_2, A_iz, D_iz_bis_beta]

    return TilingDomain(long_lines_border)


class TilingDomain:
    """
    Class for the tiling domain defined by its border (trapezoid or L-shape).

    Attributes
    ----------
    long_lines_border: List of shapely LineString corresponding to the lines defining the border without restriction to the border.
        list[shapely.geometry.LineString]
    border: Shapely Polygon corresponding to the border.
        shapely.geometry.Polygon
    lines_border: List of shapely LineString corresponding to the sides of the border.
        list[shapely.geometry.LineString]
    area: Area of the border.
        float
    """

    def __init__(self, long_lines_border):
        self.long_lines_border = long_lines_border
        self.border = polygon_from_lines(self.long_lines_border)

        self.lines_border = polygon_to_lines(self.border)

        self.area = self.border.area

    def get_breakpoint_accum(self, acc_line):
        """
        Returns the intersection between the accumulation line and the trapezoid.

        Parameters
        ----------
        acc_line: Accumulation line.
            shapely.geometry.LineString

        Returns
        -------
        breakpoint: Complex number corresponding to the intersection point.
            complex
        """
        inter = self.long_lines_border[1].intersection(acc_line)
        breakpoint = None
        if not inter.is_empty:
            if inter.geom_type == "Point":
                breakpoint = inter.xy[0][0] + 1j * inter.xy[1][0]

        return breakpoint

    def filter_all_breaklines(self, all_breaklines):
        """
        Filters the breaklines to only keep the part that are inside the trapezoid.

        Parameters
        ----------
        all_breaklines: List of list of shapely LineString corresponding to the breaklines.
            list[list[shapely.geometry.LineString]]

        Returns
        -------
        filtered_breaklines: List of list of shapely LineString corresponding to the filtered breaklines.
            list[list[shapely.geometry.LineString]]
        """
        filtered_breaklines = []
        for breaklines in all_breaklines:
            filtered_lines = []
            for breakline in breaklines:
                inter = breakline.intersection(self.border)
                if not inter.is_empty:
                    if inter.geom_type == "MultiLineString":
                        filtered_lines.extend(list(inter.geoms))
                    elif inter.geom_type == "LineString":
                        filtered_lines.append(inter)

            filtered_breaklines.append(filtered_lines)

        return filtered_breaklines

    def filter_breaklines(self, breaklines):
        """
        Filters the breaklines to only keep the part that are inside the trapezoid.

        Parameters
        ----------
        breaklines: List of shapely LineString corresponding to the breaklines.
            list[shapely.geometry.LineString]

        Returns
        -------
        filtered_lines: List of shapely LineString corresponding to the filtered breaklines.
            list[shapely.geometry.LineString]
        """
        filtered_lines = []
        for breakline in breaklines:
            inter = self.border.intersection(breakline)
            if not inter.is_empty:
                if inter.geom_type == "MultiLineString":
                    filtered_lines.extend(list(inter.geoms))
                elif inter.geom_type == "LineString":
                    filtered_lines.append(inter)

        return filtered_lines

    def filter_polygons(self, polygons):
        """
        Filters the polygons to keep those that are inside the trapezoid.

        Parameters
        ----------
        polygons: List of shapely Polygon objects.
            list[shapely.geometry.Polygon]

        Returns
        -------
        filtered_polygons: List of shapely Polygon objects that are inside the trapezoid.
            list[shapely.geometry.Polygon]
        """
        return [
            poly for poly in polygons if self.border.contains(poly.centroid)
        ]

    def inside_border(self, x, y):
        """
        Checks if the point (x, y) is inside the trapezoid.

        Parameters
        ----------
        x: x-coordinate of the point.
            float
        y: y-coordinate of the point.
            float

        Returns
        -------
        is_inside: True if the point is inside the trapezoid, False otherwise.
            bool
        """
        return self.border.contains(Point(x, y))

    def plot_domain(self):
        border_x = [coord[0] for coord in self.border.exterior.coords]
        border_y = [coord[1] for coord in self.border.exterior.coords]

        plt.plot(border_x, border_y, color="#FF1924", linewidth=5)

    def plot_breaklines(self, breaklines):
        """
        Plots the breaklines and keeps them in the trapezoid.

        Parameters
        ----------
        breaklines: List of shapely LineString corresponding to the breaklines.
            list[shapely.geometry.LineString]
        """
        filtered_breaklines = self.filter_breaklines(breaklines)
        for breakline in filtered_breaklines:
            x, y = breakline.xy
            plt.plot(x, y, color="black", linewidth=0.5)

    def plot_accumulation_lines(self, direction_set, filter_lines=True):
        """
        Plots the accumulation lines associated to each element of direction_set.

        Parameters
        ----------
        direction_set: List of complex numbers defining the accumulation lines.
            numpy.ndarray
        filter_lines: If True, only plots the part of the accumulation lines that intersect the trapezoid.
            bool
        """
        for z in direction_set:
            if z == 0:
                continue

            y_vals = np.linspace(-100, 100, 2)
            base_line = LineString([(0, y_vals[0]), (0, y_vals[1])])
            acc_line = rotate(
                base_line, -np.degrees(np.angle(z)), origin=(0, 0))

            if filter_lines:
                inter = self.border.intersection(acc_line)
                if inter.is_empty:
                    continue

            x, y = acc_line.xy
            plt.plot(x, y, color="#FC9200", linewidth=2.5, linestyle="--")
