import pandas as pd
from labpulse.io_utils import save_dataframe
import labpulse.io_utils as io

def test_save_dataframe_creates_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "PROCESSED_DIR", tmp_path)

    df = pd.DataFrame({"a": [1, 2, 3]})
    out_path = save_dataframe(df, "unit_test_file", subdir="run1")

    assert out_path.exists()
    assert out_path.suffix == ".csv"
