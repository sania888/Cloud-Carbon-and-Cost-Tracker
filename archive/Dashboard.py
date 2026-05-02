# dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import random
from datetime import timedelta
from streamlit_autorefresh import st_autorefresh

# ---------------- Page config ----------------
st.set_page_config(page_title="Cloud Carbon & Cost Tracker", layout="wide")
st.title("🌿 Cloud Carbon & Cost Tracker")

# ---------------- Controls ----------------
update_interval_sec = st.sidebar.slider(
    "Update interval (seconds)",
    min_value=5,
    max_value=15,
    value=7,
    step=1,
    help="Set how often the dashboard updates (in seconds)"
)
# st_autorefresh expects milliseconds
st_autorefresh(interval=update_interval_sec * 1000, key="data_refresh")

# ---------------- Services (use your streamer if available) ----------------
try:
    # If you already have data_simulator.MockDataStreamer, this will pick its services list.
    from data_simulator import MockDataStreamer
    streamer = MockDataStreamer()
    SERVICES = getattr(streamer, "services", ["EC2", "S3", "Lambda", "RDS"])
except Exception:
    streamer = None
    SERVICES = ["EC2", "S3", "Lambda", "RDS"]

# ---------------- Session state for history ----------------
if "history" not in st.session_state:
    st.session_state["history"] = pd.DataFrame(
        columns=["timestamp", "service", "cost_usd", "emission_kg_co2"]
    )

# ---------------- Helper: generate one timestep of data (fast, no sleep) ----------------
# You can swap this with a non-blocking call to your MockDataStreamer if you prefer.
def generate_one_snapshot(services=SERVICES):
    ts = pd.Timestamp.now()
    rows = []
    for s in services:
        # same ranges you used earlier
        cost = round(random.uniform(0.01, 0.05), 3)
        carbon = round(random.uniform(0.05, 0.2), 3)
        rows.append({"timestamp": ts, "service": s, "cost_usd": cost, "emission_kg_co2": carbon})
    df = pd.DataFrame(rows)
    return df

# ---------------- Append new data (one snapshot per rerun) ----------------
new_rows = generate_one_snapshot()
# ensure timestamp dtype is datetime
new_rows["timestamp"] = pd.to_datetime(new_rows["timestamp"])
st.session_state["history"] = pd.concat([st.session_state["history"], new_rows], ignore_index=True)

# Keep history trimmed to last 7 days only (avoid unbounded growth)
cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
st.session_state["history"] = st.session_state["history"][st.session_state["history"]["timestamp"] >= cutoff].copy()

# ---------------- Rolling window for charts (stock-style view) ----------------
ROLLING_WINDOW_MINUTES = 10  # how many minutes to display in charts
now = pd.Timestamp.now()
chart_window_start = now - pd.Timedelta(minutes=ROLLING_WINDOW_MINUTES)

# keep all history but display only the recent window in charts
chart_data = st.session_state["history"][
    st.session_state["history"]["timestamp"] >= chart_window_start
].copy()

# ---------------- Placeholders (single static spots in the app) ----------------
metrics_col = st.container()
charts_row = st.container()
daily_table = st.container()
weekly_table = st.container()

# ---------------- Metrics (single row, updating values in-place) ----------------
with metrics_col:
    st.subheader("💡 Live Metrics (Per Second)")
    cols = st.columns(len(SERVICES))
    for i, service in enumerate(SERVICES):
        df_s = chart_data[chart_data["service"] == service]
        if not df_s.empty:
            last = df_s.iloc[-1]
            cols[i].metric(
                label=service,
                value=f"{last['emission_kg_co2']:.3f} kgCO₂",
                delta=f"${last['cost_usd']:.3f}"
            )
        else:
            cols[i].metric(label=service, value="—", delta="—")

# ---------------- Two charts side-by-side: Carbon and Cost ----------------
with charts_row:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Carbon Usage (kgCO₂)")
        fig_c = go.Figure()
        for service in SERVICES:
            df_s = chart_data[chart_data["service"] == service]
            if not df_s.empty:
                fig_c.add_trace(
                    go.Scatter(
                        x=df_s["timestamp"],
                        y=df_s["emission_kg_co2"],
                        mode="lines+markers",
                        name=service,
                    )
                )
        fig_c.update_layout(
            height=400,
            xaxis_title="Time",
            yaxis_title="CO₂ (kg)",
            legend=dict(orientation="h"),
            transition=dict(duration=700, easing="cubic-in-out")
            )
        st.plotly_chart(fig_c, use_container_width=True, key="carbon_chart")

    with col2:
        st.subheader("📈 Cost Tracking ($)")
        fig_k = go.Figure()
        for service in SERVICES:
            df_s = chart_data[chart_data["service"] == service]
            if not df_s.empty:
                fig_k.add_trace(
                    go.Scatter(
                        x=df_s["timestamp"],
                        y=df_s["cost_usd"],
                        mode="lines+markers",
                        name=service,
                    )
                )
        fig_k.update_layout(
            height=400,
            xaxis_title="Time",
            yaxis_title="Cost ($)",
            legend=dict(orientation="h"),
            transition=dict(duration=700, easing="cubic-in-out")
            )
        st.plotly_chart(fig_k, use_container_width=True, key="cost_chart")

# ---------------- Daily summary (rolling 5 minutes) ----------------
with daily_table:
    st.subheader("📊 Daily Summary (Rolling 5 minutes)")
    window_5m = chart_data[chart_data["timestamp"] >= now - pd.Timedelta(minutes=5)]
    if not window_5m.empty:
        window_5m["date"] = window_5m["timestamp"].dt.date
        daily_summary = (
            window_5m.groupby(["date", "service"])[["cost_usd", "emission_kg_co2"]]
            .sum()
            .reset_index()
        )
        st.dataframe(daily_summary)
    else:
        st.info("No data available in the last 5 minutes yet.")

# ---------------- Weekly summary (rolling 7 days) ----------------
with weekly_table:
    st.subheader("📊 Weekly Summary (Rolling 7 days)")
    window_7d = chart_data[chart_data["timestamp"] >= now - pd.Timedelta(days=7)]
    if not window_7d.empty:
        window_7d["week"] = window_7d["timestamp"].dt.isocalendar().week
        weekly_summary = (
            window_7d.groupby(["week", "service"])[["cost_usd", "emission_kg_co2"]]
            .sum()
            .reset_index()
        )
        st.dataframe(weekly_summary)
    else:
        st.info("No data available for the last 7 days yet.")

# ---------- Small footer ----------
st.markdown(f"**Last snapshot:** {now.strftime('%Y-%m-%d %H:%M:%S')} — refresh interval: {update_interval_sec}s")
