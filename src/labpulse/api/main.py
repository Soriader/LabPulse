from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

app = FastAPI(title="LabPulse API")

PROCESSED_DIR = Path(os.getenv("LABPULSE_PROCESSED_DIR", "data/processed"))


# -----------------------
# Pydantic response models
# -----------------------
class RunLatestResponse(BaseModel):
    latest_run: str


class Alert(BaseModel):
    model_config = ConfigDict(extra="allow")

    sample_id: int | None = None
    product: str | None = None
    parameter: str | None = None
    unit: str | None = None
    date: str | None = None
    value_num: float | None = None


class AlertsLatestResponse(BaseModel):
    run: str
    alerts: list[Alert]


class Sample(BaseModel):

    model_config = ConfigDict(extra="allow")

    sample_id: int | None = None
    product: str | None = None
    parameter: str | None = None
    unit: str | None = None
    date: str | None = None
    value_num: float | None = None


class SamplesLatestResponse(BaseModel):
    run: str
    samples: list[Sample]


# -----------------------
# Helpers
# -----------------------
def get_latest_run_dir() -> Path:
    if not PROCESSED_DIR.exists():
        raise HTTPException(status_code=404, detail="Processed directory not found")

    runs = [d for d in PROCESSED_DIR.iterdir() if d.is_dir()]
    if not runs:
        raise HTTPException(status_code=404, detail="No processed runs found")

    # Works because run folder names are sortable (YYYY-MM-DD_HH-MM-SS)
    return sorted(runs)[-1]


def df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.to_dict(orient="records")


# -----------------------
# Endpoints
# -----------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/runs/latest", response_model=RunLatestResponse)
def runs_latest():
    latest = get_latest_run_dir()
    return {"latest_run": latest.name}


@app.get("/alerts/latest", response_model=AlertsLatestResponse)
def alerts_latest():
    latest = get_latest_run_dir()

    path = latest / "alerts_outliers_iqr.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="alerts_outliers_iqr.csv not found for latest run")

    df = pd.read_csv(path)
    return {"run": latest.name, "alerts": df_to_records(df)}


@app.get("/samples/latest", response_model=SamplesLatestResponse)
def samples_latest():
    latest = get_latest_run_dir()

    path = latest / "samples_cleaned.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="samples_cleaned.csv not found for latest run")

    df = pd.read_csv(path)
    return {"run": latest.name, "samples": df_to_records(df)}