"""
dashboard.py — Project Pulse-Point Live Analytics Dashboard
============================================================
WHAT IS STREAMLIT?
    Streamlit is a Python library that turns a regular .py script
    into a fully interactive web app — no HTML, no CSS, no JavaScript needed.
    It's the #1 tool for data analysts to share insights as live dashboards.

WHAT THIS DASHBOARD SHOWS:
    - 5 KPI metric cards (price, sentiment, high, low, avg mood)
    - Interactive Plotly price chart with moving averages
    - Sentiment over time chart (color-coded bars)
    - Correlation scatter plot
    - Distribution histograms
    - Key insights panel
    - Latest data table

HOW TO RUN:
    streamlit run dashboard.py
    → Opens automatically in your browser at http://localhost:8501
"""

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

import config


# ─── PAGE CONFIGURATION ───────────────────────────────────────────────────────
# Must be the FIRST Streamlit command in the script
st.set_page_config(
    page_title='📊 Pulse-Point | Crypto Analytics',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)


# ─── PREMIUM DARK THEME CSS ───────────────────────────────────────────────────
st.markdown('''
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #080c18 0%, #0a0e1a 50%, #0d1421 100%);
    }

    /* Metric cards — the KPI boxes at the top */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #141930 0%, #1a2744 100%);
        border: 1px solid #2a3f6f;
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 24px rgba(0, 150, 255, 0.1);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 150, 255, 0.18);
    }
    div[data-testid="metric-container"] label {
        color: #8892a4 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }

    /* Section headers */
    .section-header {
        color: #00d4ff;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1e3a5f;
        letter-spacing: 0.03em;
    }

    /* Insight cards */
    .insight-box {
        background: linear-gradient(135deg, #141930 0%, #1a2744 100%);
        border-left: 4px solid #00d4ff;
        border-radius: 0 10px 10px 0;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        color: #c0c8d8;
        line-height: 1.6;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1421 0%, #141930 100%);
        border-right: 1px solid #1e3a5f;
    }

    /* Header */
    .main-title {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-title h1 {
        color: #00d4ff;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .main-title p {
        color: #8892a4;
        font-size: 1.05rem;
        margin: 0.4rem 0 0 0;
    }

    /* Divider */
    hr { border-color: #1e3a5f !important; }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid #2a3f6f;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
''', unsafe_allow_html=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_sentiment_info(score: float):
    """Return label and color for a sentiment score."""
    if score > config.BULLISH_THRESHOLD:
        return '🟢 BULLISH', '#2ecc71'
    elif score < config.BEARISH_THRESHOLD:
        return '🔴 BEARISH', '#e74c3c'
    else:
        return '🟡 NEUTRAL', '#f39c12'


# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)    # Cache for 60 seconds — auto-refreshes data
def load_data() -> pd.DataFrame:
    """Load data from SQLite and compute derived columns."""
    try:
        conn = sqlite3.connect(config.DB_PATH)
        df = pd.read_sql_query(
            'SELECT * FROM bitcoin_prices ORDER BY timestamp', conn
        )
        conn.close()
    except Exception as e:
        return pd.DataFrame()

    if df.empty:
        return df

    df['timestamp']         = pd.to_datetime(df['timestamp'])
    df['price_change_pct']  = df['price'].pct_change() * 100
    df['rolling_avg_6h']    = df['price'].rolling(window=12).mean()
    df['rolling_avg_24h']   = df['price'].rolling(window=48).mean()
    df['sentiment_smooth']  = df['sentiment'].rolling(window=12).mean()
    return df


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('## 📊 Pulse-Point')
    st.markdown('**Real-Time Crypto Intelligence**')
    st.markdown('---')

    auto_refresh = st.toggle('🔄 Auto-Refresh (60s)', value=False)

    st.markdown('### 🗓️ Data Range')
    time_range = st.selectbox(
        'Show data from:',
        ['Last 6 Hours', 'Last 24 Hours', 'Last 3 Days', 'Last 7 Days', 'All Time'],
        index=3
    )

    st.markdown('---')
    st.markdown('**📡 Data Sources**')
    st.markdown('- 💰 Price: CoinGecko API')
    st.markdown('- 📰 News: CoinDesk + CoinTelegraph')
    st.markdown('- 🧠 NLP: TextBlob Sentiment')
    st.markdown('- 🗄️ Storage: SQLite Database')
    st.markdown('---')
    st.markdown(f'🕐 *Last refresh: {datetime.now().strftime("%H:%M:%S")}*')

    if st.button('🔄 Refresh Now'):
        st.cache_data.clear()
        st.rerun()


# ─── LOAD & FILTER DATA ───────────────────────────────────────────────────────
df_all = load_data()

if df_all.empty:
    st.error('''
    ⚠️ **No data found in the database!**

    Run one of these first:
    ```
    python generate_sample_data.py    # Seed 7 days of sample data
    python tracker_v2.py             # Start live data collection
    ```
    ''')
    st.stop()

# Apply time range filter
time_deltas = {
    'Last 6 Hours'  : timedelta(hours=6),
    'Last 24 Hours' : timedelta(hours=24),
    'Last 3 Days'   : timedelta(days=3),
    'Last 7 Days'   : timedelta(days=7),
    'All Time'      : timedelta(days=9999),
}
cutoff = datetime.now() - time_deltas[time_range]
df = df_all[df_all['timestamp'] >= cutoff].copy()
if df.empty:
    df = df_all.copy()    # Fall back to all data if filter returns nothing


# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown('''
<div class="main-title">
    <h1>📊 Project Pulse-Point</h1>
    <p>Real-Time Bitcoin Price Intelligence & Market Sentiment Dashboard</p>
</div>
''', unsafe_allow_html=True)
st.markdown('---')


# ─── KPI METRIC CARDS ─────────────────────────────────────────────────────────
latest = df.iloc[-1]
prev   = df.iloc[-2] if len(df) > 1 else latest

price_delta     = latest['price'] - prev['price']
price_delta_pct = (price_delta / prev['price']) * 100 if prev['price'] else 0

sent_label, sent_color = get_sentiment_info(latest['sentiment'])
avg_sent               = df['sentiment'].mean()
avg_sent_label, _      = get_sentiment_info(avg_sent)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        '💰 BTC Price',
        f"${latest['price']:,.2f}",
        delta=f"{price_delta_pct:+.2f}%  (${price_delta:+,.0f})"
    )
with col2:
    st.metric('🧠 Sentiment Now', sent_label, delta=f"{latest['sentiment']:+.4f}")
with col3:
    st.metric('📈 Period High', f"${df['price'].max():,.2f}")
with col4:
    st.metric('📉 Period Low',  f"${df['price'].min():,.2f}")
with col5:
    st.metric('📊 Avg Mood', avg_sent_label, delta=f"{avg_sent:+.4f}")

st.markdown('---')


# ─── PRICE CHART ──────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📈 Bitcoin Price History</p>', unsafe_allow_html=True)

fig_price = go.Figure()

fig_price.add_trace(go.Scatter(
    x=df['timestamp'], y=df['price'],
    mode='lines', name='BTC Price',
    line=dict(color='#00d4ff', width=2),
    fill='tozeroy', fillcolor='rgba(0,212,255,0.05)',
    hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Price: $%{y:,.2f}<extra></extra>'
))
fig_price.add_trace(go.Scatter(
    x=df['timestamp'], y=df['rolling_avg_6h'],
    mode='lines', name='6H Moving Avg',
    line=dict(color='#ff6b35', width=2, dash='dash'),
    hovertemplate='6H Avg: $%{y:,.2f}<extra></extra>'
))
fig_price.add_trace(go.Scatter(
    x=df['timestamp'], y=df['rolling_avg_24h'],
    mode='lines', name='24H Moving Avg',
    line=dict(color='#ffd700', width=2.5),
    hovertemplate='24H Avg: $%{y:,.2f}<extra></extra>'
))

fig_price.update_layout(
    height=420,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,20,33,0.6)',
    font=dict(color='#c0c8d8', family='Inter, sans-serif'),
    xaxis=dict(gridcolor='#1e2d4a', title='Date & Time', showspikes=True),
    yaxis=dict(gridcolor='#1e2d4a', title='Price (USD)', tickformat='$,.0f'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                bgcolor='rgba(20,25,48,0.8)', bordercolor='#2a3f6f'),
    hovermode='x unified',
    margin=dict(t=10, b=50, l=70, r=20)
)
st.plotly_chart(fig_price, use_container_width=True)


# ─── SENTIMENT CHART ──────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🧠 Market Sentiment Analysis</p>', unsafe_allow_html=True)

bar_colors = [
    '#2ecc71' if s > config.BULLISH_THRESHOLD else
    '#e74c3c' if s < config.BEARISH_THRESHOLD else '#f39c12'
    for s in df['sentiment']
]

fig_sent = go.Figure()
fig_sent.add_trace(go.Bar(
    x=df['timestamp'], y=df['sentiment'],
    marker_color=bar_colors, opacity=0.7, name='Sentiment',
    hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Sentiment: %{y:.4f}<extra></extra>'
))
fig_sent.add_trace(go.Scatter(
    x=df['timestamp'], y=df['sentiment_smooth'],
    mode='lines', name='Smoothed Trend',
    line=dict(color='#ffffff', width=2.5),
    hovertemplate='Trend: %{y:.4f}<extra></extra>'
))
fig_sent.add_hline(y=0,    line_color='rgba(255,255,255,0.25)', line_width=1)
fig_sent.add_hline(y=0.05, line_color='#2ecc71', line_width=1, line_dash='dot',
                   annotation_text='Bullish', annotation_position='right')
fig_sent.add_hline(y=-0.05,line_color='#e74c3c', line_width=1, line_dash='dot',
                   annotation_text='Bearish', annotation_position='right')
fig_sent.update_layout(
    height=360,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,20,33,0.6)',
    font=dict(color='#c0c8d8'),
    xaxis=dict(gridcolor='#1e2d4a', title='Date & Time'),
    yaxis=dict(gridcolor='#1e2d4a', title='Sentiment Score', range=[-1.15, 1.15]),
    hovermode='x unified',
    legend=dict(bgcolor='rgba(20,25,48,0.8)', bordercolor='#2a3f6f'),
    margin=dict(t=10, b=50, l=70, r=80)
)
st.plotly_chart(fig_sent, use_container_width=True)


# ─── CORRELATION & DISTRIBUTION ───────────────────────────────────────────────
st.markdown('<p class="section-header">📐 Correlation & Distribution Deep-Dive</p>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    # Scatter: Sentiment vs Price Change
    df_corr = df.dropna(subset=['sentiment', 'price_change_pct'])
    corr_val = df_corr['sentiment'].corr(df_corr['price_change_pct'])

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Scatter(
        x=df_corr['sentiment'], y=df_corr['price_change_pct'],
        mode='markers',
        marker=dict(color=df_corr['sentiment'], colorscale='RdYlGn',
                    size=6, opacity=0.7, line=dict(color='white', width=0.3)),
        name='Data Points',
        hovertemplate='Sentiment: %{x:.3f}<br>Price Change: %{y:.3f}%<extra></extra>'
    ))

    # Manual trendline
    if len(df_corr) > 2:
        z = np.polyfit(df_corr['sentiment'], df_corr['price_change_pct'], 1)
        x_tr = np.linspace(df_corr['sentiment'].min(), df_corr['sentiment'].max(), 100)
        fig_sc.add_trace(go.Scatter(
            x=x_tr, y=np.poly1d(z)(x_tr),
            mode='lines', name='Trend',
            line=dict(color='white', width=2, dash='dash')
        ))

    fig_sc.update_layout(
        title=dict(text=f'Sentiment vs. Price Change  (r = {corr_val:.3f})',
                   font=dict(size=13, color='#c0c8d8')),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13,20,33,0.6)',
        font=dict(color='#c0c8d8'),
        xaxis=dict(gridcolor='#1e2d4a', title='Sentiment Score', zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
        yaxis=dict(gridcolor='#1e2d4a', title='Price Change (%)', zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
        showlegend=True,
        legend=dict(bgcolor='rgba(20,25,48,0.8)', bordercolor='#2a3f6f'),
        margin=dict(t=40, b=50, l=60, r=20)
    )
    st.plotly_chart(fig_sc, use_container_width=True)

with col_right:
    # Dual histogram
    fig_dist = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Price Distribution', 'Sentiment Distribution'),
        vertical_spacing=0.18
    )
    fig_dist.add_trace(
        go.Histogram(x=df['price'], nbinsx=30, marker_color='#00d4ff',
                     opacity=0.8, name='Price'),
        row=1, col=1
    )
    fig_dist.add_trace(
        go.Histogram(x=df['sentiment'], nbinsx=30, marker_color='#7c3aed',
                     opacity=0.8, name='Sentiment'),
        row=2, col=1
    )
    fig_dist.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13,20,33,0.6)',
        font=dict(color='#c0c8d8'),
        showlegend=False,
        margin=dict(t=40, b=30, l=60, r=20)
    )
    fig_dist.update_xaxes(gridcolor='#1e2d4a')
    fig_dist.update_yaxes(gridcolor='#1e2d4a')
    st.plotly_chart(fig_dist, use_container_width=True)


# ─── KEY INSIGHTS PANEL ───────────────────────────────────────────────────────
st.markdown('<p class="section-header">💡 Key Insights</p>', unsafe_allow_html=True)

price_range     = df['price'].max() - df['price'].min()
price_range_pct = (price_range / df['price'].min() * 100) if df['price'].min() > 0 else 0
bull_pct        = (df['sentiment'] > config.BULLISH_THRESHOLD).mean() * 100
corr_val_insight= df.dropna(subset=['sentiment','price_change_pct'])['sentiment'].corr(
                      df.dropna(subset=['sentiment','price_change_pct'])['price_change_pct']
                  )

i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(f'''
<div class="insight-box">
    <strong>💹 Price Volatility</strong><br>
    BTC swung <strong>${price_range:,.0f}</strong> ({price_range_pct:.1f}%) during this period,
    from a low of <strong>${df["price"].min():,.0f}</strong> to a high of 
    <strong>${df["price"].max():,.0f}</strong>.
</div>''', unsafe_allow_html=True)

with i2:
    signal = 'Strong signal' if abs(corr_val_insight) > 0.3 else 'Weak signal — more data needed'
    st.markdown(f'''
<div class="insight-box">
    <strong>🔗 Sentiment Signal</strong><br>
    Sentiment & price change show a <strong>{abs(corr_val_insight):.1%}</strong> correlation.
    <em>{signal}</em>. 
    {"Positive news tends to follow price increases." if corr_val_insight > 0 else ""}
</div>''', unsafe_allow_html=True)

with i3:
    st.markdown(f'''
<div class="insight-box">
    <strong>🧠 Market Mood</strong><br>
    <strong>{bull_pct:.0f}%</strong> of readings were bullish in this period. 
    Overall market tone: <strong>{avg_sent_label}</strong>
    (avg score: {avg_sent:+.4f}).
</div>''', unsafe_allow_html=True)


# ─── LATEST DATA TABLE ────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📋 Latest 20 Data Points</p>', unsafe_allow_html=True)

display_cols = ['timestamp', 'price', 'sentiment']
if 'headline' in df.columns:
    display_cols.append('headline')

display_df = df[display_cols].tail(20).copy()
display_df.columns = [c.title() for c in display_cols]
display_df = display_df.iloc[::-1].reset_index(drop=True)
display_df['Price']     = display_df['Price'].apply(lambda x: f'${x:,.2f}')
display_df['Sentiment'] = display_df['Sentiment'].apply(lambda x: f'{x:+.4f}')

st.dataframe(display_df, use_container_width=True, height=320)

st.markdown('---')
st.markdown(
    '<p style="color:#4a5568;text-align:center;font-size:0.85rem;">'
    '📊 Project Pulse-Point | Built with Python, Streamlit & Plotly | '
    f'Data points: {len(df_all):,} total | {len(df):,} in selected range'
    '</p>',
    unsafe_allow_html=True
)


# ─── AUTO-REFRESH ─────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(60)
    st.cache_data.clear()
    st.rerun()
