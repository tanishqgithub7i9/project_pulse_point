# 📊 Project Pulse-Point

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75?logo=plotly&logoColor=white)](https://plotly.com)

> **A Real-Time Bitcoin Price Intelligence & Market Sentiment Analytics System**

---

## 🎯 What Is This Project?

**Project Pulse-Point** is an end-to-end data analytics pipeline that:

1. 💰 **Fetches** live Bitcoin prices every 5 minutes via CoinGecko API
2. 📰 **Reads** real crypto news headlines from CoinDesk & CoinTelegraph RSS feeds
3. 🧠 **Analyzes** market sentiment using Natural Language Processing (TextBlob NLP)
4. 🗄️ **Stores** all data in a local SQLite relational database
5. 📊 **Visualizes** trends, correlations & insights via a live Streamlit dashboard
6. 📓 **Reports** findings in a professional Jupyter EDA notebook

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PROJECT PULSE-POINT                             │
│                                                                     │
│  CoinGecko API ──────┐                                              │
│                      ├──► tracker_v2.py ──► pulse_point.db         │
│  RSS News Feeds ─────┘         │                   │               │
│  (CoinDesk, CoinTelegraph)     │ (ETL Pipeline)    │               │
│                                ▼                   ▼               │
│                          TextBlob NLP        ┌─────────────┐       │
│                          (Sentiment)         │ dashboard.py│       │
│                                              │  (Streamlit)│       │
│                                              └─────────────┘       │
│                                                    │               │
│                                                    ▼               │
│                                            analysis.ipynb          │
│                                           (Jupyter EDA Notebook)   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Key Findings

> ⚠️ Run the full pipeline first, then update these with your actual findings!

| Metric | Value |
|---|---|
| **Analysis Period** | 7 days (April 2026) |
| **Total Observations** | ~336 data points |
| **Price Range** | $XX,XXX — $XX,XXX |
| **Price Volatility (σ)** | $X,XXX |
| **Overall Sentiment** | Slightly Bullish (+0.XX) |
| **Sentiment-Price Correlation** | X.XX (weak/moderate/strong) |
| **Best Trading Hour (UTC)** | XX:00 |

---

## 🛠️ Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| **Language** | Python 3.9+ | Core development language |
| **Data Collection** | `requests` | HTTP calls to CoinGecko & RSS feeds |
| **NLP** | `TextBlob` | Sentiment analysis on news headlines |
| **Storage** | SQLite | Local relational database (no server needed) |
| **Data Manipulation** | `pandas` | DataFrames, SQL queries, aggregations |
| **Numerical Computing** | `numpy` | Statistics, rolling calculations, polyfit |
| **Static Charts** | `matplotlib`, `seaborn` | EDA charts in Jupyter notebook |
| **Interactive Charts** | `plotly` | Live charts in Streamlit dashboard |
| **Dashboard** | `streamlit` | Web dashboard (no HTML/JS needed!) |
| **Notebooks** | `jupyter`, `nbformat` | EDA notebook creation |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/project_pulse_point.git
cd project_pulse_point
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Install all dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up the database
```bash
python database_setup_v2.py
```

### 5. Seed sample data (7 days of realistic data)
```bash
python generate_sample_data.py
```

### 6. Launch the live dashboard
```bash
streamlit run dashboard.py
```
→ Opens in browser at `http://localhost:8501`

### 7. Open the analysis notebook
```bash
python create_notebook.py   # First: generates analysis.ipynb
jupyter notebook analysis.ipynb
```
→ Run all cells: `Kernel → Restart & Run All`

### 8. Start the live data pipeline (optional)
```bash
python tracker_v2.py
```
→ Runs indefinitely, adding real data every 5 minutes. Press `Ctrl+C` to stop.

---

## 📁 Project Structure

```
project_pulse_point/
│
├── 📄 tracker_v2.py           # Live ETL pipeline (collect → analyze → store)
├── 📄 dashboard.py            # Streamlit web dashboard
├── 📄 create_notebook.py      # Generates analysis.ipynb programmatically
├── 📓 analysis.ipynb          # Full EDA Jupyter notebook (5 sections, 5 charts)
│
├── 📄 database_setup_v2.py    # Database schema creation & migration
├── 📄 generate_sample_data.py # Seeds 7 days of realistic historical data
│
├── 📄 config.py               # Project configuration (API URLs, settings)
├── 📄 requirements.txt        # Python dependencies (pip install -r requirements.txt)
├── 📄 .gitignore              # Files excluded from Git
│
├── 🗄️ pulse_point.db          # SQLite database (auto-generated, not in Git)
└── 📜 pipeline.log            # Runtime log file (auto-generated, not in Git)
```

---

## 📓 Notebook Sections (analysis.ipynb)

| Section | Content |
|---|---|
| **1. Data Overview** | Load data, check quality, clean nulls, type conversion |
| **2. Feature Engineering** | Rolling averages, % changes, sentiment labels, datetime features |
| **3. Summary Statistics** | Mean, median, std dev, min/max for price and sentiment |
| **4. Price & Sentiment Trends** | 2 time series charts with moving average overlays |
| **5. Distribution Analysis** | Histograms — where do most values cluster? |
| **6. Correlation Analysis** | Scatter plot + heatmap: does sentiment predict price? |
| **7. Business Insights** | Plain-English findings report for non-technical stakeholders |

---

## 🔮 Future Improvements

- [ ] **Twitter/Reddit API** — richer, real-time social sentiment signals
- [ ] **Machine learning** — train a classifier to predict price direction from sentiment
- [ ] **Multi-asset tracking** — add Ethereum, Solana, BNB
- [ ] **Email/Telegram alerts** — notify when extreme sentiment is detected
- [ ] **PostgreSQL** — upgrade from SQLite to a production database
- [ ] **Docker containerization** — make the pipeline portable
- [ ] **Backtesting engine** — simulate trading based on the sentiment signal

---

## 👤 Author

**[Tanishq Singh]** — Aspiring Data Analyst


---

> *Built to demonstrate industry-ready Python data analytics skills:*
> *API integration, database management, NLP, EDA, statistical analysis & dashboarding.*
