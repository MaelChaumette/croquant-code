import numpy as np

from shapely.geometry import LineString
from shapely.affinity import rotate
from shapely.ops import polygonize, unary_union


def relu(x):
    return x * (x > 0)


def chop_complex(x, t=24):
    """
    Quantizes the elements of the complex array x with t significant bits.

    Parameters
    ----------
    x: Input array.
        np.ndarray
    t: Number of bits for quantization.
        int

    Returns
    -------
    The quantized array.
        np.ndarray
    """
    if t == np.inf:
        return x

    if np.iscomplex(x).any() or x.dtype == complex or np.issubdtype(x.dtype, np.complexfloating):
        a, b = np.real(x), np.imag(x)

        return chop_complex(a, t) + chop_complex(b, t) * 1j

    y = np.abs(x) + (x == 0)

    e = np.floor(np.log2(y) + 1).astype(int)

    return np.ldexp(np.round(np.ldexp(x, t - e)), e - t)


def stochastic_chop_complex(x, t=24):
    """
    Quantizes the elements of the complex array x with t significant bits with a stochastic rounding strategy.

    Parameters
    ----------
    x: Input array.
        np.ndarray
    t: Number of bits for quantization.
        int

    Returns
    -------
    The quantized array.
        np.ndarray
    """
    if t == np.inf:
        return x

    if np.iscomplex(x).any() or x.dtype == complex or np.issubdtype(x.dtype, np.complexfloating):
        a, b = np.real(x), np.imag(x)

        return stochastic_chop_complex(a, t) + stochastic_chop_complex(b, t) * 1j

    y = np.abs(x) + (x == 0)

    e = np.floor(np.log2(y) + 1).astype(int)

    x_scaled = np.ldexp(x, t - e)
    lower = np.floor(x_scaled)
    upper = np.ceil(x_scaled)
    prob = x_scaled - lower

    rnd = np.random.uniform(size=x.shape)
    rounded = np.where(rnd < prob, upper, lower)
    return np.ldexp(rounded, e - t)


def fixed_chop_complex(x, t=24):
    """
    Performs fixed-point quantization on x with t-bit precision.

    Parameters
    ----------
    x: Input array.
        np.ndarray
    t: Number of bits for quantization.
        int

    Returns
    -------
    The quantized array.
        np.ndarray
    """
    if t == np.inf:
        return x

    if np.iscomplex(x).any() or x.dtype == complex or np.issubdtype(x.dtype, np.complexfloating):
        a, b = np.real(x), np.imag(x)

        return fixed_chop_complex(a, t) + 1j * fixed_chop_complex(b, t)

    scale = 2**(t - 1)
    x_scaled = x * scale

    x_quantized = np.round(x_scaled)

    return x_quantized / scale


def c(x, y, x_hat, y_hat):
    r"""
    Computes $|| x y^H - \hat{x} \hat{y}^H ||_F^2$.

    Parameters
    ----------
    x: Left vector.
        np.ndarray
    y: Right vector.
        np.ndarray
    x_hat: Quantized left vector.
        np.ndarray
    y_hat: Quantized right vector.
        np.ndarray

    Returns
    -------
    The computed Frobenius norm squared.
        float
    """
    return relu(
        (np.linalg.norm(x) * np.linalg.norm(y)) ** 2 +
        (np.linalg.norm(x_hat) * np.linalg.norm(y_hat)) ** 2 -
        2 * np.real(np.vdot(x_hat, x) * np.vdot(y, y_hat))
    )


def C(x, y, lbd, t):
    r"""
    Computes $|| x y^\top - \hat{x} \text{round}_t(\mu(\hat{x}) y) ||_F^2
    where $\hat{x} = \text{round}_t(\lambda x)$ and $\mu(\hat{x}) = \frac{\langle x, \hat{x} \rangle}{|| \hat{x} ||_2^2}$.

    Parameters
    ----------
    x: Left vector.
        np.ndarray
    y: Right vector.
        np.ndarray
    lbd: Scaling factor for x.
        complex
    t: Number of significand bits.
        int

    Returns
    -------
    The computed Frobenius norm squared.
        float
    """
    x_hat = chop_complex(lbd * x, t)

    mu = np.vdot(x, x_hat) / (np.linalg.norm(x_hat) ** 2)
    y_hat = chop_complex(mu * y, t)

    return relu(
        (np.linalg.norm(x) * np.linalg.norm(y)) ** 2 +
        (np.linalg.norm(x_hat) * np.linalg.norm(y_hat)) ** 2 -
        2 * np.real(np.vdot(x_hat, x) * np.vdot(y, y_hat))
    )


