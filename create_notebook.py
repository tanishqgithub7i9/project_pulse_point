"""
create_notebook.py — Generates the Full Analysis Notebook
==========================================================
WHAT THIS DOES:
    This script PROGRAMMATICALLY creates analysis.ipynb using the
    nbformat library. Instead of manually building JSON (error-prone),
    we write Python code that generates the notebook for us.

WHY NOT WRITE THE NOTEBOOK MANUALLY?
    Jupyter notebooks are stored as JSON files. Writing JSON by hand
    for 15+ cells is tedious and error-prone. This approach is how
    data engineering teams VERSION CONTROL and AUTO-GENERATE notebooks.

HOW TO USE:
    python create_notebook.py
    → This generates analysis.ipynb in the same folder
    Then open it with: jupyter notebook analysis.ipynb
"""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell


# ─── CELL CONTENT ─────────────────────────────────────────────────────────────
# Each section below is the Python code (or markdown) for one notebook cell.
# We use triple-quoted strings for multi-line content.

CELLS = []


# ─── CELL 0: Title ────────────────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""# 📊 Project Pulse-Point — Bitcoin Intelligence Analysis

**Author:** Your Name | **Date:** April 2026 | **Project:** End-to-End Crypto Analytics Pipeline

---

## 🎯 Project Summary

This notebook provides a complete **Exploratory Data Analysis (EDA)** of Bitcoin price and
market sentiment data collected by the **Pulse-Point** real-time pipeline.

The data was gathered every 30 minutes by:
- 💰 Fetching Bitcoin price from **CoinGecko API**
- 📰 Pulling real news headlines from **CoinDesk & CoinTelegraph RSS feeds**
- 🧠 Running **TextBlob NLP** sentiment analysis on each headline
- 🗄️ Storing everything in a **SQLite database**

### 📋 Analysis Goals
1. Understand Bitcoin price behavior and volatility over 7 days
2. Track market sentiment trends (bullish vs. bearish periods)
3. Discover correlation between news sentiment and price movement
4. Generate actionable business insights from raw data

---
"""))


# ─── CELL 1: Imports ──────────────────────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  STEP 1: IMPORT LIBRARIES
#  A data analyst's toolkit — each library has a specific job
# ════════════════════════════════════════════════════════

import sqlite3                          # Read from our local database
import pandas as pd                     # THE data manipulation library
import numpy as np                      # Math, statistics, arrays
import matplotlib.pyplot as plt         # Foundation plotting library
import matplotlib.dates as mdates       # Format date labels on charts
import seaborn as sns                   # Beautiful statistical charts
import warnings
warnings.filterwarnings('ignore')       # Hide minor warnings

# ── Configure visualization style ────────────────────────────────────────────
plt.style.use('dark_background')
plt.rcParams.update({
    'figure.dpi'        : 120,
    'font.size'         : 11,
    'axes.titlesize'    : 15,
    'axes.titleweight'  : 'bold',
    'axes.labelsize'    : 12,
    'figure.facecolor'  : '#0a0e1a',
    'axes.facecolor'    : '#0d1421',
    'axes.edgecolor'    : '#2a3f6f',
    'axes.grid'         : True,
    'grid.alpha'        : 0.2,
    'xtick.color'       : '#8892a4',
    'ytick.color'       : '#8892a4',
    'text.color'        : '#c0c8d8',
    'legend.facecolor'  : '#141930',
    'legend.edgecolor'  : '#2a3f6f',
})

print('✅ All libraries loaded successfully!')
print('🚀 Project Pulse-Point — Analysis Notebook v2.0')
"""))


# ─── CELL 2: Load Data ────────────────────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  STEP 2: LOAD DATA FROM SQLITE DATABASE
#  pd.read_sql_query() lets us run SQL directly into a DataFrame
# ════════════════════════════════════════════════════════

# Connect to database and run a SQL query
conn = sqlite3.connect('pulse_point.db')
df = pd.read_sql_query('SELECT * FROM bitcoin_prices ORDER BY timestamp', conn)
conn.close()

