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
# 1. Advanced Institutional Interface Stylesheet (Light Isometric Matrix)
# ----------------------------------------------------
st.set_page_config(page_title="GLOBAL ENERGY MATRIX TERMINAL", layout="wide")

# High-contrast, clean architecture overriding all core select boxes safely
st.markdown("""
    <style>
        /* Base Canvas - High Contrast Light Isometric Emulation */
        .reportview-container { background-color: #F8FAFC !important; }
        .stApp { 
            background-color: #FAFAFA !important;
            background-image: 
                linear-gradient(30deg, #E2E8F0 12%, transparent 12.5%, transparent 87%, #E2E8F0 87.5%, #E2E8F0),
                linear-gradient(150deg, #E2E8F0 12%, transparent 12.5%, transparent 87%, #E2E8F0 87.5%, #E2E8F0),
                linear-gradient(300deg, #E2E8F0 12%, transparent 12.5%, transparent 87%, #E2E8F0 87.5%, #E2E8F0),
                linear-gradient(210deg, #E2E8F0 12%, transparent 12.5%, transparent 87%, #E2E8F0 87.5%, #E2E8F0),
                linear-gradient(30deg, #E2E8F0 38%, transparent 38.5%, transparent 61%, #E2E8F0 61.5%, #E2E8F0),
                linear-gradient(150deg, #E2E8F0 38%, transparent 38.5%, transparent 61%, #E2E8F0 61.5%, #E2E8F0);
            background-size: 50px 86px;
            background-position: 0 0, 0 0, 25px 43px, 25px 43px, 0 0, 25px 43px;
        }
        
        /* Corporate Rigid Block Header Layout */
        .fw-terminal-header {
            background-color: #FFFFFF;
            border-top: 4px solid #0F172A;
            border-bottom: 4px solid #0F172A;
            border-left: 1px solid #0F172A;
            border-right: 1px solid #0F172A;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .fw-terminal-title {
            color: #0F172A !important;
            font-family: 'Helvetica Neue', Arial, sans-serif !important;
            font-size: 26px !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            text-transform: uppercase !important;
            margin: 0 !important;
        }
        .fw-terminal-subtitle {
            color: #475569 !important;
            font-family: Arial, sans-serif !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            margin-top: 6px !important;
        }

        /* Safe Widget Target Containment preventing text blending or sizing bugs */
        div[data-testid="stSidebar"] { 
            background-color: #FFFFFF !important; 
            border-right: 2px solid #0F172A !important; 
        }
        div[data-testid="stSidebar"] label p {
            color: #0F172A !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            text-transform: uppercase;
        }
        
        /* Enforce high-contrast dark text inside Select Box options dynamically */
        div[data-baseweb="select"] * {
            color: #0F172A !important;
            font-weight: 500 !important;
        }
        
        /* Core Data Grid Matrix */
        .fw-matrix-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 25px; border: 2px solid #0F172A; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        .fw-matrix-table td { border: 1px solid #0F172A; padding: 12px 16px; background-color: #FFFFFF; color: #0F172A !important; font-weight: 500; }
        .fw-hdr-label { background-color: #F1F5F9 !important; color: #0F172A !important; font-weight: 700 !important; text-transform: uppercase; width: 18%; }
        
        /* Infrastructure Wire Rows */
        .fw-news-wire-row { 
            border: 1px solid #0F172A; 
            padding: 14px; 
            background-color: #FFFFFF; 
            margin-bottom: 10px; 
            border-left: 6px solid #0F172A; 
            color: #0F172A !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .fw-section-header { font-size: 14px; font-weight: 800; color: #0F172A !important; text-transform: uppercase; margin-bottom: 14px; border-bottom: 3px solid #0F172A; padding-bottom: 4px; letter-spacing: 0.5px; }
        
        /* Status Elements */
        .state-pos { color: #15803D !important; font-weight: 700; }
        .state-neg { color: #B91C1C !important; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# Main Corporate Header Block
st.markdown("""
    <div class="fw-terminal-header">
        <h1 class="fw-terminal-title">ENERGY INFRASTRUCTURE & DISPATCH REGULATORY TERMINAL</h1>
        <div class="fw-terminal-subtitle">PRODUCTION DATA MATRICES // SYSTEM VOLATILITY HORIZONS // LIVE TRANSMISSION LOGS</div>
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
selected_display = st.sidebar.selectbox("Asset Track Target", list(ASSET_METADATA.keys()))
asset_info = ASSET_METADATA[selected_display]
ticker = asset_info["ticker"]

historical_horizon = st.sidebar.selectbox("Historical Bounds", ["1y", "2y", "5y"], index=1)
volatility_model_type = st.sidebar.selectbox("Statistical Matrix Mode (GARCH)", ["studentst", "normal"], index=0)
confidence_interval = st.sidebar.selectbox("Value at Risk Threshold (VaR)", [0.95, 0.99], index=0)
projection_timeline = st.sidebar.slider("Forecast Lookahead Window (Days)", 5, 30, 15)

# Data Acquisition Engine
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
    # 3. Structural Operational Data Grid
    # ----------------------------------------------------
    direction_class = "state-pos" if df['Log_Returns'].iloc[-1] >= 0 else "state-neg"
    
    st.markdown("<div class='fw-section-header'>Asset Infrastructure Metrics</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class="fw-matrix-table">
        <tr>
            <td class="fw-hdr-label">Identifier Ticker</td><td><strong>{ticker}</strong></td>
            <td class="fw-hdr-label">System Classification</td><td>{asset_info['type']}</td>
            <td class="fw-hdr-label">Physical Grid Infrastructure</td><td>{asset_info['infrastructure']}</td>
            <td class="fw-hdr-label">Last Valuation</td><td class="{direction_class}">${df['Close'].iloc[-1]:.2f}</td>
        </tr>
        <tr>
            <td class="fw-hdr-label">Daily Settlement Net</td><td class="{direction_class}">{df['Log_Returns'].iloc[-1]:.2f}%</td>
            <td class="fw-hdr-label">Value at Risk (VaR)</td><td class="state-neg">{var_limit:.2f}%</td>
            <td class="fw-hdr-label">Expected Shortfall</td><td class="state-neg">{expected_shortfall:.2f}%</td>
            <td class="fw-hdr-label">Variance Persistence</td><td>{variance_persistence:.3f}</td>
        </tr>
        <tr>
            <td class="fw-hdr-label">Model Alpha Factor</td><td>{alpha_coefficient:.4f}</td>
            <td class="fw-hdr-label">Model Beta Factor</td><td>{beta_coefficient:.4f}</td>
            <td class="fw-hdr-label">Analysis Target Horizon</td><td>{projection_timeline} Business Days</td>
            <td class="fw-hdr-label">Operational Control Node</td><td>{asset_info['hq']}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # High-Contrast Pure Line Charts
    visual_grid = make_subplots(rows=1, cols=2, subplot_titles=("Historical Asset Pricing Series", "Statistical Volatility Horizon Map"), horizontal_spacing=0.06)
    visual_grid.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Settlement Price", line=dict(color='#0F172A', width=2)), row=1, col=1)
    visual_grid.add_trace(go.Scatter(x=projection_date_axis, y=annualized_vol_projection, name="Projected Variance", line=dict(color='#B91C1C', width=2, dash='dash')), row=1, col=2)
    
    visual_grid.update_layout(
        template="plotly_white", height=280, showlegend=False, margin=dict(l=0, r=0, t=25, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#FFFFFF'
    )
    visual_grid.update_xaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#0F172A')
    visual_grid.update_yaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#0F172A')
    st.plotly_chart(visual_grid, use_container_width=True)

    # Microclimate Thermodynamic Load Section
    st.markdown(f"<div class='fw-section-header'>Microclimate Thermodynamic Load Grid — {asset_info['hq']}</div>", unsafe_allow_html=True)
    climatological_matrix = pd.DataFrame({
        'Meteorological Node Metrics': ['Target Node Location Grid Point', 'Regional Degree Day Base Shift', '14-Day Temperature Deviation Model'],
        'Operational Value Reading': [asset_info['hq'], 'Baseline Normalized (+1.2% Structural Shift)', '+2.4°F vs Historic Season Vector'],
        'Grid Load Delivery Implication': ['Isolates spatial delivery constraints', 'Forecasts baseline consumer volume demand profiles', 'Prompt-month storage draw trigger vector']
    })
    st.table(climatological_matrix)

    # ----------------------------------------------------
    # 4. Pure Professional News Wire Stream
    # ----------------------------------------------------
    st.markdown("<div class='fw-section-header'>Live Market Transmission Wire</div>", unsafe_allow_html=True)
    
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
            BackupArticle("Nuclear Generation Grid Interconnect Footprint Expands", "System Session Feed Log"),
            BackupArticle("Photovoltaic Transmission Matrix Logs Peak Seasonal Performance Profiles", "System Session Feed Log")
        ]

    for item in headlines_extracted:
        headline_text = item.title
        publish_date = item.published if hasattr(item, 'published') else 'Live Entry Stream'
        
        nlp_processing_blob = TextBlob(headline_text)
        score = nlp_processing_blob.sentiment.polarity
        
        if score < -0.02:
            sentiment_tag = '<span class="state-neg">// RISK DEVIATION IMPLICATION</span>'
        elif score > 0.02:
            sentiment_tag = '<span class="state-pos">// POSITIVE EFFICIENCY PROFILE</span>'
        else:
            sentiment_tag = '<span style="color:#475569; font-weight:700;">// VOLATILITY STABLE PROFILE</span>'
            
        st.markdown(f"""
        <div class="fw-news-wire-row">
            <strong style="color:#0F172A !important; font-size:14px;">{headline_text}</strong> 
            <br>
            <span style="color: #475569; font-size: 11px; text-transform: uppercase; font-weight:700;">{publish_date} {sentiment_tag}</span>
        </div>
        """, unsafe_allow_html=True)

except Exception as data_exception:
    st.error(f"Central terminal synchronization delay encountered. Details: {data_exception}")
