from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def save_dataframe(df: pd.DataFrame, filename: str, subdir: str | None = None) -> Path:
    out_dir = PROCESSED_DIR if subdir is None else (PROCESSED_DIR / subdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{filename}.csv"
    df.to_csv(path, index=False)
    return path