# Convert timestamp string → proper datetime type
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Quick summary
n_rows  = len(df)
ts_min  = df['timestamp'].min().strftime('%Y-%m-%d %H:%M')
ts_max  = df['timestamp'].max().strftime('%Y-%m-%d %H:%M')

print(f'📥 Dataset loaded successfully!')
print(f'   Rows (observations) : {n_rows:,}')
print(f'   Columns             : {list(df.columns)}')
print(f'   Start time          : {ts_min}')
print(f'   End time            : {ts_max}')
print()
print('🔍 First 10 rows:')
df.head(10)
"""))


# ─── CELL 3: Section 1 Header ─────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""\
---
## 📋 Section 1: Data Overview & Cleaning

**Key concept:** Before ANY analysis, a data analyst MUST understand and clean their data.

Steps we follow:
1. **Inspect** — What does the data look like? What are the data types?
2. **Check quality** — Are there missing values? Duplicates? Wrong types?
3. **Clean** — Fix issues found
4. **Engineer features** — Create NEW columns derived from existing ones (e.g., % change, rolling averages)

This step is where real analysts spend 60-80% of their time!
"""))


# ─── CELL 4: Data Cleaning & Feature Engineering ─────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  STEP 3: DATA CLEANING + FEATURE ENGINEERING
# ════════════════════════════════════════════════════════

print('🔎 DATA QUALITY CHECK')
print('=' * 55)
print(f'Shape      : {df.shape[0]:,} rows × {df.shape[1]} columns')
print()
print('Data Types:')
print(df.dtypes.to_string())
print()
print('Missing Values:')
print(df.isnull().sum().to_string())

# ── Clean: Remove any rows missing price or sentiment ─────────────────────────
df = df.dropna(subset=['price', 'sentiment'])
print(f'\\n✅ Clean records: {len(df):,}')

# ── Feature Engineering: Create analytical columns ───────────────────────────
print('\\n🔧 Engineering features...')

df['hour']            = df['timestamp'].dt.hour                       # 0–23 hour of day
df['day_of_week']     = df['timestamp'].dt.day_name()                 # Monday, Tuesday...
df['date']            = df['timestamp'].dt.date                       # Date only (2026-04-01)
df['price_change_pct']= df['price'].pct_change() * 100               # % change vs previous row
df['price_change_abs']= df['price'].diff()                            # $ change vs previous row
df['rolling_avg_6h']  = df['price'].rolling(window=12).mean()         # 6H avg (12 × 30min)
df['rolling_avg_24h'] = df['price'].rolling(window=48).mean()         # 24H avg (48 × 30min)
df['next_price_change']= df['price_change_pct'].shift(-1)             # NEXT period's % change

# Classify sentiment into human-readable labels
def classify_sentiment(score):
    if score > 0.05:
        return 'Bullish'
    elif score < -0.05:
        return 'Bearish'
    else:
        return 'Neutral'

df['sentiment_label'] = df['sentiment'].apply(classify_sentiment)

print('✅ Features created:')
new_cols = ['hour','day_of_week','price_change_pct','rolling_avg_6h','rolling_avg_24h','sentiment_label']
for col in new_cols:
    print(f'   + {col}')
