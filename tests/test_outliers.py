import pandas as pd

from labpulse.cleaning import prepare_base_df, filter_numeric_rows
from labpulse.qc_rules import apply_unit_rules
from labpulse.alerts import build_outlier_alerts


def test_build_outlier_alerts_flags_extreme_value(tmp_path):

    df = pd.DataFrame({
        "sample_id": [1, 2, 3, 4, 5],
        "product": ["JetA1"] * 5,
        "parameter": ["Ash"] * 5,
        "value": [0.010, 0.011, 0.012, 0.013, 1.000],
        "unit": ["% m/m"] * 5,
        "date": ["2026-01-02"] * 5,
    })

    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False)

    df_base = prepare_base_df(csv_path)
    df_num = filter_numeric_rows(df_base)
    df_qc = apply_unit_rules(df_num)

    alerts = build_outlier_alerts(df_qc)

    assert len(alerts) >= 1

