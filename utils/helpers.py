import pandas as pd
import numpy as np

def load_csv(path):
    """Safe load for a CSV file."""
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return pd.DataFrame()

def normalize(series):
    """Normalize a numeric series to 0–1 range."""
    if series.empty:
        return series
    return (series - series.min()) / (series.max() - series.min())

def weighted_score(*args, weights=None):
    """Compute weighted average for scores."""
    if weights is None:
        weights = [1] * len(args)
    total = np.dot(np.array(args), np.array(weights))
    return total / sum(weights)