"""))


# ─── CELL 5: Summary Statistics ───────────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  STEP 4: SUMMARY STATISTICS
#  Know your data numbers BEFORE making any charts!
# ════════════════════════════════════════════════════════

print('═' * 60)
print('  📊 PROJECT PULSE-POINT — SUMMARY STATISTICS')
print('═' * 60)

# ── Price Stats ───────────────────────────────────────────────────────────────
print('\\n💰 BITCOIN PRICE (USD):')
print(f'   Mean         : ${df["price"].mean():>12,.2f}  ← average price over period')
print(f'   Median       : ${df["price"].median():>12,.2f}  ← middle value (robust to outliers)')
print(f'   Std Dev (σ)  : ${df["price"].std():>12,.2f}  ← VOLATILITY — how much it swings')
print(f'   Minimum      : ${df["price"].min():>12,.2f}')
print(f'   Maximum      : ${df["price"].max():>12,.2f}')
print(f'   Range        : ${df["price"].max()-df["price"].min():>12,.2f}')

# ── Sentiment Stats ───────────────────────────────────────────────────────────
overall_mood = 'Slightly Bullish 📈' if df['sentiment'].mean() > 0 else 'Slightly Bearish 📉'
print('\\n🧠 SENTIMENT SCORE (-1.0 = Very Bearish → +1.0 = Very Bullish):')
print(f'   Mean         : {df["sentiment"].mean():>10.4f}  ← {overall_mood}')
print(f'   Std Dev      : {df["sentiment"].std():>10.4f}')
print(f'   Most Bearish : {df["sentiment"].min():>10.4f}  at {df.loc[df["sentiment"].idxmin(),"timestamp"].strftime("%Y-%m-%d %H:%M")}')
print(f'   Most Bullish : {df["sentiment"].max():>10.4f}  at {df.loc[df["sentiment"].idxmax(),"timestamp"].strftime("%Y-%m-%d %H:%M")}')

# ── Sentiment Distribution ────────────────────────────────────────────────────
bull = (df['sentiment_label']=='Bullish').sum()
neut = (df['sentiment_label']=='Neutral').sum()
bear = (df['sentiment_label']=='Bearish').sum()
tot  = len(df)

print('\\n📊 SENTIMENT BREAKDOWN:')
print(f'   🟢 Bullish : {bull:>4} readings ({bull/tot*100:.1f}%)')
print(f'   🟡 Neutral : {neut:>4} readings ({neut/tot*100:.1f}%)')
print(f'   🔴 Bearish : {bear:>4} readings ({bear/tot*100:.1f}%)')
print('═' * 60)
"""))


# ─── CELL 6: Section 2 Header ─────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""\
---
## 📈 Section 2: Price & Sentiment Trend Analysis

**Key concept:** Time series analysis shows HOW variables change over time.

**Rolling Average (Moving Average):**
A rolling average smooths out short-term noise to reveal the underlying trend.
For example, a 6-hour rolling average takes the average of the past 6 hours of data.
This is one of the most fundamental tools in financial data analysis.
"""))


# ─── CELL 7: Chart 1 — Price Trend ────────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  CHART 1: Bitcoin Price Trend with Moving Averages
# ════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(16, 7))

# ── Raw price line ────────────────────────────────────────────────────────────
ax.plot(df['timestamp'], df['price'],
        color='#00d4ff', linewidth=1.5, alpha=0.7, label='BTC Price', zorder=2)

# ── Rolling averages (smoothed trend lines) ───────────────────────────────────
ax.plot(df['timestamp'], df['rolling_avg_6h'],
        color='#ff6b35', linewidth=2.5, linestyle='--', label='6H Moving Avg', zorder=3)
ax.plot(df['timestamp'], df['rolling_avg_24h'],
        color='#ffd700', linewidth=3, label='24H Moving Avg', zorder=4)

# ── Area fill under price line ────────────────────────────────────────────────
ax.fill_between(df['timestamp'], df['price'], df['price'].min(),
                alpha=0.08, color='#00d4ff', zorder=1)

# ── Annotate High and Low points ──────────────────────────────────────────────
max_idx = df['price'].idxmax()
min_idx = df['price'].idxmin()

ax.annotate(f'High: ${df.loc[max_idx, "price"]:,.0f}',
            xy=(df.loc[max_idx, 'timestamp'], df.loc[max_idx, 'price']),
            xytext=(0, 15), textcoords='offset points',
            fontsize=10, color='#2ecc71',
            arrowprops=dict(arrowstyle='->', color='#2ecc71', lw=1.5))

ax.annotate(f'Low: ${df.loc[min_idx, "price"]:,.0f}',
            xy=(df.loc[min_idx, 'timestamp'], df.loc[min_idx, 'price']),
            xytext=(0, -22), textcoords='offset points',
            fontsize=10, color='#e74c3c',
            arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.5))

# ── Labels, formatting ────────────────────────────────────────────────────────
ax.set_title('Bitcoin Price Trend — 7-Day Analysis with Moving Averages', pad=15)
ax.set_xlabel('Date & Time')
ax.set_ylabel('Price (USD)')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\\n%H:%M'))
ax.legend(loc='upper left', fontsize=11)

plt.tight_layout()
plt.savefig('chart_01_price_trend.png', dpi=150, bbox_inches='tight', facecolor='#0a0e1a')
plt.show()
print('✅ Saved as chart_01_price_trend.png')
"""))