def generate_midpoints(t, e_max, e_min):
    r"""
    Generate the midpoints values $\mathbb{M}_t^*$ used for the quantization,
    restricted to e_min <= e <= e_max for tractability.

    Parameters
    ----------
    t: Number of bits for quantization.
        int
    e_max: Maximum value of e for tractability.
        int
    e_min: Minimum value of e for tractability.
        int
    """
    return [
        (k + 0.5) * 2**(e - t)
        for k in range(2**(t - 1), 2**t)
        for e in range(e_min, e_max + 1)
    ]


def generate_directions(x):
    r"""
    Generates the set $\mathbb{C}_x := \{ i^l x_j, l \in \{ 0, 1 \}, j = 1, ..., m, x_j \neq 0 \}$.

    Parameters
    ----------
    x: Input vector.
        np.ndarray

    Returns
    -------
    list of directions of x
        list[complex]
    """
    x_nz = x[x != 0]

    return np.concat(((1j)**0 * x_nz, (1j)**1 * x_nz), axis=0)


def normalize_direction_set(direction_set):
    """
    Normalize the given set of directions.

    Parameters
    ----------
    direction_set: list of complex numbers
        The set of directions to normalize.

    Returns
    -------
    list of normalized complex numbers
        list[complex]
    """
    return [
        z / (2 ** np.floor(np.log2(np.abs(z))))
        for z in direction_set
    ]


def from_direction_midpoints_to_breaklines(direction_set, midpoint_set):
    r"""
    Returns the list of breaklines from the sets $\mathbb{C}_x$ and $\mathbb{M}_t^*$.

    Each breakline of equation $Re(\lambda z) = \beta$ corresponds to the line $\Re(\lambda) = \beta / \lvert z \rvert$ after a rotation of $\arg(z)$.

    Each list is associated to one accumulation line.

    Parameters
    ----------
    direction_set: List of directions of x.
        list[complex]
    midpoint_set: List of midpoints values.
        list[float]

    Returns
    -------
    list of breaklines
        list[list[LineString]]
    """
    all_breaklines = []
    for z in direction_set:
        if z == 0:
            continue
        y_vals = np.linspace(-100, 100, 2)
        angle_deg = np.degrees(np.angle(z))

        breaklines = []
        for beta in midpoint_set:
            for s in [-1, 1]:
                base_line = LineString([(s * beta / np.abs(z), y_vals[0]),
                                        (s * beta / np.abs(z), y_vals[1])])
                rotated_line = rotate(
                    base_line, -angle_deg, origin=(0, 0))

                breaklines.append(rotated_line)

        all_breaklines.append(breaklines)

    return all_breaklines


def find_e_max(direction_set, t, border):
    """
    Finds the largest e such that there exists at least one breakline in the border.

    Parameters
    ----------
    direction_set: list of directions of x
        list[complex]
    t: Number of bits for quantization.
        int
    border: Tiling domain
        TilingDomain

    Returns
    -------
    The largest e value.
        int
    """
    e = 0

    midpoint_set = generate_midpoints(t, e, e)
    breaklines = from_direction_midpoints_to_breaklines(
        direction_set, midpoint_set)
    breaklines_in_border = sum(border.filter_all_breaklines(breaklines), [])
    if len(breaklines_in_border) == 0:
        direction = -1
    else:
        direction = 1

    while True:
        if len(breaklines_in_border) == 0:
            if direction == 1:
                return e - 1

            e -= 1

        else:
            if direction == -1:
                return e

            e += 1

        midpoint_set = generate_midpoints(t, e, e)
        breaklines = from_direction_midpoints_to_breaklines(
            direction_set, midpoint_set)
        breaklines_in_border = sum(
            border.filter_all_breaklines(breaklines), [])


