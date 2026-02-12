import pandas as pd
from labpulse.cleaning import filter_numeric_rows

def test_filter_numeric_rows_removes_non_numeric():
    df = pd.DataFrame({"value_num": [1.0, 2.5, None, "abc"]})
    cleaned = filter_numeric_rows(df)

    assert cleaned["value_num"].isna().sum() == 0