# ─── CELL 8: Chart 2 — Sentiment Trend ───────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  CHART 2: Market Sentiment Over Time (Color-Coded)
#  Green bars = bullish readings | Red = bearish | Yellow = neutral
# ════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(16, 6))

# ── Color-coded bars ──────────────────────────────────────────────────────────
bar_colors = [
    '#2ecc71' if s > 0.05 else '#e74c3c' if s < -0.05 else '#f39c12'
    for s in df['sentiment']
]
ax.bar(df['timestamp'], df['sentiment'],
       color=bar_colors, alpha=0.75, width=0.018, label='Raw Sentiment')

# ── Smoothed trend line ───────────────────────────────────────────────────────
smooth = df['sentiment'].rolling(window=12).mean()
ax.plot(df['timestamp'], smooth,
        color='#ffffff', linewidth=2.5, alpha=0.9, label='12-Period Moving Avg')

# ── Reference lines ───────────────────────────────────────────────────────────
ax.axhline(y=0,     color='white', linewidth=1.5, linestyle='-',  alpha=0.3)
ax.axhline(y=0.05,  color='#2ecc71', linewidth=1, linestyle=':', alpha=0.5, label='Bullish Threshold')
ax.axhline(y=-0.05, color='#e74c3c', linewidth=1, linestyle=':', alpha=0.5, label='Bearish Threshold')

# ── Green/Red fill areas ──────────────────────────────────────────────────────
ax.fill_between(df['timestamp'], smooth, 0,
                where=(smooth > 0), color='#2ecc71', alpha=0.1, interpolate=True)
ax.fill_between(df['timestamp'], smooth, 0,
                where=(smooth < 0), color='#e74c3c', alpha=0.1, interpolate=True)

ax.set_title('Market Sentiment Over Time — Bullish vs. Bearish Readings')
ax.set_xlabel('Date & Time')
ax.set_ylabel('Sentiment Score (-1 to +1)')
ax.set_ylim(-1.15, 1.15)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('chart_02_sentiment.png', dpi=150, bbox_inches='tight', facecolor='#0a0e1a')
plt.show()
print('✅ Saved as chart_02_sentiment.png')
"""))


# ─── CELL 9: Section 3 Header ─────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""\
---
## 📊 Section 3: Distribution Analysis

**Key concept:** Distribution plots show WHERE most values cluster.

- A **normal distribution** (bell curve) means values spread evenly around the mean
- **Right-skewed** distribution = more lower values (bearish periods dominate)
- **Left-skewed** distribution = more higher values (bullish periods dominate)
- **Spread (std dev / σ)** measures volatility — crucial for risk assessment in finance
"""))


# ─── CELL 10: Chart 3 — Distributions ────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  CHART 3: Price & Sentiment Distribution Histograms
#  Histograms answer: 'What range of values appears most often?'
# ════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# ── LEFT: Price Distribution ──────────────────────────────────────────────────
axes[0].hist(df['price'], bins=40, color='#00d4ff', alpha=0.8,
             edgecolor='#0a0e1a', linewidth=0.5)

# Mark mean and median
axes[0].axvline(df['price'].mean(),   color='#ffd700', linewidth=2.5, linestyle='--',
                label=f'Mean:   ${df["price"].mean():,.0f}')
