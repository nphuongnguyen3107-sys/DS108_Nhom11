import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from src.data_loader import load_cleaned_data, get_data_summary

# ─── page config ───
st.set_page_config(
    page_title="PM2.5 TP.HCM Dashboard",
    page_icon="🌫️",
    layout="wide",
)

# ─── CSS nhẹ ───
st.markdown("""
<style>
.stMetric {background:#f0f2f6; border-radius:8px; padding:8px;}
h1 {color:#1a1a2e; font-size:1.8rem !important;}
</style>
""", unsafe_allow_html=True)

# ─── load data (cache) ───
@st.cache_data
def load_data():
    df = load_cleaned_data()
    return df

df = load_data()
# Tạo cột pm25_original chứa dữ liệu thực tế (gán các hàng nội suy bằng NaN để hiển thị khoảng trống)
df['pm25_original'] = df['pm25'].copy()
df.loc[df['pm25_interpolated'] == True, 'pm25_original'] = np.nan

summary = get_data_summary(df)

# ─── HEADER ───
st.title("🌫️ Dự Báo Nồng Độ PM2.5 — TP.HCM")
st.caption("Dữ liệu: OpenAQ (5 trạm) + Open-Meteo Archive API")

# ─── KPI ───
c1, c2, c3, c4 = st.columns(4)
c1.metric("📅 Phạm vi", summary["date_range"])
c2.metric("📊 Tổng giờ", f"{summary['total_hours']:,}")
c3.metric("💨 PM2.5 TB", f"{summary['pm25_mean']} µg/m³")
c4.metric("✅ Hợp lệ", f"{summary['pm25_valid_pct']}%")
st.divider()

# ─── SIDEBAR lọc ───
with st.sidebar:
    st.header("🎛️ Bộ lọc")
    date_range = st.date_input(
        "Khoảng thời gian",
        value=(df["time"].min().date(), df["time"].max().date()),
    )
    pm25_max = float(df["pm25"].quantile(0.99))
    pm25_range = st.slider(
        "PM2.5 (µg/m³)",
        float(df["pm25"].min()), pm25_max,
        (float(df["pm25"].min()), pm25_max),
    )
    show_raw = st.checkbox("Hiện dữ liệu thô (chưa làm sạch)", value=False)

# ─── lọc dataframe ───
pm25_col = "pm25_original" if show_raw else "pm25"
mask = (
    (df["time"].dt.date >= date_range[0])
    & (df["time"].dt.date <= date_range[1])
    & (
        ((df[pm25_col] >= pm25_range[0]) & (df[pm25_col] <= pm25_range[1]))
        | df[pm25_col].isna()
    )
)
df_f = df[mask]
st.caption(f"Đang hiển thị {len(df_f):,} / {len(df):,} dòng")

# ─── TAB: 3 trang ───
tab1, tab2, tab3 = st.tabs(["📈 Chuỗi thời gian", "📊 Phân tích thống kê", "🔬 ACF / PACF"])

