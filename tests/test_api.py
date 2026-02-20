import pandas as pd
from fastapi.testclient import TestClient

import labpulse.api.main as api


def test_runs_latest_and_alerts_latest(tmp_path, monkeypatch):
    # Arrange: set processed dir to temp
    monkeypatch.setattr(api, "PROCESSED_DIR", tmp_path)

    run_dir = tmp_path / "2026-02-20_18-00-00"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Create alerts file
    alerts = pd.DataFrame([
        {"sample_id": 1, "product": "JetA1", "parameter": "Ash", "value_num": 0.01, "severity": "low"},
        {"sample_id": 2, "product": "JetA1", "parameter": "Ash", "value_num": 1.00, "severity": "high"},
    ])
    alerts.to_csv(run_dir / "alerts_outliers_iqr.csv", index=False)

    # Create samples file
    samples = pd.DataFrame([
        {"sample_id": 1, "product": "JetA1", "parameter": "Ash", "value_num": 0.01, "unit": "% m/m", "date": "2026-01-02"},
        {"sample_id": 2, "product": "JetA1", "parameter": "Ash", "value_num": 1.00, "unit": "% m/m", "date": "2026-01-02"},
    ])
    samples.to_csv(run_dir / "samples_cleaned.csv", index=False)

    client = TestClient(api.app)

    # Act + Assert
    r = client.get("/runs/latest")
    assert r.status_code == 200
    assert r.json()["latest_run"] == run_dir.name

    r = client.get("/alerts/latest")
    assert r.status_code == 200
    payload = r.json()
    assert payload["run"] == run_dir.name
    assert len(payload["alerts"]) == 2

    r = client.get("/samples/latest")
    assert r.status_code == 200
    payload = r.json()
    assert payload["run"] == run_dir.name
    assert len(payload["samples"]) == 2


def test_no_runs_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "PROCESSED_DIR", tmp_path)
    client = TestClient(api.app)

    r = client.get("/runs/latest")
    assert r.status_code == 404