axes[0].axvline(df['price'].median(), color='#ff6b35', linewidth=2,   linestyle=':',
                label=f'Median: ${df["price"].median():,.0f}')

axes[0].set_title('Bitcoin Price Distribution')
axes[0].set_xlabel('Price (USD)')
axes[0].set_ylabel('Frequency (# of readings)')
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
axes[0].legend()

# ── RIGHT: Sentiment Distribution ────────────────────────────────────────────
axes[1].hist(df['sentiment'], bins=40, color='#7c3aed', alpha=0.8,
             edgecolor='#0a0e1a', linewidth=0.5)

axes[1].axvline(0,                   color='white',  linewidth=2,   linestyle='-',  alpha=0.5, label='Neutral (0.0)')
axes[1].axvline(df['sentiment'].mean(),color='#ffd700',linewidth=2.5, linestyle='--',
                label=f'Mean: {df["sentiment"].mean():.3f}')

# Annotate regions
y_top = axes[1].get_ylim()[1] * 0.8
axes[1].text(-0.95, y_top, 'BEARISH', color='#e74c3c', fontsize=13, fontweight='bold', alpha=0.8)
axes[1].text(0.35,  y_top, 'BULLISH', color='#2ecc71', fontsize=13, fontweight='bold', alpha=0.8)

axes[1].set_title('Sentiment Score Distribution')
axes[1].set_xlabel('Sentiment Score  (-1.0 = Very Bearish → +1.0 = Very Bullish)')
axes[1].set_ylabel('Frequency (# of readings)')
axes[1].legend()

plt.suptitle('Distribution Analysis — Where Do Most Values Cluster?',
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('chart_03_distributions.png', dpi=150, bbox_inches='tight', facecolor='#0a0e1a')
plt.show()
print('✅ Saved as chart_03_distributions.png')
"""))


# ─── CELL 11: Section 4 Header ────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""\
---
## 🔗 Section 4: Correlation & Predictive Analysis

**Key concept:** Correlation measures whether two variables move together.

| Correlation | Meaning |
|---|---|
| **+1.0** | Perfect positive: when X goes up, Y always goes up |
| **0.0**  | No relationship |
| **-1.0** | Perfect negative: when X goes up, Y always goes down |

### 💡 The Million-Dollar Question:
> *Does positive news sentiment **predict** a Bitcoin price increase?*

This is the core business analytical question of Project Pulse-Point.
We test this by comparing today's sentiment against **tomorrow's** price change.
"""))


# ─── CELL 12: Chart 4 — Correlation ──────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  CHART 4: Correlation Analysis
#  Left:  Scatter plot — Sentiment vs Next Price Change
#  Right: Heatmap — How all variables correlate together
# ════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# ── LEFT: Scatter Plot ────────────────────────────────────────────────────────
df_clean = df.dropna(subset=['sentiment', 'next_price_change'])

sc = axes[0].scatter(
    df_clean['sentiment'], df_clean['next_price_change'],
    c=df_clean['sentiment'], cmap='RdYlGn',
    alpha=0.6, s=35, edgecolors='white', linewidth=0.3
)

# Manual trend line using numpy polynomial fit
z = np.polyfit(df_clean['sentiment'], df_clean['next_price_change'], 1)
x_line = np.linspace(df_clean['sentiment'].min(), df_clean['sentiment'].max(), 100)
axes[0].plot(x_line, np.poly1d(z)(x_line), 'w--', linewidth=2.5, label='Trend Line')

# Reference crosshairs at zero
axes[0].axhline(y=0, color='white', linewidth=0.8, alpha=0.3)
axes[0].axvline(x=0, color='white', linewidth=0.8, alpha=0.3)

corr_val = df_clean['sentiment'].corr(df_clean['next_price_change'])
axes[0].set_title(f'Sentiment → Next Price Change\\n(Correlation: {corr_val:.4f})')
axes[0].set_xlabel('Current Sentiment Score')
axes[0].set_ylabel('Next Period Price Change (%)')
axes[0].legend()
plt.colorbar(sc, ax=axes[0], label='Sentiment Score')

