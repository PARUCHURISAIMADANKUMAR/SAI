# Investment Recommendation System

## Finance Capstone Project

A Python and Streamlit based finance analytics application for analyzing historical stock performance, investment risk and return, stock comparison, portfolio performance, and project-defined investment recommendations.

### Author
**PARUCHURI SAI MADAN KUMAR**  
Roll No.: 25914050399  
MBA Finance | K. L University  
Academic Year 2026

## Project Overview

The system collects historical market data from Yahoo Finance and analyzes selected stocks using return, trend and risk metrics. Results are presented through an interactive Streamlit dashboard.

### Stocks Covered

- TCS
- Infosys
- Reliance Industries
- HDFC Bank
- ICICI Bank

### Key Features

- Historical price trend visualization
- Total return calculation
- Daily and annualized volatility
- Maximum drawdown
- 20-day and 50-day moving averages
- Investment scoring
- BUY / HOLD / SELL classification
- Detailed stock analysis
- Stock comparison
- Historical return vs risk visualization
- Portfolio construction with user-defined weights
- Portfolio return, volatility and drawdown
- Portfolio growth chart
- Downloadable investment report

## Recommendation Methodology

The project uses a defined academic scoring methodology:

**Return Score**
- Return > 10% → +1
- Return < -10% → -1
- Otherwise → 0

**Volatility Score**
- Annualized volatility < 15% → +1
- 15%–25% → 0
- > 25% → -1

**Drawdown Score**
- Maximum drawdown > -20% → +1
- -20% to -30% → 0
- < -30% → -1

**Investment Score**

`0.40 × Return Score + 0.30 × Trend Score + 0.30 × Normalized Risk Score`

**Recommendation**
- Score ≥ 0.50 → BUY
- Score ≤ -0.50 → SELL
- Otherwise → HOLD

These weights and thresholds are project-defined rules for academic analysis and are not presented as universal investment advice.

## Technology Stack

- Python
- Pandas
- NumPy
- yfinance
- Plotly
- Streamlit
- Matplotlib
- OpenPyXL

## Data Source

Historical market data is retrieved using Yahoo Finance through the `yfinance` Python library.

## Project Structure

```text
Investment-Recommendation-System/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── reports/
├── src/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/PARUCHURISAIMADANKUMAR/SAI.git
cd SAI
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

## Academic Scope

The project is designed for finance analytics and academic demonstration. It does not execute trades, connect to a brokerage account, or guarantee future market performance.

## Limitations

- Uses historical market data.
- Historical performance does not guarantee future returns.
- Recommendation thresholds are project-defined.
- Advanced quantitative finance and machine-learning prediction are outside the current implementation.

## Future Scope

- Additional asset classes
- Machine-learning based analysis
- Real-time alerts
- Portfolio optimization
- Online deployment
- Expanded financial indicators and reporting

## Disclaimer

This project is for academic and analytical purposes only. It is not financial advice and should not be used as a standalone basis for investment decisions.
