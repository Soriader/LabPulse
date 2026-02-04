import numpy as np
import pandas as pd

def _detect_iqr_outliers_for_group(group: pd.DataFrame, value_col: str = "value_num") -> pd.DataFrame:
    q1 = group[value_col].quantile(0.25)
    q3 = group[value_col].quantile(0.75)
    iqr = q3 - q1

    if pd.isna(iqr) or iqr == 0:
        return group.iloc[0:0].copy()

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    out = group[(group[value_col] < lower) | (group[value_col] > upper)].copy()
    out["iqr_lower"] = lower
    out["iqr_upper"] = upper
    out["iqr"] = iqr
    out["parameter"] = group.name  # ensure parameter is always a column

    return out

def detect_iqr_outliers(df: pd.DataFrame, group_col: str = "parameter", value_col: str = "value_num") -> pd.DataFrame:

    outliers = (
        df
        .groupby(group_col, group_keys=False)
        .apply(_detect_iqr_outliers_for_group)
        .reset_index(drop=True)
    )

    return outliers