# ── RIGHT: Correlation Heatmap ────────────────────────────────────────────────
corr_cols   = ['price', 'sentiment', 'price_change_pct', 'hour', 'rolling_avg_6h']
corr_labels = ['Price', 'Sentiment', 'Price Change%', 'Hour of Day', '6H Moving Avg']

corr_matrix = df[corr_cols].corr()
corr_matrix.index   = corr_labels
corr_matrix.columns = corr_labels

sns.heatmap(
    corr_matrix, ax=axes[1],
    annot=True, fmt='.3f', cmap='coolwarm',
    vmin=-1, vmax=1, center=0,
    square=True, linewidths=2, linecolor='#0a0e1a',
    annot_kws={'size': 11, 'weight': 'bold'},
    cbar_kws={'label': 'Correlation Coefficient', 'shrink': 0.8}
)
axes[1].set_title('Feature Correlation Heatmap\\n(How do all variables relate to each other?)')
axes[1].tick_params(axis='x', rotation=30, labelsize=10)
axes[1].tick_params(axis='y', rotation=0,  labelsize=10)

plt.tight_layout()
plt.savefig('chart_04_correlation.png', dpi=150, bbox_inches='tight', facecolor='#0a0e1a')
plt.show()
print(f'✅ Saved as chart_04_correlation.png')
print(f'🔑 Key finding: Sentiment shows {abs(corr_val):.1%} correlation with next price change.')
"""))


# ─── CELL 13: Chart 5 — Combined Dual Axis ────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  CHART 5: Combined Dual-Axis — Price + Sentiment
#  Two variables, same timeline, two y-axes
#  Great for spotting: does sentiment shift BEFORE price moves?
# ════════════════════════════════════════════════════════

fig, ax1 = plt.subplots(figsize=(16, 8))

# ── Left axis: BTC Price ──────────────────────────────────────────────────────
color_price = '#00d4ff'
ax1.set_xlabel('Date & Time', fontsize=12)
ax1.set_ylabel('BTC Price (USD)', color=color_price, fontsize=13, labelpad=10)
line1 = ax1.plot(df['timestamp'], df['price'],
                 color=color_price, linewidth=2, label='BTC Price', zorder=2)
ax1.tick_params(axis='y', labelcolor=color_price)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax1.fill_between(df['timestamp'], df['price'], df['price'].min(),
                 alpha=0.06, color=color_price)

# ── Right axis: Smoothed Sentiment ───────────────────────────────────────────
color_sent = '#ff6b35'
ax2 = ax1.twinx()                      # twinx() creates a second y-axis sharing the same x-axis
ax2.set_ylabel('Sentiment Score (12-period MA)', color=color_sent, fontsize=13, labelpad=10)

smooth_sent = df['sentiment'].rolling(window=12).mean()
line2 = ax2.plot(df['timestamp'], smooth_sent,
                 color=color_sent, linewidth=2.5, label='Sentiment Trend')
ax2.tick_params(axis='y', labelcolor=color_sent)
ax2.set_ylim(-1.2, 1.2)
ax2.axhline(y=0, color=color_sent, linewidth=0.8, linestyle='--', alpha=0.4)
ax2.fill_between(df['timestamp'], smooth_sent, 0,
                 where=(smooth_sent > 0), color='#2ecc71', alpha=0.08, interpolate=True)
ax2.fill_between(df['timestamp'], smooth_sent, 0,
                 where=(smooth_sent < 0), color='#e74c3c', alpha=0.08, interpolate=True)

# ── Combined legend ───────────────────────────────────────────────────────────
all_lines  = line1 + line2
all_labels = [l.get_label() for l in all_lines]
ax1.legend(all_lines, all_labels, loc='upper left', fontsize=11,
           facecolor='#141930', edgecolor='#2a3f6f')

ax1.set_title('BTC Price vs. Market Sentiment — Dual-Axis Time Series\\n'
              'Can you spot when sentiment shifts precede price moves?', pad=15)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.grid(True, alpha=0.12)

plt.tight_layout()
plt.savefig('chart_05_combined.png', dpi=150, bbox_inches='tight', facecolor='#0a0e1a')
plt.show()
print('✅ Saved as chart_05_combined.png')
"""))


