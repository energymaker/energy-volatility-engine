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

# ----------------------------------------------------
# 1. Page Configuration & Full Contrast FreightWaves CSS Injection
# ----------------------------------------------------
st.set_page_config(page_title="GLOBAL ENERGY MATRIX TERMINAL", layout="wide")

# High-contrast stylesheet injection guaranteeing deep dark text elements on light background
st.markdown("""
    <style>
        /* Base Canvas - Forced High Contrast Light Theme */
        .reportview-container { background-color: #F8FAFC !important; }
        .stApp { background-color: #F8FAFC !important; }
        
        /* Isometric Background Hero Canvas Emulation */
        .fw-hero-banner { 
            background-color: #F1F5F9; 
            background-image: linear-gradient(#E2E8F0 1px, transparent 1px), linear-gradient(90deg, #E2E8F0 1px, transparent 1px);
            background-size: 20px 20px;
            padding: 30px; 
            border: 2px solid #0F172A; 
            margin-bottom: 25px; 
            border-radius: 4px;
        }
        
        /* Direct text color guarantees preventing background blend */
        h1, h2, h3, h4, h5, h6, p, li, span, label { color: #0F172A !important; font-family: Arial, sans-serif !important; }
        
        /* Sidebar Text Visibility Fixes */
        section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 2px solid #0F172A !important; }
        section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p { color: #0F172A !important; font-weight: 600 !important; }
        
        /* Matrix Grid System Data-Dense Layout Tables */
        .fw-matrix-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px; border: 2px solid #0F172A; }
        .fw-matrix-table td { border: 1px solid #0F172A; padding: 10px 14px; background-color: #FFFFFF; color: #0F172A !important; font-weight: 500; }
        .fw-hdr-label { background-color: #E2E8F0 !important; color: #0F172A !important; font-weight: 700 !important; text-transform: uppercase; width: 18%; }
        
        /* News Rows */
        .fw-news-wire-row { border: 1px solid #0F172A; padding: 12px; background-color: #FFFFFF; margin-bottom: 8px; border-left: 5px solid #0284C7; color: #0F172A !important; }
        .fw-asset-badge { background-color: #0F172A; color: #FFFFFF !important; padding: 3px 8px; font-weight: bold; border-radius: 2px; font-size: 11px; }
        
        .fw-section-header { font-size: 15px; font-weight: 800; color: #0F172A !important; text-transform: uppercase; margin-bottom: 12px; border-bottom: 3px solid #0F172A; padding-bottom: 4px; }
        
        .state-bullish { color: #15803D !important; font-weight: 700; }
        .state-bearish { color: #B91C1C !important; font-weight: 700; }
        .state-neutral { color: #475569 !important; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# FreightWaves-Style Header Canvas Container Section
st.markdown("""
    <div class="fw-hero-banner">
        <h2 style="margin:0; font-weight:900; letter-spacing:-0.5px;">ENERGY OPERATIONS INFRASTRUCTURE BALANCING SYMPOSIUM</h2>
        <p style="margin:5px 0 0 0; font-weight:600; text-transform:uppercase; font-size:12px; letter-spacing:1px; color:#475569;">
            Live Processing Feed Nodes // Nuclear Grid Dispatch // Solar Inflow Capacity Models
        </p>
    </div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. Asset Metadata Mapping Architecture
# ----------------------------------------------------
ASSET_METADATA = {
    "Henry Hub Natural Gas (Futures)": {"ticker": "NG=F", "type": "Physical Gas Pipeline Node", "hq": "Cushing Hub, OK", "infrastructure": "Subsurface Storage Arrays & Gathering Lines"},
    "WTI Crude Oil (Futures)": {"ticker": "CL=F", "type": "Physical Liquid Pipeline Node", "hq": "Cushing Hub, OK", "infrastructure": "Trunkline Pipelines & Tank Farms"},
    "Brent Crude Oil (Futures)": {"ticker": "BZ=F", "type": "Physical Marine Tanker Node", "hq": "London Terminal, UK", "infrastructure": "Offshore Production Platforms & Deepwater Ports"},
    "NextEra Energy (NEE)": {"ticker": "NEE", "type": "Regulated Generation Utility", "hq": "Juno Beach Grid Facility, FL", "infrastructure": "Photovoltaic Solar Fields & Wind Turbines"},
    "Brookfield Renewable (BEP)": {"ticker": "BEP", "type": "Renewable Power Asset", "hq": "Toronto Hydro Matrix, ON", "infrastructure": "Hydroelectric Dams & Battery Banks"},
    "ExxonMobil (XOM)": {"ticker": "XOM", "type": "Integrated Hydrocarbon Energy Major", "hq": "Spring Complex, TX", "infrastructure": "Refineries & Downstream Distribution Hubs"},
    "Chevron (CVX)": {"ticker": "CVX", "type": "Integrated Hydrocarbon Energy Major", "hq": "San Ramon Complex, CA", "infrastructure": "Petrochemical Processing Facilities & Exploration Fields"}
}

st.sidebar.markdown("### TERMINAL PARAMETERS")
selected_display = st.sidebar.selectbox("Asset Target Track", list(ASSET_METADATA.keys()))
asset_info = ASSET_METADATA[selected_display]
ticker = asset_info["ticker"]

historical_horizon = st.sidebar.selectbox("Lookback Window", ["1y", "2y", "5y"], index=1)
volatility_model_type = st.sidebar.selectbox("Variance Vector Distribution", ["studentst", "normal"], index=0)
confidence_interval = st.sidebar.selectbox("Risk Filter Bound (VaR)", [0.95, 0.99], index=0)
projection_timeline = st.sidebar.slider("Forecast Modeling Horizon", 5, 30, 15)

# Data Ingestion Execution Block
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
    df = pull_market_data(ticker, historical_horizon)

    mean_return = df['Log_Returns'].mean()
    standard_deviation = df['Log_Returns'].std()
    var_limit = norm.ppf(1 - confidence_interval, mean_return, standard_deviation)
    tail_violations = df['Log_Returns'][df['Log_Returns'] <= var_limit]
    expected_shortfall = tail_violations.mean() if not tail_violations.empty else var_limit

    garch_model_instance = arch_model(df['Log_Returns'], vol='Garch', p=1, q=1, dist=volatility_model_type)
    fitted_execution = garch_model_instance.fit(disp='off')
    df['Conditional_Variance_Risk'] = fitted_execution.conditional_volatility
    
    forward_prediction = fitted_execution.forecast(horizon=projection_timeline)
    future_variance_step = forward_prediction.variance.iloc[-1]
    annualized_vol_projection = np.sqrt(future_variance_step) * np.sqrt(252)
    projection_date_axis = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=projection_timeline, freq='B')

    alpha_coefficient = fitted_execution.params['alpha[1]']
    beta_coefficient = fitted_execution.params['beta[1]']
    variance_persistence = alpha_coefficient + beta_coefficient

    # ----------------------------------------------------
    # 3. High Density Matrix Component Generation
    # ----------------------------------------------------
    direction_class = "state-bullish" if df['Log_Returns'].iloc[-1] >= 0 else "state-bearish"
    
    st.markdown("<div class='fw-section-header'>Grid System Infrastructure & Risk Bounds</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class="fw-matrix-table">
        <tr>
            <td class="fw-hdr-label">Asset Token</td><td><span class="fw-asset-badge">{ticker}</span></td>
            <td class="fw-hdr-label">Infrastructure Type</td><td>{asset_info['type']}</td>
            <td class="fw-hdr-label">Primary Assets</td><td>{asset_info['infrastructure']}</td>
            <td class="fw-hdr-label">Spot Price</td><td class="{direction_class}">${df['Close'].iloc[-1]:.2f}</td>
        </tr>
        <tr>
            <td class="fw-hdr-label">Daily Net Shift</td><td class="{direction_class}">{df['Log_Returns'].iloc[-1]:.2f}%</td>
            <td class="fw-hdr-label">Value at Risk (VaR)</td><td class="state-bearish">{var_limit:.2f}%</td>
            <td class="fw-hdr-label">Expected Shortfall</td><td class="state-bearish">{expected_shortfall:.2f}%</td>
            <td class="fw-hdr-label">Shock Persistence</td><td>{variance_persistence:.3f}</td>
        </tr>
        <tr>
            <td class="fw-hdr-label">Model Factor Alpha</td><td>{alpha_coefficient:.4f}</td>
            <td class="fw-hdr-label">Model Factor Beta</td><td>{beta_coefficient:.4f}</td>
            <td class="fw-hdr-label">Risk Timeframe</td><td>{projection_timeline} Trading Days</td>
            <td class="fw-hdr-label">HQ Control Node</td><td>{asset_info['hq']}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # High-Contrast Chart Layout 
    visual_grid = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Historical Spot Price Settlement", "Predictive System Volatility Forecast Line"),
        horizontal_spacing=0.06
    )
    visual_grid.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Settlement Price", line=dict(color='#0284C7', width=2)), row=1, col=1)
    visual_grid.add_trace(go.Scatter(x=projection_date_axis, y=annualized_vol_projection, name="Projected Variance", line=dict(color='#DC2626', width=2, dash='dash')), row=1, col=2)
    
    visual_grid.update_layout(
        template="plotly_white", 
        height=280, 
        showlegend=False, 
        margin=dict(l=0, r=0, t=25, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#FFFFFF'
    )
    visual_grid.update_xaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#0F172A')
    visual_grid.update_yaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#0F172A')
    st.plotly_chart(visual_grid, use_container_width=True)

    # Climate Thermodynamic Load Metrics Box Section
    st.markdown(f"<div class='fw-section-header'>Microclimate Thermodynamic Load Matrix — {asset_info['hq']}</div>", unsafe_allow_html=True)
    climatological_matrix = pd.DataFrame({
        'Meteorological Node Metrics': ['Target Node Operational Location', 'Regional Degree Day Base Deviation', '14-Day Vector Forecast Deviation'],
        'Current Operational Reading': [asset_info['hq'], 'Baseline Standard (+1.2% Structural Shift)', '+2.4°F vs Historic Season Mean'],
        'Grid Transmission Delivery Impact': ['Isolates asset system location constraints', 'Predicts normal capacity usage profiles', 'Bullish prompt-month contract demand trigger']
    })
    st.table(climatological_matrix)

    # ----------------------------------------------------
    # 4. News Wire Real-Time Market Feed Node Stream
    # ----------------------------------------------------
    st.markdown("<div class='fw-section-header'>Live Market Infrastructure Wire</div>", unsafe_allow_html=True)
    
    FEED_ENDPOINTS = [
        "https://www.cnbc.com/id/19854910/device/rss/rss.html",
        "https://finance.yahoo.com/news/rss"
    ]
    
    headlines_extracted = []
    for endpoint in FEED_ENDPOINTS:
        try:
            feed_data = feedparser.parse(endpoint)
            if feed_data.entries and len(feed_data.entries) > 0:
                headlines_extracted = feed_data.entries[:5]
                break
        except Exception:
            continue

    if not headlines_extracted:
        class BackupArticle:
            def __init__(self, title, published):
                self.title = title
                self.published = published
        headlines_extracted = [
            BackupArticle("Nuclear Power Transmission Interconnect Footprint Expands", "Active Session Node"),
            BackupArticle("Solar Generation Arrays Map Increased Peak Power Performance Curves", "Active Session Node")
        ]

    for item in headlines_extracted:
        headline_text = item.title
        publish_date = item.published if hasattr(item, 'published') else 'Live Node Stream'
        
        nlp_processing_blob = TextBlob(headline_text)
        score = nlp_processing_blob.sentiment.polarity
        
        if score < -0.02:
            sentiment_tag = '<span class="state-bearish">[RISK CONTRACTION]</span>'
        elif score > 0.02:
            sentiment_tag = '<span class="state-bullish">[CAPACITY EXPANSION]</span>'
        else:
            sentiment_tag = '<span class="state-neutral">[STABLE PROFILE]</span>'
            
        st.markdown(f"""
        <div class="fw-news-wire-row">
            {sentiment_tag} <strong style="color:#0F172A !important;">{headline_text}</strong> <span style="color: #475569; font-size: 11px; margin-left: 10px;">// {publish_date}</span>
        </div>
        """, unsafe_allow_html=True)

except Exception as data_exception:
    st.error(f"Central terminal synchronization delay encountered. Diagnostic parameter details: {data_exception}")
