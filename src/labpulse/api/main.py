from fastapi import FastAPI
from pathlib import Path
import pandas as pd

app = FastAPI(title="LabPulse API")
PROCESSED_DIR = Path("data/processed")

def get_latest_run_dir() -> Path | None:
    if not PROCESSED_DIR.exists():
        return None
    runs = [d for d in PROCESSED_DIR.iterdir() if d.is_dir()]
    if not runs:
        return None
    return sorted(runs)[-1]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/runs/latest")
def runs_latest():
    latest = get_latest_run_dir()
    return {"latest_run": latest.name if latest else None}

@app.get("/alerts/latest")
def alerts_latest():
    latest = get_latest_run_dir()
    if latest is None:
        return {"run": None, "alerts": []}

    path = latest / "alerts_outliers_iqr.csv"
    if not path.exists():
        return {"run": latest.name, "alerts": []}

    df = pd.read_csv(path)
    return {"run": latest.name, "alerts": df.to_dict(orient="records")}

@app.get("/samples/latest")
def samples_latest():
    latest = get_latest_run_dir()
    if latest is None:
        return {"run": None, "samples": []}

    path = latest / "samples_cleaned.csv"
    if not path.exists():
        return {"run": latest.name, "samples": []}

    df = pd.read_csv(path)
    return {"run": latest.name, "samples": df.to_dict(orient="records")}