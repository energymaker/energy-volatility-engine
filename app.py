import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from arch import arch_model

# 1. Page Configuration & Custom Theme Setup
st.set_page_config(page_title="Energy Volatility Engine", layout="wide")

st.title("🔋 Institutional Energy Volatility & Risk Forecasting Engine")
st.caption("Live Quantitative Analysis Desk — Powered by GARCH(1,1) Statistical Modeling")

# 2. Industry Standard Peer Matrix Dropdown Dictionary
ENERGY_PEERS = {
    "NextEra Energy (NEE) - Clean Utility": "NEE",
    "Brookfield Renewable (BEP) - Pure Renewables": "BEP",
    "ExxonMobil (XOM) - Oil & Gas Major": "XOM",
    "Chevron (CVX) - Oil & Gas Major": "CVX",
    "Duke Energy (DUK) - Regulated Grid Utility": "DUK",
    "Southern Company (SO) - Traditional Utility": "SO"
}

# 3. User Interface Sidebar Controls
st.sidebar.header("🕹️ Model Parameters")
selected_display_name = st.sidebar.selectbox("Select Target Energy Asset", list(ENERGY_PEERS.keys()))
ticker = ENERGY_PEERS[selected_display_name]

lookback_period = st.sidebar.selectbox("Historical Lookback Data Range", ["1 Year", "2 Years", "5 Years"], index=1)
period_map = {"1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}

forecast_horizon = st.sidebar.slider("Volatility Forecast Horizon (Days)", min_value=5, max_value=30, value=15)

# 4. Data Extraction Engine
@st.cache_data(ttl=3600)  # Caches data for 1 hour to optimize performance, updates daily
def load_energy_data(ticker_symbol, time_frame):
    # Using group_by="ticker" to correctly isolate the Close price
    data = yf.download(ticker_symbol, period=time_frame, group_by="ticker")
    if isinstance(data.columns, pd.MultiIndex):
        close_series = data[ticker_symbol]['Close']
    else:
        close_series = data['Close']
    df = pd.DataFrame(close_series).dropna()
    # Calculate conditional daily percentage log returns
    df['Returns'] = np.log(df.iloc[:, 0] / df.iloc[:, 0].shift(1)) * 100
    return df.dropna()

try:
    df = load_energy_data(ticker, period_map[lookback_period])
    
    # 5. Execute GARCH(1,1) Quantitative Risk Model
    model = arch_model(df['Returns'], vol='Garch', p=1, q=1, dist='normal')
    model_fit = model.fit(disp='off')
    
    # Extract calculated historical risk tracking metric
    df['Historical_Conditional_Volatility'] = model_fit.conditional_volatility
    
    # Generate the forward-looking mathematical forecast
    garch_forecast = model_fit.forecast(horizon=forecast_horizon)
    forecast_variance = garch_forecast.variance.iloc[-1]
    forecast_volatility_annualized = np.sqrt(forecast_variance) * np.sqrt(252) # Annualized pricing metric

    # Create Dates for the Forecast Horizon Axis
    future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_horizon, freq='B')

    # 6. Build the Visual Dashboards
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📊 Historical Volatility Clustering Matrix")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(x=df.index, y=df['Returns'], name="Daily Asset Price Swings (%)", line=dict(color='rgba(255,255,255,0.15)', width=1)))
        fig_hist.add_trace(go.Scatter(x=df.index, y=df['Historical_Conditional_Volatility'], name="GARCH Tracked Internal Risk", line=dict(color='#00ffcc', width=2)))
        fig_hist.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.markdown("### 🔮 Forward Risk Prediction Curve")
        fig_fore = go.Figure()
        fig_fore.add_trace(go.Scatter(x=future_dates, y=forecast_volatility_annualized, name="Annualized Volatility Forecast", line=dict(color='#ff3366', width=3, dash='dash')))
        fig_fore.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_fore, use_container_width=True)

    # 7. Desk Briefing Data Output Cards
    st.markdown("### 📝 Quant Desk Core Parameters")
    alpha = model_fit.params['alpha[1]']
    beta = model_fit.params['beta[1]']
    persistence = alpha + beta

    c1, c2, c3 = st.columns(3)
    c1.metric(label="Model News Sensitivity (Alpha)", value=f"{alpha:.3f}", delta="High Reaction" if alpha > 0.1 else "Stable")
    c2.metric(label="Risk Memory Stickiness (Beta)", value=f"{beta:.3f}", delta="Persistent" if beta > 0.9 else "Short-Lived")
    c3.metric(label="Total Variance Persistence", value=f"{persistence:.3f}", delta="Mean Reverting" if persistence < 1.0 else "Explosive Risk")

    st.info(f"**How to interpret this asset's output:** This configuration presents a variance persistence of **{persistence:.3f}**. "
            f"Because this number is near 1.0, any sudden geopolitical price shock, pipeline disruption, or weather anomaly affecting **{ticker}** "
            f"will introduce highly persistent variance cluster ripples that linger inside corporate hedging calculations for extended tracking cycles.")

except Exception as e:
    st.error(f"Data Engine sync delay or ticker format adjustment needed. Technical code details: {e}")