def find_e_min(normalized_direction_set, t, border):
    r"""
    Finds the smallest e such that the set of stable regions is empty.

    Parameters
    ----------
    direction_set: list of directions of x
        list[complex]
    t: Number of bits for quantization.
        int
    border: Tiling domain
        TilingDomain

    Returns
    -------
    The smallest e value.
        int
    """
    def is_covered(e, normalized_direction_set, t, polygon_border):
        r"""
        Checks if the border is covered by the accumulation polygons associated to the directions in normalized_direction_set.

        Parameters
        ----------
        normalized_direction_set: list of normalized directions of x
            list[complex]
        t: number of bits for quantization
            int
        border: Tiling domain
            TilingDomain

        Returns
        -------
        True if the border is covered, False otherwise.
            bool
        """
        accum_polygons = []
        for z in normalized_direction_set:
            if z == 0:
                continue

            y_vals = np.linspace(-100, 100, 2)
            base_line = LineString([(0, y_vals[0]), (0, y_vals[1])])
            accum_line = rotate(
                base_line, -np.degrees(np.angle(z)), origin=(0, 0))

            beta_min = (2**t + 1) * 2**(e-t - 1)

            if np.imag(z) == 0:
                dist = beta_min / np.real(z)
            else:
                dist = beta_min * np.sin(np.angle(z)) / np.imag(z)

            accum_polygons.append(accum_line.buffer(dist))

        union_accum_polygons = unary_union(accum_polygons)
        return polygon_border.difference(union_accum_polygons).is_empty

    e = 0

    polygon_border = border.border

    covered = is_covered(e, normalized_direction_set, t, polygon_border)

    if covered:
        direction = -1
    else:
        direction = 1

    while True:
        if covered:
            if direction == 1:
                return e

            e -= 1
        else:
            if direction == -1:
                return e + 1

            e += 1

        covered = is_covered(e, normalized_direction_set, t, polygon_border)


def get_polygons(normalized_direction_set, midpoint_set, border):
    r"""
    Return the polygons generated by the breaklines of the function $\lambda \mapsto round(\lambda x)$.
    Keeps only the polygons which are in the border and not too close to the accumulation lines.
    """
    if len(midpoint_set) == 0:
        return []

    all_breaklines = from_direction_midpoints_to_breaklines(
        normalized_direction_set, midpoint_set)
    # Filter the breaklines to only consider the ones that are inside the border
    all_breaklines = border.filter_all_breaklines(all_breaklines)

    merged_lines = unary_union(sum(all_breaklines, []) + border.lines_border)
    polygons = list(polygonize(merged_lines))

    smallest_beta = np.min(midpoint_set)

    # Remove the polygons that are too close from the accumulation lines
    for z in normalized_direction_set:
        if z == 0:
            continue

        y_vals = np.linspace(-100, 100, 2)
        base_line = LineString([(0, y_vals[0]), (0, y_vals[1])])
        accum_line = rotate(
            base_line, -np.degrees(np.angle(z)), origin=(0, 0))

        if np.imag(z) == 0:
            dist = smallest_beta / np.real(z)
        else:
            dist = smallest_beta * np.sin(np.angle(z)) / np.imag(z)

        accum_polygon = accum_line.buffer(dist)

        polygons = [
            poly for poly in polygons if not accum_polygon.contains(poly.centroid)
        ]

    return polygons


def get_centroids(normalized_direction_set, midpoint_set, border):
    r"""
    Returns the centroids of the polygons generated by the breaklines of the function $\lambda \mapsto round(\lambda x)$.
    The breaklines are generated from the set of directions of x all_z and the set of midpoints all_beta.

    Parameters
    ----------
    normalized_direction_set: list of directions of x
        list[complex]
    midpoint_set: list of midpoints of the form s * (k + 0.5) * 2^(e - t)
        list[float]
    border: Tiling domain
        TilingDomain

    Returns
    -------
    list of centroids of the polygons
        list[complex]
    """
    polygons = get_polygons(normalized_direction_set, midpoint_set, border)

    return [polygon.centroid.x + 1j * polygon.centroid.y for polygon in polygons]


def get_centroids_from_polygons(polygons, old_polygons=[]):
    """
    From a list of polygons, returns the centroids of the new polygons (not in old_polygons).

    Parameters
    ----------
    polygons: list of polygons to extract centroids from
        list[shapely.geometry.Polygon]
    old_polygons: list of old polygons to ignore, by default []
        list[shapely.geometry.Polygon]

    Returns
    -------
    list of centroids of the new polygons
        list[complex]
    """
    return [
        (polygon.centroid.x + 1j * polygon.centroid.y)
        for polygon in polygons
        if not any(polygon.equals(old_polygon) for old_polygon in old_polygons)
    ]


