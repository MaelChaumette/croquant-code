import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "0"):
        return False


def get_args():
    """
    Parses command line arguments for complex-valued rank-one matrix quantization experiments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--function",
        type=str,
        help="Function to run (only for plots)",
    )
    parser.add_argument(
        "--m",
        type=int,
        help="Size of the right vector",
        default=2
    )
    parser.add_argument(
        "--n",
        type=int,
        help="Size of the left vector or the butterfly matrices (only power of 2)",
        default=2
    )
    parser.add_argument(
        "--bit",
        type=int,
        help="Number of bits for quantization",
        default=4
    )
    parser.add_argument(
        "--delta",
        type=int,
        help="Value of the parameter delta",
        default=2
    )
    parser.add_argument(
        "--distrib",
        type=str,
        help="Distribution type",
        choices=["uniform", "normal", "roots_of_unity", "finite_alphabet"],
        default="uniform"
    )
    parser.add_argument(
        "--max_points",
        type=int,
        help="Maximum number of points",
        default=100
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--save_dir",
        type=str,
        help="Directory to save results",
        default="results"
    )
    parser.add_argument(
        "--save_img_dir",
        type=str,
        help="Directory to save images",
        default="images"
    )
    parser.add_argument(
        "--draw_zoom",
        type=str2bool,
        default=True,
    )

    return parser.parse_args()