# ─── CELL 14: Section 5 Header ────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""\
---
## 💡 Section 5: Business Insights Report

**Key concept:** Raw data → Clean numbers → Business decisions.

As a data analyst, your job isn't just to make charts.
Your job is to **translate numbers into language that business leaders understand**.

The insights below are written for a non-technical audience (e.g., a trading team manager).
"""))


# ─── CELL 15: Business Insights ───────────────────────────────────────────────
CELLS.append(new_code_cell("""\
# ════════════════════════════════════════════════════════
#  STEP 5: BUSINESS INSIGHTS REPORT
#  Translate data findings into plain-English decisions
# ════════════════════════════════════════════════════════

# ── Compute key metrics ───────────────────────────────────────────────────────
same_corr  = df['sentiment'].corr(df['price_change_pct'])
next_corr  = df['sentiment'].corr(df['next_price_change'])
price_range= df['price'].max() - df['price'].min()
range_pct  = (price_range / df['price'].min()) * 100

bull_pct   = (df['sentiment_label']=='Bullish').mean() * 100
neut_pct   = (df['sentiment_label']=='Neutral').mean() * 100
bear_pct   = (df['sentiment_label']=='Bearish').mean() * 100

hourly_ret = df.groupby('hour')['price_change_pct'].mean()
best_hour  = hourly_ret.idxmax()
worst_hour = hourly_ret.idxmin()

mood_str   = 'BULLISH 📈' if df['sentiment'].mean() > 0 else 'BEARISH 📉'

ts_start   = df['timestamp'].min().strftime('%Y-%m-%d')
ts_end     = df['timestamp'].max().strftime('%Y-%m-%d')

# ── Print report ──────────────────────────────────────────────────────────────
print('═' * 65)
print('    📋 PROJECT PULSE-POINT — BUSINESS INSIGHTS REPORT')
print('═' * 65)
print()
print(f'  📅 Period         : {ts_start} → {ts_end} (7 days)')
print(f'  📊 Observations   : {len(df):,} data points (every 30 minutes)')
print()
print('  ─── 💰 PRICE ANALYSIS ────────────────────────────────────────')
print(f'  Range         : ${df["price"].min():,.2f} — ${df["price"].max():,.2f}')
print(f'  Total swing   : ${price_range:,.2f}  ({range_pct:.1f}% move from low to high)')
print(f'  Avg price     : ${df["price"].mean():,.2f}')
print(f'  Volatility σ  : ${df["price"].std():,.2f}  ← higher = more risk & opportunity')
print()
print('  ─── 🧠 SENTIMENT ANALYSIS ────────────────────────────────────')
print(f'  Overall mood  : {mood_str}  (mean score: {df["sentiment"].mean():.4f})')
print(f'  🟢 Bullish    : {bull_pct:.1f}%  of all 30-min windows')
print(f'  🟡 Neutral    : {neut_pct:.1f}%  of all 30-min windows')
print(f'  🔴 Bearish    : {bear_pct:.1f}%  of all 30-min windows')
print()
print('  ─── 🔗 PREDICTIVE SIGNAL ─────────────────────────────────────')
print(f'  Same-period correlation  : {same_corr:+.4f}')
print(f'  Predictive correlation   : {next_corr:+.4f}  ← Can sentiment predict next move?')

if abs(next_corr) > 0.3:
    print(f'  ✅ STRONG SIGNAL: {abs(next_corr)*100:.0f}% correlation detected!')
    direction = 'PRECEDES price increases' if next_corr > 0 else 'PRECEDES price drops'
    print(f'     Positive sentiment {direction}.')
