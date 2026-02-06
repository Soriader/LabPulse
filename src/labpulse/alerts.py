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
    out["parameter"] = group.name

    return out

def detect_iqr_outliers(df: pd.DataFrame, group_col: str = "parameter", value_col: str = "value_num") -> pd.DataFrame:

    outliers = (
        df
        .groupby(group_col, group_keys=False)
        .apply(_detect_iqr_outliers_for_group)
        .reset_index(drop=True)
    )

    return outliers

def add_severity(outliers: pd.DataFrame, value_col: str = "value_num") -> pd.DataFrame:

    if outliers is None or outliers.empty:
        return outliers.copy() if outliers is not None else pd.DataFrame()

    required = {"iqr_lower", "iqr_upper", "iqr", value_col}
    missing = required - set(outliers.columns)
    if missing:
        raise ValueError(f"add_severity: missing required columns: {sorted(missing)}")

    df = outliers.copy()

    df["severity"] = np.where(
        df[value_col] > df["iqr_upper"],
        (df[value_col] - df["iqr_upper"]) / df["iqr"],
        (df["iqr_lower"] - df[value_col]) / df["iqr"],
    )
    df.loc[df["iqr"] == 0, "severity"] = np.nan

    df["severity_level"] = pd.cut(
        df["severity"],
        bins=[-np.inf, 1, 3, np.inf],
        labels=["low", "medium", "high"],
    )

    return df

def build_outlier_alerts(df: pd.DataFrame) -> pd.DataFrame:

    required = {
        "sample_id", "product", "parameter", "unit", "date_dt",
        "value_num", "unit_ok"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"build_outlier_alerts: missing required columns: {sorted(missing)}")

    df_analysis = df[(df["unit_ok"] == True) & (df["value_num"].notna())].copy()

    outliers = detect_iqr_outliers(df_analysis, group_col="parameter", value_col="value_num")

    alert_cols = [
        "sample_id", "product", "parameter", "value_num", "unit", "date_dt",
        "iqr_lower", "iqr_upper", "severity", "severity_level"
    ]

    if outliers.empty:
        return pd.DataFrame(columns=alert_cols)

    outliers = add_severity(outliers, value_col="value_num")

    alerts = (
        outliers[alert_cols]
        .sort_values(["severity", "date_dt"], ascending=[False, False])
        .reset_index(drop=True)
    )

    return alerts
