import re
import os
import numpy as np
import pandas as pd


def gather_results(root_dir, file_name):
    """
    Gathers the results from the file_name files in the root_dir tree.

    - If file_name ends with .npy, returns (ndarray, param_keys, param_values)
    - If file_name ends with .csv, returns (DataFrame, param_keys, param_values),
      where each row of the DataFrame is annotated with the parameter values.
    """
    pattern = re.compile(r"(\w+)=([-\w.]+)")
    param_paths = []

    # Collect files and parameters
    for dirpath, _, filenames in os.walk(root_dir):
        if file_name in filenames:
            rel_path = os.path.relpath(dirpath, root_dir)
            parts = rel_path.split(os.sep)
            param_dict = {}
            for part in parts:
                match = pattern.match(part)
                if match:
                    key, val = match.groups()
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    param_dict[key] = val
            param_paths.append((param_dict, os.path.join(dirpath, file_name)))

    if not param_paths:
        raise RuntimeError("No files matching this name.")

    # Detect file type
    sample_path = param_paths[0][1]
    if sample_path.endswith(".npy"):
        # Build multidimensional numpy array
        param_keys = sorted({k for d, _ in param_paths for k in d})
        param_values = {k: sorted(set(d.get(k)
                                  for d, _ in param_paths)) for k in param_keys}
        shape = tuple(len(param_values[k]) for k in param_keys)
        val_to_idx = {k: {v: i for i, v in enumerate(
            param_values[k])} for k in param_keys}
        result_array = np.empty(shape, dtype=object)

        for param_dict, path in param_paths:
            idx = tuple(val_to_idx[k][param_dict.get(k)] for k in param_keys)
            result_array[idx] = np.load(path)

        return result_array, param_keys, param_values

    elif sample_path.endswith(".csv"):
        # Build pandas DataFrame with parameter columns
        dfs = []
        param_keys = sorted({k for d, _ in param_paths for k in d})
        param_values = {k: sorted(set(d.get(k)
                                  for d, _ in param_paths)) for k in param_keys}

        for param_dict, path in param_paths:
            df = pd.read_csv(path)
            # Add parameter columns
            for k, v in param_dict.items():
                df[k] = v
            dfs.append(df)

        full_df = pd.concat(dfs, ignore_index=True)
        return full_df, param_keys, param_values

    else:
        raise ValueError(f"Unsupported file format: {sample_path}")