elif abs(next_corr) > 0.1:
    print(f'  ⚠️  WEAK SIGNAL: {abs(next_corr)*100:.0f}% correlation — more data needed.')
else:
    print(f'  📊 NO CLEAR SIGNAL — more data & richer news sources needed.')
    print(f'     Consider adding Twitter, Reddit APIs for better signal.')

print()
print('  ─── ⏰ TIMING PATTERNS ───────────────────────────────────────')
print(f'  Best avg return hour  : {best_hour:02d}:00 UTC  ({hourly_ret[best_hour]:+.4f}% avg)')
print(f'  Worst avg return hour : {worst_hour:02d}:00 UTC  ({hourly_ret[worst_hour]:+.4f}% avg)')
print()
print('  ─── 🚀 RECOMMENDED NEXT STEPS ───────────────────────────────')
print('  1. Integrate Twitter/Reddit API for richer sentiment signals')
print('  2. Collect 30+ days of data for statistical significance')
print('  3. Build a machine learning model to predict price direction')
print('  4. Add ETH/SOL comparison for multi-asset market analysis')
print('  5. Create a backtesting simulation to validate the signal')
print()
print('═' * 65)
"""))


# ─── CELL 16: Conclusion ──────────────────────────────────────────────────────
CELLS.append(new_markdown_cell("""\
---
## 🎯 Conclusion

This analysis demonstrates a complete **end-to-end data analytics pipeline**:

| Step | Tool | What We Did |
|---|---|---|
| **Collect** | `requests` + RSS | Fetched real-time BTC price and crypto news |
| **Store** | SQLite | Persisted all data in a structured database |
| **Load** | `pandas.read_sql_query()` | Loaded data into a DataFrame with SQL |
| **Clean** | `pandas` | Handled nulls, corrected data types |
| **Engineer** | `numpy`, `pandas` | Created rolling averages, % changes, labels |
| **Analyze** | `matplotlib`, `seaborn` | Built 5 professional charts |
| **Correlate** | `numpy.polyfit`, `pandas.corr()` | Tested sentiment as price predictor |
| **Communicate** | Markdown + print | Wrote business insights in plain English |

### 📊 Charts Generated
- `chart_01_price_trend.png` — Price trend with moving averages
- `chart_02_sentiment.png` — Sentiment analysis (color-coded)
- `chart_03_distributions.png` — Price & sentiment frequency distributions
- `chart_04_correlation.png` — Correlation heatmap + scatter plot
- `chart_05_combined.png` — Dual-axis price + sentiment view

---

> **Project Pulse-Point** — Built to demonstrate industry-ready Python data analytics skills
> including API integration, database management, EDA, statistical analysis, and business communication.
"""))


# ─── BUILD THE NOTEBOOK ───────────────────────────────────────────────────────
def create_notebook():
    """Assemble all cells into a Jupyter notebook and save it."""
    nb = new_notebook()
    nb.cells = CELLS

    # Set notebook metadata
    nb.metadata = {
        'kernelspec': {
            'display_name': 'Python 3',
            'language': 'python',
            'name': 'python3'
        },
        'language_info': {
            'name': 'python',
            'version': '3.9.0'
        }
    }

    output_path = 'analysis.ipynb'
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

    print()
    print('═' * 55)
    print('  ✅ analysis.ipynb CREATED SUCCESSFULLY!')
    print('═' * 55)
    print(f'  Total cells   : {len(nb.cells)}')
    print(f'  Code cells    : {sum(1 for c in nb.cells if c.cell_type == "code")}')
    print(f'  Markdown cells: {sum(1 for c in nb.cells if c.cell_type == "markdown")}')
    print()
    print('  Next step:')
    print('  Open it with: jupyter notebook analysis.ipynb')
    print('  Then: Run All Cells  (Kernel → Restart & Run All)')
    print()
    print('  This will generate 5 professional charts + the full')
    print('  business insights report!')
    print('═' * 55)


if __name__ == '__main__':
    create_notebook()
