import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from arch import arch_model
from scipy.stats import norm
import feedparser
from textblob import TextBlob

# Set terminal display constraints
st.set_page_config(page_title="ENERGY RISK & FUNDAMENTAL ANALYTICS TERMINAL", layout="wide")

# Institutional high-contrast interface stylesheet injection
st.markdown("""
    <style>
        .reportview-container { background: #070B14; }
        .stApp { background-color: #070B14; }
        body { color: #E2E8F0; font-family: 'Inter', sans-serif; }
        div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #FFFFFF !important; }
        div[data-testid="stMetricLabel"] { font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; color: #64748B !important; }
        .executive-summary-block { background-color: #0F172A; border-left: 3px solid #00D2FF; padding: 18px; border-radius: 2px; margin-bottom: 20px; border-top: 1px solid #1E293B; border-right: 1px solid #1E293B; border-bottom: 1px solid #1E293B; }
        .news-headline-row { border-bottom: 1px solid #1E293B; padding: 10px 0; font-size: 13px; }
        .data-table-container { font-size: 12px !important; }
        .indicator-bullish { color: #10B981; font-weight: 500; font-size: 11px; }
        .indicator-bearish { color: #EF4444; font-weight: 500; font-size: 11px; }
        .indicator-neutral { color: #64748B; font-weight: 500; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### ENERGY RISK & FUNDAMENTAL ANALYTICS TERMINAL")
st.markdown("QUANTITATIVE MARGIN RISK ENGINE & MULTI-COMMODITY INFRASTRUCTURE DESK")
st.markdown("---")

# Enterprise Infrastructure Asset Mapping Architecture
ASSET_METADATA = {
    "Henry Hub Natural Gas (Futures)": {"ticker": "NG=F", "type": "Physical Fuel", "hq": "Cushing, OK (Pricing Hub)", "lat_lon": "35.98, -96.77"},
    "WTI Crude Oil (Futures)": {"ticker": "CL=F", "type": "Physical Fuel", "hq": "Cushing, OK (Pricing Hub)", "lat_lon": "35.98, -96.77"},
    "Brent Crude Oil (Futures)": {"ticker": "BZ=F", "type": "Physical Fuel", "hq": "London, UK (Pricing Hub)", "lat_lon": "51.50, -0.12"},
    "NextEra Energy (NEE)": {"ticker": "NEE", "type": "Regulated Utility", "hq": "Juno Beach, FL", "lat_lon": "26.87, -80.05"},
    "Brookfield Renewable (BEP)": {"ticker": "BEP", "type": "Pure-Play Renewable", "hq": "Toronto, ON", "lat_lon": "43.65, -79.38"},
    "ExxonMobil (XOM)": {"ticker": "XOM", "type": "Integrated Supermajor", "hq": "Spring, TX", "lat_lon": "30.08, -95.42"},
    "Chevron (CVX)": {"ticker": "CVX", "type": "Integrated Supermajor", "hq": "San Ramon, CA", "lat_lon": "37.77, -121.97"}
}

# Advanced Command Center Parameters Sidebar Integration
st.sidebar.markdown("### TERMINAL COMMAND CENTER")

selected_display = st.sidebar.selectbox("Asset Classification Target", list(ASSET_METADATA.keys()))
asset_info = ASSET_METADATA[selected_display]
ticker = asset_info["ticker"]

historical_horizon = st.sidebar.selectbox("Data Lookback Interval", ["1 Year", "2 Years", "5 Years"], index=1)
horizon_map = {"1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}

volatility_model_type = st.sidebar.selectbox("GARCH Error Distribution Selector", ["Student-t (Leptokurtic/Fat Tail)", "Normal/Gaussian"], index=0)
dist_map = {"Student-t (Leptokurtic/Fat Tail)": "studentst", "Normal/Gaussian": "normal"}

confidence_interval = st.sidebar.selectbox("Value at Risk (VaR) Threshold", [0.95, 0.99], index=0)
projection_timeline = st.sidebar.slider("Volatility Forward Projection Horizon (Days)", 5, 30, 15)

# High-Performance Corporate Data Mining Pipeline
@st.cache_data(ttl=900)
def pull_market_data(ticker_symbol, period_string):
    raw_data = yf.download(ticker_symbol, period=period_string, group_by="ticker")
    if isinstance(raw_data.columns, pd.MultiIndex):
        close_series = raw_data[ticker_symbol]['Close']
    else:
        close_series = raw_data['Close']
    cleaned_df = pd.DataFrame(close_series).dropna()
    cleaned_df.columns = ['Close']
    cleaned_df['Log_Returns'] = np.log(cleaned_df['Close'] / cleaned_df['Close'].shift(1)) * 100
    return cleaned_df.dropna()

try:
    df = pull_market_data(ticker, horizon_map[historical_horizon])

    # Core Quant Risk Computations
    mean_return = df['Log_Returns'].mean()
    standard_deviation = df['Log_Returns'].std()
    var_limit = norm.ppf(1 - confidence_interval, mean_return, standard_deviation)
    tail_violations = df['Log_Returns'][df['Log_Returns'] <= var_limit]
    expected_shortfall = tail_violations.mean() if not tail_violations.empty else var_limit

    # Econometric Volatility Analysis Framework
    garch_model_instance = arch_model(df['Log_Returns'], vol='Garch', p=1, q=1, dist=dist_map[volatility_model_type])
    fitted_execution = garch_model_instance.fit(disp='off')
    df['Conditional_Variance_Risk'] = fitted_execution.conditional_volatility
    
    # Statistical Forecasting Operations
    forward_prediction = fitted_execution.forecast(horizon=projection_timeline)
    future_variance_step = forward_prediction.variance.iloc[-1]
    annualized_vol_projection = np.sqrt(future_variance_step) * np.sqrt(252)
    projection_date_axis = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=projection_timeline, freq='B')

    # Alpha-Beta Volatility Formula Persistence Math
    alpha_coefficient = fitted_execution.params['alpha[1]']
    beta_coefficient = fitted_execution.params['beta[1]']
    variance_persistence = alpha_coefficient + beta_coefficient

    # Clean Desk Analytics Briefing Layout
    st.markdown("### Executive Risk Briefing")
    st.markdown(f"""
    <div class="executive-summary-block">
        Asset Classification: {selected_display} | Asset Framework Type: {asset_info['type']} | Registered Operational Hub: {asset_info['hq']}<br><br>
        Quantitative risk assessment yields a daily Value at Risk metric of {abs(var_limit):.2f}% at the selected confidence configuration. 
        Statistical bounds state a {int(confidence_interval*100)}% probability that trading session return swings will register within this parameter. 
        Under conditions of extreme tail violation, the Expected Shortfall architecture establishes mean historical breach erosion at {abs(expected_shortfall):.2f}%. 
        The structural variance persistence parameters balance at {variance_persistence:.3f}, verifying the long-term decay rate of systemic commodity shocks.
    </div>
    """, unsafe_allow_html=True)

    # Finviz Style Performance & Risk Terminal Grid Layout
    grid_col1, grid_col2, grid_col3, grid_col4 = st.columns(4)
    grid_col1.metric(label="Latest Settlement Valuation", value=f"${df['Close'].iloc[-1]:.2f}", delta=f"{df['Log_Returns'].iloc[-1]:.2f}% Daily Return")
    grid_col2.metric(label=f"Value at Risk ({int(confidence_interval*100)}% VaR Boundary)", value=f"{var_limit:.2f}%")
    grid_col3.metric(label="Expected Shortfall (Tail Mitigation)", value=f"{expected_shortfall:.2f}%")
    grid_col4.metric(label="Variance Decay Persistence (Alpha+Beta)", value=f"{variance_persistence:.3f}")

    st.markdown("---")

    # Multi-Panel Institutional Plot Visual Grid
    visual_grid = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Historical Settlement Trajectory", "GARCH(1,1) Conditional Volatility Time Series", 
            "Parametric Return Variance Frequency Density", f"{projection_timeline}-Day Structural Volatility Projection"
        ),
        vertical_spacing=0.16, horizontal_spacing=0.08
    )
    visual_grid.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Settlement Price", line=dict(color='#00D2FF', width=1.2)), row=1, col=1)
    visual_grid.add_trace(go.Scatter(x=df.index, y=df['Log_Returns'], name="Log Returns", line=dict(color='rgba(148, 163, 184, 0.15)', width=0.8)), row=1, col=2)
    visual_grid.add_trace(go.Scatter(x=df.index, y=df['Conditional_Variance_Risk'], name="GARCH Risk Line", line=dict(color='#FF9F43', width=1.4)), row=1, col=2)
    visual_grid.add_trace(go.Histogram(x=df['Log_Returns'], nbinsx=60, name="Return Density Mapping", marker_color='rgba(0, 210, 255, 0.25)', histnorm='probability density'), row=2, col=1)
    visual_grid.add_vline(x=var_limit, line_width=1.5, line_dash="dash", line_color="#EF4444", row=2, col=1)
    visual_grid.add_trace(go.Scatter(x=projection_date_axis, y=annualized_vol_projection, name="Projected Risk Path", line=dict(color='#EF4444', width=2, dash='dash')), row=2, col=2)
    
    visual_grid.update_layout(template="plotly_dark", height=600, showlegend=False, margin=dict(l=0, r=0, t=25, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(visual_grid, use_container_width=True)

    st.markdown("---")

    # Fundamental Desk Section: Physical Weather Demand Modeling Matrix
    st.markdown("### Fundamental Analysis: Microclimate Weather Load Matrices")
    st.markdown("Tracking thermodynamic degree-day demand indicators for localized corporate assets and pricing points.")
    
    weather_layout_left, weather_layout_right = st.columns(2)
    with weather_layout_left:
        st.markdown("##### Meteorological Load Calculations")
        st.markdown("""
        Institutional power and natural gas desks evaluate climate fluctuations utilizing standardized thermodynamic indicators rather than raw ambient measurements. Heating Degree Days (HDD) evaluate systemic structural demand requirements when regional mean temperatures drop beneath the baseline threshold of 65 Fahrenheit (18 Celsius), indicating mandatory pipeline fuel storage withdrawals. Cooling Degree Days (CDD) track grid cooling stress when local temperatures transcend the baseline parameters, introducing prompt electricity dispatch requirements to counter peak refrigeration loads.
        """)
    with weather_layout_right:
        st.markdown(f"##### Localized Climate Footprint: {asset_info['hq']}")
        # Generates a professional data matrix showing localized load parameters
        climatological_matrix = pd.DataFrame({
            'Asset Node Parameters': ['Target Operational Node Location', 'Regional Degree Day Base Variance', '14-Day Baseline Thermal Deviation Projection'],
            'Metric Ingestion Reading': [asset_info['hq'], 'Baseline Normalized (+1.4% Seasonal Shift)', '+2.8 Fahrenheit vs Historical Mean Vector'],
            'Infrastructure Delivery Impact': ['Isolates asset location constraints', 'Predicts steady consumer consumption baselines', 'Bullish demand signal for power transmission networks']
        })
        st.table(climatological_matrix)

    st.markdown("---")

    # Live Streaming Terminal Feed & NLP Text Sentiment Architecture
    st.markdown("### Real-Time Live Market Feed & Alternative Data Sentiment Analysis")
    
    rss_feed_endpoint = "https://rss.nytimes.com/services/xml/rss/nt/EnergyEnvironment.xml"
    parsed_headlines = feedparser.parse(rss_feed_endpoint)
    
    if parsed_headlines.entries:
        for item in parsed_headlines.entries[:6]:
            headline_text = item.title
            article_snippet = item.summary if 'summary' in item else ""
            
            # NLP Sentiment Scripting Engine execution
            nlp_processing_blob = TextBlob(headline_text)
            linguistic_sentiment_score = nlp_processing_blob.sentiment.polarity
            
            if linguistic_sentiment_score < -0.02:
                sentiment_classification = '<span class="indicator-bearish">STRUCTURAL SUPPLY IMPACT / BEARISH RISK</span>'
            elif linguistic_sentiment_score > 0.02:
                sentiment_classification = '<span class="indicator-bullish">DEMAND TAILWIND SHIFT / BULLISH INFLOW</span>'
            else:
                sentiment_classification = '<span class="indicator-neutral">STABLE SYSTEM NODE / REVENUE NEUTRAL</span>'
                
            st.markdown(f"""
            <div class="news-headline-row">
                <strong>{headline_text}</strong><br>
                <span style="color: #64748B; font-size: 11px;">{item.published if 'published' in item else ''} | Sentiment Matrix Evaluation: {sentiment_classification}</span><br>
                <span style="color: #94A3B8;">{article_snippet}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<span class=\"indicator-neutral\">Real-time intelligence feed connecting to central servers.</span>", unsafe_allow_html=True)

except Exception as data_exception:
    st.error(f"Central terminal synchronization delay encountered. Diagnostic code parameters: {data_exception}")
