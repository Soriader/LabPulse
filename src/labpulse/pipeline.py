from labpulse.cleaning import prepare_base_df, filter_numeric_rows
from labpulse.qc_rules import apply_unit_rules
from labpulse.alerts import build_outlier_alerts
from labpulse.io_utils import save_dataframe
from datetime import datetime

def run_pipeline(input_path: str):
    df = prepare_base_df(input_path)
    df = filter_numeric_rows(df)
    df = apply_unit_rules(df)
    alerts = build_outlier_alerts(df)

    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_dataframe(df, "samples_cleaned", subdir=run_id)
    save_dataframe(alerts, "alerts_outliers_iqr", subdir=run_id)

    return df, alerts
