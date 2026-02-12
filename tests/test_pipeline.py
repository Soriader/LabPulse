from labpulse.pipeline import run_pipeline


def test_pipeline_runs():

    input_path = "data/raw/samples.csv"

    df, alerts = run_pipeline(input_path)

    assert len(df) > 0
    assert alerts is not None