def get_centroids_accum(normalized_direction_set, t, border):
    """
    Returns the centroids on the accumulation lines associated to the directions stored in all_z.

    Parameters
    ----------
    normalized_direction_set: list of directions of x
        list[complex]
    t: number of bits for the quantization
        int
    border: Tiling domain
        TilingDomain

    Returns
    -------
    list of centroids on the accumulation lines
        list[complex]
    """
    def get_e_values(z1, z2, im_z1_z2, alpha1, t):
        r"""
        For each couple of directions (z1, z2), one associated to the accumulation line of equation Re(\lambda z) = 0
        and one to generate the breaklines of equation Re(\lambda z) = beta, where beta = s * (k + 0.5) * 2^(e - t),
        find the values of e (for each k) for which the breaklines intersect the accumulation line inside the border.

        To do so, the element of both lines can be written as \lambda = i \bar{z1} * beta / Im(z1 \bar{z2}).
        The value of e is then obtained by solving for e the equation |lambda| \geq alpha1, where alpha1 is the distance
        from the origin to the intersection of the accumulation line

        Parameters
        ----------
        z1: first direction associated to the accumulation line
            complex
        z2: second direction associated to the breaklines
            complex
        im_z1_z2: imaginary part of z1 * conjugate(z2)
            float
        alpha1: distance from the origin to the intersection of the accumulation line
            float
        t: number of bits for the quantization
            int

        Returns
        -------
        list of valid e values
            list[int]
        """
        e_values = []

        if im_z1_z2 == 0 or z1 == 0 or z2 == 0:
            return e_values

        for k in range(2**(t - 1), 2**t):
            log_value = np.log2((np.abs(im_z1_z2) * alpha1) /
                                (np.abs(z1) * (k + 0.5)))
            value = 2 - t - int(log_value)
            value = t + int(log_value)

            e_values.append(value)

        return e_values

    def unique_allclose(arr, rtol=1e-05, atol=1e-08):
        arr = np.asarray(arr)
        uniques = []

        for x in arr:
            if not any(np.isclose(x, u, rtol=rtol, atol=atol) for u in uniques):
                uniques.append(x)

        return np.array(uniques)

    passed_z = []
    all_centroids_accum = []
    for z in normalized_direction_set:
        if np.isclose(np.angle(z) % (np.pi / 2), np.angle(passed_z) % (np.pi / 2)).any():
            continue

        u1, v1 = np.real(z), np.imag(z)

        y_vals = np.linspace(-100, 100, 2)
        base_line = LineString([(0, y_vals[0]), (0, y_vals[1])])
        acc_line = rotate(
            base_line, -np.degrees(np.angle(z)), origin=(0, 0))

        breakpoint_border = border.get_breakpoint_accum(acc_line)
        if breakpoint_border is None:
            continue

        passed_z.append(z)

        alpha = np.abs(breakpoint_border)
        angle_breakpoint = np.angle(breakpoint_border) % (2 * np.pi)

        valid_breakpoint = [breakpoint_border, 2 * breakpoint_border]
        for z_other in normalized_direction_set:
            if z_other == z:
                continue
            im = np.imag(z * z_other.conjugate())
            if im == 0:
                continue

            for s in [-1, 1]:
                e_values = get_e_values(z, z_other, im, alpha, t)
                for k, e in zip(range(2**(t - 1), 2**t), e_values):
                    beta = s * (k + 0.5) * 2**(e - t)

                    re_breakpoint = (v1 / im) * beta
                    im_breakpoint = (u1 / im) * beta

                    bp = re_breakpoint + 1j * im_breakpoint
                    angle_bp = np.angle(bp) % (2 * np.pi)
                    if np.allclose(angle_bp, angle_breakpoint):
                        valid_breakpoint.append(bp)

        valid_breakpoint = sorted(unique_allclose(valid_breakpoint), key=abs)
        centroids_accum = [
            (valid_breakpoint[i] + valid_breakpoint[i + 1]) / 2
            for i in range(len(valid_breakpoint) - 1)
        ]
        all_centroids_accum.append(centroids_accum)

    return sum(all_centroids_accum, [])
