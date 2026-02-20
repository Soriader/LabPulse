import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="LabPulse Dashboard", layout="wide")
st.title("LabPulse – Dashboard QC & Alerts")

# --- helpers ---
def api_get(path: str, timeout: int = 10):
    url = f"{API_BASE}{path}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()

def fetch_latest():
    # healthcheck
    health = api_get("/health")
    if health.get("status") != "ok":
        raise RuntimeError("API healthcheck failed")

    run_info = api_get("/runs/latest")
    latest_run = run_info.get("latest_run")

    alerts_payload = api_get("/alerts/latest")
    samples_payload = api_get("/samples/latest")

    alerts = alerts_payload.get("alerts", [])
    samples = samples_payload.get("samples", [])

    return latest_run, pd.DataFrame(samples), pd.DataFrame(alerts)

# --- UI ---
with st.sidebar:
    st.header("Connected to LabPulse Dashboard")
    st.caption("API must run on 127.0.0.1:8000")
    refresh = st.button("Refresh data")

try:
    latest_run, samples_df, alerts_df = fetch_latest()
except Exception as e:
    st.error("I can't get data from the API. Make sure FastAPI is running.")
    st.code(str(e))
    st.stop()

st.success(f"New run: {latest_run}")

col1, col2, col3 = st.columns(3)
col1.metric("Rows (samples)", int(len(samples_df)))
col2.metric("Alerts", int(len(alerts_df)))
col3.metric("Products (unique)", int(samples_df["product"].nunique()) if "product" in samples_df.columns and len(samples_df) else 0)

# --- Filters ---
st.subheader("Filters")

fcol1, fcol2 = st.columns(2)

products = sorted(samples_df["product"].dropna().unique()) if "product" in samples_df.columns and len(samples_df) else []
parameters = sorted(samples_df["parameter"].dropna().unique()) if "parameter" in samples_df.columns and len(samples_df) else []

with fcol1:
    product_sel = st.multiselect("Product", products, default=products[:1] if products else [])
with fcol2:
    parameter_sel = st.multiselect("Parameter", parameters, default=parameters[:1] if parameters else [])

filtered_samples = samples_df.copy()
if product_sel and "product" in filtered_samples.columns:
    filtered_samples = filtered_samples[filtered_samples["product"].isin(product_sel)]
if parameter_sel and "parameter" in filtered_samples.columns:
    filtered_samples = filtered_samples[filtered_samples["parameter"].isin(parameter_sel)]

filtered_alerts = alerts_df.copy()
if len(filtered_alerts):
    if product_sel and "product" in filtered_alerts.columns:
        filtered_alerts = filtered_alerts[filtered_alerts["product"].isin(product_sel)]
    if parameter_sel and "parameter" in filtered_alerts.columns:
        filtered_alerts = filtered_alerts[filtered_alerts["parameter"].isin(parameter_sel)]

# --- Tables ---
t1, t2 = st.columns(2)

with t1:
    st.subheader("Samples (latest)")
    st.dataframe(filtered_samples, use_container_width=True)

with t2:
    st.subheader("Alerts (latest)")
    st.dataframe(filtered_alerts, use_container_width=True)

st.subheader("Distribution (value_num)")

if "value_num" in filtered_samples.columns and len(filtered_samples):
    series = pd.to_numeric(filtered_samples["value_num"], errors="coerce").dropna()
    if len(series):
        fig, ax = plt.subplots()
        ax.hist(series, bins=20)
        ax.set_xlabel("value_num")
        ax.set_ylabel("count")
        st.pyplot(fig)
    else:
        st.info("No numeric value_num available after filtering.")
else:
    st.info("Column value_num not available in samples or no data after filtering.")