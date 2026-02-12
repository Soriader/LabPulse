import pandas as pd

from labpulse.cleaning import prepare_base_df, filter_numeric_rows
from labpulse.qc_rules import apply_unit_rules


def test_apply_unit_rules_keeps_numeric_values_and_rows(tmp_path):

    df = pd.DataFrame({
        "sample_id": [1, 2, 3],
        "product": ["JetA1", "HSFO", "JetA1"],
        "parameter": ["Ash", "Ash", "Viscosity"],
        "value": [0.010, 0.020, 137.2],
        "unit": ["% m/m", "% m/m", "cSt"],
        "date": ["2026-01-02", "2026-01-07", "2026-01-26"],
    })

    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False)

    df_base = prepare_base_df(csv_path)
    df_num = filter_numeric_rows(df_base)
    out = apply_unit_rules(df_num)

    assert len(out) == len(df_num)
    assert "value_num" in out.columns
    assert out["value_num"].isna().sum() == 0