# ═══════════════════════════════════════════
#  TAB 1: Time Series
# ═══════════════════════════════════════════
with tab1:
    st.subheader("Nồng độ PM2.5 theo thời gian")

    chart_type = st.radio("Loại biểu đồ", ["Line", "Scatter"], horizontal=True)
    if chart_type == "Line":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_f["time"], y=df_f[pm25_col],
            mode="lines", name="PM2.5",
            line=dict(color="#e74c3c", width=1),
        ))
    else:
        fig = px.scatter(
            df_f, x="time", y=pm25_col, opacity=0.4,
            labels={"time": "Thời gian", pm25_col: "PM2.5 (µg/m³)"},
        )

    # WHO threshold + màu nền theo mức
    fig.add_hline(y=15, line_dash="dash", line_color="black",
                  annotation_text="WHO 15 µg/m³", annotation_position="bottom right")
    fig.add_hrect(y0=0,   y1=15,  fillcolor="green",  opacity=0.05, line_width=0)
    fig.add_hrect(y0=15,  y1=35,  fillcolor="yellow", opacity=0.05, line_width=0)
    fig.add_hrect(y0=35,  y1=200, fillcolor="red",    opacity=0.05, line_width=0)
    fig.update_layout(
        xaxis_title="Thời gian", yaxis_title="PM2.5 (µg/m³)",
        height=450, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ─── Biểu đồ phụ: PM2.5 vs khí tượng ───
    st.subheader("PM2.5 và khí tượng")
    c_left, c_right = st.columns(2)
    with c_left:
        weather_col = st.selectbox(
            "Biến khí tượng:",
            ["temperature", "humidity", "wind_speed", "pressure", "precipitation"],
            format_func=lambda x: {
                "temperature": "Nhiệt độ", "humidity": "Độ ẩm",
                "wind_speed": "Tốc độ gió", "pressure": "Áp suất", "precipitation": "Lượng mưa"
            }.get(x, x),
        )
    with c_right:
        rolling_w = st.slider("Rolling window (giờ)", 1, 72, 24)

    df_plot = df_f.copy()
    df_plot["pm25_roll"] = df_plot[pm25_col].rolling(rolling_w, min_periods=1).mean()
    df_plot["weather_roll"] = df_plot[weather_col].rolling(rolling_w, min_periods=1).mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_plot["time"], y=df_plot["pm25_roll"], name="PM2.5 (rolling)",
        yaxis="y", line=dict(color="#e74c3c"),
    ))
    fig2.add_trace(go.Scatter(
        x=df_plot["time"], y=df_plot["weather_roll"], name=weather_col,
        yaxis="y2", line=dict(color="#3498db", dash="dot"),
    ))
    fig2.update_layout(
        xaxis_title="Thời gian",
        yaxis=dict(title="PM2.5 (µg/m³)", side="left"),
        yaxis2=dict(title=weather_col, overlaying="y", side="right"),
        height=400, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ─── Scatter matrix: PM2.5 vs các biến khí tượng ───
    st.subheader("Tương quan PM2.5 vs khí tượng")
    scatter_col = st.selectbox(
        "Chọn biến:", ["temperature", "humidity", "wind_speed", "pressure", "precipitation"],
        format_func=lambda x: {
            "temperature": "Nhiệt độ", "humidity": "Độ ẩm",
            "wind_speed": "Tốc độ gió", "pressure": "Áp suất", "precipitation": "Lượng mưa"
        }.get(x, x),
    )
    fig_scatter = px.scatter(
        df_f.dropna(subset=[pm25_col, scatter_col]),
        x=scatter_col, y=pm25_col,
        opacity=0.5, labels={scatter_col: scatter_col, pm25_col: "PM2.5 (µg/m³)"},
        trendline="lowess",
    )
    fig_scatter.add_hline(y=15, line_dash="dash", line_color="red",
                          annotation_text="WHO 15 µg/m³")
    st.plotly_chart(fig_scatter, use_container_width=True)

# ═══════════════════════════════════════════
#  TAB 2: Thống kê
# ═══════════════════════════════════════════
with tab2:
    st.subheader("Phân phối PM2.5")
    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(
            df_f.dropna(subset=[pm25_col]), x=pm25_col, nbins=60,
            labels={pm25_col: "PM2.5 (µg/m³)"},
        )
        fig_hist.add_vline(x=15, line_dash="dash", line_color="red", annotation_text="WHO 15")
        fig_hist.add_vline(x=df_f[pm25_col].median(), line_dash="dot", line_color="navy",
                           annotation_text=f"Median: {df_f[pm25_col].median():.1f}")
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        fig_box = px.box(
            df_f.dropna(subset=[pm25_col]),
            x="hour", y=pm25_col,
            labels={"hour": "Giờ", pm25_col: "PM2.5 (µg/m³)"},
        )
        fig_box.add_hline(y=15, line_dash="dash", line_color="red")
        st.plotly_chart(fig_box, use_container_width=True)

    # Heatmap tương quan
    st.subheader("Ma trận tương quan")
    corr_cols = [pm25_col, "temperature", "humidity", "wind_speed", "pressure", "precipitation"]
    corr = df_f[corr_cols].corr()
    fig_heat = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        labels=dict(color="Corr"), aspect="auto",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Boxplot theo tháng
    st.subheader("PM2.5 phân bố theo tháng")
    fig_month = px.box(
        df_f.dropna(subset=[pm25_col]), x="month", y=pm25_col,
        labels={"month": "Tháng", pm25_col: "PM2.5 (µg/m³)"},
        color="month",
    )
    fig_month.add_hline(y=15, line_dash="dash", line_color="red")
    st.plotly_chart(fig_month, use_container_width=True)

    # Thống kê mô tả
    st.subheader("Thống kê mô tả")
    desc = df_f[[pm25_col, "temperature", "humidity", "wind_speed", "pressure", "precipitation"]].describe()
    st.dataframe(desc.T.style.format("{:.2f}"), use_container_width=True)

# ═══════════════════════════════════════════
#  TAB 3: ACF / PACF
# ═══════════════════════════════════════════
with tab3:
    st.subheader("Tự tương quan chuỗi thời gian")
    col_a, col_b = st.columns(2)
    pm25_dropna = df_f[pm25_col].dropna()
    max_lags = min(100, len(pm25_dropna) // 4)

    with col_a:
        st.caption("ACF — Tự tương quan")
        fig_acf, ax = plt.subplots(figsize=(6, 3))
        plot_acf(pm25_dropna, lags=max_lags, ax=ax, alpha=0.05)
        ax.axvline(x=24,  color="red",    linestyle="--", alpha=0.5, label="24h")
        ax.axvline(x=168, color="green",  linestyle="--", alpha=0.5, label="168h")
        ax.legend(fontsize=8)
        st.pyplot(fig_acf)

    with col_b:
        st.caption("PACF — Tự tương quan riêng phần")
        fig_pacf, ax = plt.subplots(figsize=(6, 3))
        plot_pacf(pm25_dropna, lags=max_lags, ax=ax, alpha=0.05, method="ywm")
        ax.axvline(x=24,  color="red",   linestyle="--", alpha=0.5)
        ax.axvline(x=168, color="green", linestyle="--", alpha=0.5)
        st.pyplot(fig_pacf)

    # Seasonal decomposition
    st.subheader("Phân rã chu kỳ (Seasonal Decomposition)")
    period = st.radio("Chu kỳ:", [24, 168], horizontal=True,
                      help="24 = chu kỳ ngày, 168 = chu kỳ tuần (7 ngày × 24h)")
    series = pm25_dropna.iloc[:min(3000, len(pm25_dropna))]
    decomposition = seasonal_decompose(series, model="additive", period=period)
    fig_dec, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    decomposition.observed.plot(ax=axes[0], title="Observed (Thực tế)")
    decomposition.trend.plot(ax=axes[1], title="Trend (Xu hướng)")
    decomposition.seasonal.plot(ax=axes[2], title="Seasonal (Chu kỳ)")
    decomposition.resid.plot(ax=axes[3], title="Residual (Phần còn lại)")
    plt.tight_layout()
    st.pyplot(fig_dec)