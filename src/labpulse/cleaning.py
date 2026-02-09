import pandas as pd
import numpy as np

def prepare_base_df(path: str) -> pd.DataFrame:
    """
    Load raw CSV data and perform basic cleaning:
    - replace invalid measurement tokens with NaN
    - normalize decimal separator
    - convert values to numeric
    - parse date column to datetime
    """

    df = pd.read_csv(path)

    bad_tokens = ["error", "bad_reading", "N/A"]

    #replace invalid tokens
    df["value_clean"] = df["value"].replace(bad_tokens, np.nan)

    #normalize decimal separator
    df["value_clean"] = (
        df["value_clean"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    #convert to numeric
    df["value_num"] = pd.to_numeric(df["value_clean"], errors="coerce")

    #parse date
    df["date_dt"] = pd.to_datetime(
        df["date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    return df


def filter_numeric_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter rows with valid numeric measurements.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'value_num' column.

    Returns
    -------
    pd.DataFrame
        DataFrame with rows where value_num is not NaN.
    """

    filtered_df = df[df['value_num'].notna()].copy()
    filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df



# load_raw(path: str) -> pd.DataFrame
#
# clean_values(df: pd.DataFrame) -> pd.DataFrame
#
# parse_dates(df: pd.DataFrame) -> pd.DataFrame
#
# prepare_base_df(path: str) -> pd.DataFrame