import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Investment Recommendation System",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# STOCK LIST
# ============================================================

stocks = {
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "Reliance Industries": "RELIANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS"
}


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Investment Analysis")

selected_stock = st.sidebar.selectbox(
    "Select Stock",
    list(stocks.keys())
)

ticker = stocks[selected_stock]

st.sidebar.write(
    f"**Ticker:** {ticker}"
)

st.sidebar.write(
    "**Analysis Period:** 1 Year"
)

st.sidebar.write(
    "**Data Source:** Yahoo Finance"
)


# ============================================================
# LOAD STOCK DATA
# ============================================================

@st.cache_data
def load_stock_data(ticker):

    data = yf.download(
        ticker,
        period="1y",
        auto_adjust=True
    )

    # Handle yfinance multi-level columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    return data


data = load_stock_data(ticker)


# ============================================================
# CHECK DATA
# ============================================================

if data.empty:

    st.error(
        "Unable to download stock data."
    )

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

data["Date"] = pd.to_datetime(
    data["Date"]
)

data["Close"] = pd.to_numeric(
    data["Close"],
    errors="coerce"
)

data = data.dropna(
    subset=["Close"]
)


# ============================================================
# DAILY RETURN
# ============================================================

data["Daily_Return"] = (
    data["Close"].pct_change()
)


# ============================================================
# MOVING AVERAGES
# ============================================================

data["MA_20"] = (
    data["Close"]
    .rolling(window=20)
    .mean()
)

data["MA_50"] = (
    data["Close"]
    .rolling(window=50)
    .mean()
)


# ============================================================
# TOTAL RETURN
# ============================================================

starting_price = (
    data["Close"].iloc[0]
)

ending_price = (
    data["Close"].iloc[-1]
)

total_return = (
    (ending_price - starting_price)
    / starting_price
)


# ============================================================
# VOLATILITY
# ============================================================

valid_returns = (
    data["Daily_Return"]
    .dropna()
)

daily_volatility = (
    valid_returns.std()
)

annualized_volatility = (
    daily_volatility
    * np.sqrt(252)
)


# ============================================================
# MAXIMUM DRAWDOWN
# ============================================================

data["Running_Max"] = (
    data["Close"].cummax()
)

data["Drawdown"] = (
    (data["Close"] - data["Running_Max"])
    / data["Running_Max"]
)

maximum_drawdown = (
    data["Drawdown"].min()
)


# ============================================================
# TREND ANALYSIS
# ============================================================

data["Trend_Score"] = 0


# Positive trend
data.loc[
    (data["Close"] > data["MA_20"]) &
    (data["MA_20"] > data["MA_50"]),
    "Trend_Score"
] = 1


# Negative trend
data.loc[
    (data["Close"] < data["MA_20"]) &
    (data["MA_20"] < data["MA_50"]),
    "Trend_Score"
] = -1


# Latest trend score
trend_score = (
    data["Trend_Score"].iloc[-1]
)


# ============================================================
# RETURN SCORE
# ============================================================

if total_return > 0.10:

    return_score = 1

elif total_return < -0.10:

    return_score = -1

else:

    return_score = 0


# ============================================================
# VOLATILITY SCORE
# ============================================================

if annualized_volatility < 0.15:

    volatility_score = 1

elif annualized_volatility <= 0.25:

    volatility_score = 0

else:

    volatility_score = -1


# ============================================================
# DRAWDOWN SCORE
# ============================================================

if maximum_drawdown > -0.20:

    drawdown_score = 1

elif maximum_drawdown >= -0.30:

    drawdown_score = 0

else:

    drawdown_score = -1


# ============================================================
# RISK SCORE
# ============================================================

risk_score = (
    volatility_score
    + drawdown_score
)


# ============================================================
# NORMALIZED RISK SCORE
# ============================================================

normalized_risk_score = (
    risk_score / 2
)


# ============================================================
# INVESTMENT SCORE
# ============================================================

investment_score = (

    (return_score * 0.40)

    + (trend_score * 0.30)

    + (normalized_risk_score * 0.30)
)


# ============================================================
# RECOMMENDATION
# ============================================================

if investment_score >= 0.50:

    recommendation = "BUY"

elif investment_score <= -0.50:

    recommendation = "SELL"

else:

    recommendation = "HOLD"


# ============================================================
# PAGE TITLE
# ============================================================

st.title(
    "📊 Investment Recommendation System"
)

st.write(
    f"Financial analysis dashboard for "
    f"**{selected_stock}** ({ticker})."
)


# ============================================================
# INVESTMENT OVERVIEW
# ============================================================

st.subheader("📈 Investment Overview")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Current Price",
    f"₹{ending_price:,.2f}"
)


col2.metric(
    "Total Return",
    f"{total_return * 100:.2f}%"
)


col3.metric(
    "Annualized Volatility",
    f"{annualized_volatility * 100:.2f}%"
)


col4.metric(
    "Maximum Drawdown",
    f"{maximum_drawdown * 100:.2f}%"
)


# ============================================================
# PRICE TREND CHART
# ============================================================

st.subheader(
    f"📊 {selected_stock} Price Trend"
)


fig = go.Figure()


# Closing price
fig.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Close"],
        mode="lines",
        name="Closing Price"
    )
)


# 20-day moving average
fig.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["MA_20"],
        mode="lines",
        name="20-Day Moving Average"
    )
)


# 50-day moving average
fig.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["MA_50"],
        mode="lines",
        name="50-Day Moving Average"
    )
)


fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    width="stretch"
)


# ============================================================
# RISK ANALYSIS
# ============================================================

st.subheader("⚠️ Risk Analysis")


risk_col1, risk_col2, risk_col3 = st.columns(3)


risk_col1.metric(
    "Daily Volatility",
    f"{daily_volatility * 100:.2f}%"
)


risk_col2.metric(
    "Annualized Volatility",
    f"{annualized_volatility * 100:.2f}%"
)


risk_col3.metric(
    "Maximum Drawdown",
    f"{maximum_drawdown * 100:.2f}%"
)


# ============================================================
# INVESTMENT SCORE
# ============================================================

st.subheader(
    "🎯 Investment Score Analysis"
)


score_col1, score_col2, score_col3, score_col4 = st.columns(4)


score_col1.metric(
    "Return Score",
    return_score
)


score_col2.metric(
    "Trend Score",
    trend_score
)


score_col3.metric(
    "Risk Score",
    risk_score
)


score_col4.metric(
    "Investment Score",
    f"{investment_score:.2f}"
)


# ============================================================
# RECOMMENDATION
# ============================================================

st.subheader("💡 Recommendation")


st.metric(
    "System Recommendation",
    recommendation
)


st.write(
    "The recommendation is generated from the "
    "project's historical return, trend and risk "
    "scoring methodology."
)


# ============================================================
# WHY THIS RECOMMENDATION?
# ============================================================

st.subheader(
    "🔎 Recommendation Factors"
)


factor_col1, factor_col2, factor_col3 = st.columns(3)


factor_col1.write(
    f"**Historical Return**  \n"
    f"{total_return * 100:.2f}%  \n"
    f"Score: {return_score}"
)


factor_col2.write(
    f"**Trend**  \n"
    f"Trend Score: {trend_score}  \n"
    f"MA20: ₹{data['MA_20'].iloc[-1]:,.2f}  \n"
    f"MA50: ₹{data['MA_50'].iloc[-1]:,.2f}"
)


factor_col3.write(
    f"**Risk**  \n"
    f"Volatility Score: {volatility_score}  \n"
    f"Drawdown Score: {drawdown_score}  \n"
    f"Risk Score: {risk_score}"
)


# ============================================================
# DETAILED ANALYSIS
# ============================================================

st.subheader("📋 Detailed Analysis")


analysis_data = pd.DataFrame(
    {
        "Metric": [
            "Stock",
            "Ticker",
            "Starting Price",
            "Current Price",
            "Total Return",
            "Daily Volatility",
            "Annualized Volatility",
            "Maximum Drawdown",
            "Trend Score",
            "Return Score",
            "Volatility Score",
            "Drawdown Score",
            "Risk Score",
            "Normalized Risk Score",
            "Investment Score",
            "Recommendation"
        ],

        "Value": [
            selected_stock,
            ticker,
            f"₹{starting_price:,.2f}",
            f"₹{ending_price:,.2f}",
            f"{total_return * 100:.2f}%",
            f"{daily_volatility * 100:.2f}%",
            f"{annualized_volatility * 100:.2f}%",
            f"{maximum_drawdown * 100:.2f}%",
            trend_score,
            return_score,
            volatility_score,
            drawdown_score,
            risk_score,
            f"{normalized_risk_score:.2f}",
            f"{investment_score:.2f}",
            recommendation
        ]
    }
)


st.dataframe(
    analysis_data,
    width="stretch",
    hide_index=True
)


# ============================================================
# RECENT MARKET DATA
# ============================================================
# ============================================================
# RECENT MARKET DATA
# ============================================================

st.subheader("📅 Recent Market Data")

recent_data = data[
    [
        "Date",
        "Close",
        "MA_20",
        "MA_50",
        "Daily_Return"
    ]
].tail(10).copy()

# Format price columns
recent_data["Close"] = (
    recent_data["Close"].round(2)
)

recent_data["MA_20"] = (
    recent_data["MA_20"].round(2)
)

recent_data["MA_50"] = (
    recent_data["MA_50"].round(2)
)

# Convert daily return to percentage
recent_data["Daily_Return"] = (
    recent_data["Daily_Return"] * 100
).round(2)

recent_data["Daily_Return"] = (
    recent_data["Daily_Return"].astype(str) + "%"
)

st.dataframe(
    recent_data,
    width="stretch",
    hide_index=True
)

# ============================================================
# STOCK COMPARISON
# ============================================================

st.subheader("📊 Stock Comparison")

st.write(
    "Compare the selected stocks using the same "
    "return, risk and investment scoring methodology."
)


comparison_results = []


for stock_name, stock_ticker in stocks.items():

    try:

        stock_data = load_stock_data(stock_ticker)

        if stock_data.empty:
            continue

        # Handle multi-level columns
        if isinstance(
            stock_data.columns,
            pd.MultiIndex
        ):
            stock_data.columns = (
                stock_data.columns
                .get_level_values(0)
            )

        stock_data["Close"] = pd.to_numeric(
            stock_data["Close"],
            errors="coerce"
        )

        stock_data = stock_data.dropna(
            subset=["Close"]
        )

        # -----------------------------------------
        # Total Return
        # -----------------------------------------

        first_price = (
            stock_data["Close"].iloc[0]
        )

        last_price = (
            stock_data["Close"].iloc[-1]
        )

        stock_return = (
            (last_price - first_price)
            / first_price
        )

        # -----------------------------------------
        # Daily Return
        # -----------------------------------------

        stock_data["Daily_Return"] = (
            stock_data["Close"].pct_change()
        )

        valid_stock_returns = (
            stock_data["Daily_Return"]
            .dropna()
        )

        # -----------------------------------------
        # Annualized Volatility
        # -----------------------------------------

        stock_daily_volatility = (
            valid_stock_returns.std()
        )

        stock_annualized_volatility = (
            stock_daily_volatility
            * np.sqrt(252)
        )

        # -----------------------------------------
        # Maximum Drawdown
        # -----------------------------------------

        stock_data["Running_Max"] = (
            stock_data["Close"].cummax()
        )

        stock_data["Drawdown"] = (
            (
                stock_data["Close"]
                - stock_data["Running_Max"]
            )
            / stock_data["Running_Max"]
        )

        stock_max_drawdown = (
            stock_data["Drawdown"].min()
        )

        # -----------------------------------------
        # Moving Averages
        # -----------------------------------------

        stock_data["MA_20"] = (
            stock_data["Close"]
            .rolling(window=20)
            .mean()
        )

        stock_data["MA_50"] = (
            stock_data["Close"]
            .rolling(window=50)
            .mean()
        )

        # -----------------------------------------
        # Trend Score
        # -----------------------------------------

        stock_data["Trend_Score"] = 0

        stock_data.loc[
            (
                stock_data["Close"]
                > stock_data["MA_20"]
            )
            &
            (
                stock_data["MA_20"]
                > stock_data["MA_50"]
            ),
            "Trend_Score"
        ] = 1

        stock_data.loc[
            (
                stock_data["Close"]
                < stock_data["MA_20"]
            )
            &
            (
                stock_data["MA_20"]
                < stock_data["MA_50"]
            ),
            "Trend_Score"
        ] = -1

        stock_trend_score = (
            stock_data["Trend_Score"].iloc[-1]
        )

        # -----------------------------------------
        # Return Score
        # -----------------------------------------

        if stock_return > 0.10:

            stock_return_score = 1

        elif stock_return < -0.10:

            stock_return_score = -1

        else:

            stock_return_score = 0

        # -----------------------------------------
        # Volatility Score
        # -----------------------------------------

        if stock_annualized_volatility < 0.15:

            stock_volatility_score = 1

        elif stock_annualized_volatility <= 0.25:

            stock_volatility_score = 0

        else:

            stock_volatility_score = -1

        # -----------------------------------------
        # Drawdown Score
        # -----------------------------------------

        if stock_max_drawdown > -0.20:

            stock_drawdown_score = 1

        elif stock_max_drawdown >= -0.30:

            stock_drawdown_score = 0

        else:

            stock_drawdown_score = -1

        # -----------------------------------------
        # Risk Score
        # -----------------------------------------

        stock_risk_score = (
            stock_volatility_score
            + stock_drawdown_score
        )

        # -----------------------------------------
        # Normalized Risk Score
        # -----------------------------------------

        stock_normalized_risk = (
            stock_risk_score / 2
        )

        # -----------------------------------------
        # Investment Score
        # -----------------------------------------

        stock_investment_score = (

            (
                stock_return_score
                * 0.40
            )

            +

            (
                stock_trend_score
                * 0.30
            )

            +

            (
                stock_normalized_risk
                * 0.30
            )
        )

        # -----------------------------------------
        # Recommendation
        # -----------------------------------------

        if stock_investment_score >= 0.50:

            stock_recommendation = "BUY"

        elif stock_investment_score <= -0.50:

            stock_recommendation = "SELL"

        else:

            stock_recommendation = "HOLD"

        # -----------------------------------------
        # Store Results
        # -----------------------------------------

        comparison_results.append(
            {
                "Stock": stock_name,
                "Total Return": (
                    stock_return * 100
                ),
                "Annualized Volatility": (
                    stock_annualized_volatility
                    * 100
                ),
                "Maximum Drawdown": (
                    stock_max_drawdown
                    * 100
                ),
                "Trend Score": (
                    stock_trend_score
                ),
                "Risk Score": (
                    stock_risk_score
                ),
                "Investment Score": (
                    stock_investment_score
                ),
                "Recommendation": (
                    stock_recommendation
                )
            }
        )

    except Exception as error:

        st.warning(
            f"Unable to analyze "
            f"{stock_name}: {error}"
        )


# ============================================================
# DISPLAY COMPARISON
# ============================================================
# ============================================================
# DISPLAY COMPARISON
# ============================================================

if comparison_results:

    comparison_df = pd.DataFrame(
        comparison_results
    )

    # Create a copy for display formatting
    comparison_display = comparison_df.copy()

    # Format percentage columns
    comparison_display["Total Return"] = (
        comparison_display["Total Return"]
        .round(2)
        .astype(str)
        + "%"
    )

    comparison_display["Annualized Volatility"] = (
        comparison_display["Annualized Volatility"]
        .round(2)
        .astype(str)
        + "%"
    )

    comparison_display["Maximum Drawdown"] = (
        comparison_display["Maximum Drawdown"]
        .round(2)
        .astype(str)
        + "%"
    )

    # Format investment score
    comparison_display["Investment Score"] = (
        comparison_display["Investment Score"]
        .round(2)
    )

    # Display formatted comparison table
    st.dataframe(
        comparison_display,
        width="stretch",
        hide_index=True
    )

# ============================================================
# INVESTMENT SCORE COMPARISON CHART
# ============================================================

st.subheader("📊 Investment Score Comparison")

comparison_chart = go.Figure()

comparison_chart.add_trace(
    go.Bar(
        x=comparison_df["Stock"],
        y=comparison_df["Investment Score"],
        text=comparison_df["Investment Score"].round(2),
        textposition="auto",
        name="Investment Score"
    )
)

comparison_chart.update_layout(
    xaxis_title="Stock",
    yaxis_title="Investment Score",
    yaxis=dict(
        range=[-1, 1]
    )
)

st.plotly_chart(
    comparison_chart,
    width="stretch"
)
# ============================================================
# RETURN VS RISK CHART
# ============================================================

st.subheader("📈 Historical Return vs Risk")

risk_return_chart = go.Figure()

risk_return_chart.add_trace(
    go.Scatter(
        x=comparison_df["Annualized Volatility"],
        y=comparison_df["Total Return"],
        mode="markers+text",
        text=comparison_df["Stock"],
        textposition="top center",
        marker=dict(
            size=12
        ),
        name="Stocks"
    )
)

risk_return_chart.update_layout(
    xaxis_title="Annualized Volatility (%)",
    yaxis_title="Total Return (%)"
)

st.plotly_chart(
    risk_return_chart,
    width="stretch"
)
# ============================================================
# PORTFOLIO ANALYSIS
# ============================================================

st.subheader("💼 Portfolio Analysis")

st.write(
    "Create a portfolio by selecting stocks and assigning "
    "investment weights."
)


# Select stocks for portfolio
portfolio_stocks = st.multiselect(
    "Select stocks for your portfolio",
    list(stocks.keys()),
    default=[
        "TCS",
        "Infosys",
        "Reliance Industries"
    ]
)
# ============================================================
# PORTFOLIO WEIGHTS
# ============================================================

portfolio_weights = {}


if portfolio_stocks:

    st.write("### Assign Portfolio Weights")

    weight_columns = st.columns(
        len(portfolio_stocks)
    )

    for index, stock_name in enumerate(
        portfolio_stocks
    ):

        with weight_columns[index]:

            weight = st.number_input(
                f"{stock_name} (%)",
                min_value=0.0,
                max_value=100.0,
                value=(
                    100.0
                    / len(portfolio_stocks)
                ),
                step=5.0
            )

            portfolio_weights[
                stock_name
            ] = weight

# ============================================================
# VALIDATE PORTFOLIO WEIGHTS
# ============================================================

if portfolio_stocks:

    total_weight = sum(
        portfolio_weights.values()
    )

    st.write(
        f"**Total Portfolio Weight: "
        f"{total_weight:.2f}%**"
    )

    if abs(total_weight - 100) > 0.01:

        st.warning(
            "Portfolio weights should add up to 100%."
        )

    else:

        st.success(
            "Portfolio weights are valid."
        )
# ============================================================
# PORTFOLIO DATA
# ============================================================

if portfolio_stocks and abs(total_weight - 100) <= 0.01:

    portfolio_prices = pd.DataFrame()

    for stock_name in portfolio_stocks:

        stock_ticker = stocks[stock_name]

        stock_data = load_stock_data(
            stock_ticker
        )

        if stock_data.empty:
            continue

        if isinstance(
            stock_data.columns,
            pd.MultiIndex
        ):

            stock_data.columns = (
                stock_data.columns
                .get_level_values(0)
            )

        stock_data["Date"] = pd.to_datetime(
            stock_data["Date"]
        )

        stock_data["Close"] = pd.to_numeric(
            stock_data["Close"],
            errors="coerce"
        )

        stock_data = stock_data.dropna(
            subset=["Close"]
        )

        stock_prices = stock_data[
            [
                "Date",
                "Close"
            ]
        ].copy()

        stock_prices = stock_prices.rename(
            columns={
                "Close": stock_name
            }
        )

        stock_prices = stock_prices.set_index(
            "Date"
        )

        if portfolio_prices.empty:

            portfolio_prices = stock_prices

        else:

            portfolio_prices = (
                portfolio_prices.join(
                    stock_prices,
                    how="inner"
                )
            )
# ============================================================
# PORTFOLIO DAILY RETURNS
# ============================================================

    portfolio_stock_returns = (
        portfolio_prices.pct_change()
        .dropna()
    )
# ============================================================
# CALCULATE WEIGHTED PORTFOLIO RETURNS
# ============================================================

    weights = pd.Series(
        {
            stock_name:
            portfolio_weights[stock_name] / 100
            for stock_name in portfolio_stocks
        }
    )

    portfolio_daily_returns = (
        portfolio_stock_returns
        .mul(weights)
        .sum(axis=1)
    )
# ============================================================
# PORTFOLIO PERFORMANCE
# ============================================================

    portfolio_cumulative_value = (
        1 + portfolio_daily_returns
    ).cumprod()

    portfolio_total_return = (
        portfolio_cumulative_value.iloc[-1]
        - 1
    )
# ============================================================
# PORTFOLIO VOLATILITY
# ============================================================

    portfolio_daily_volatility = (
        portfolio_daily_returns.std()
    )

    portfolio_annualized_volatility = (
        portfolio_daily_volatility
        * np.sqrt(252)
    )
# ============================================================
# PORTFOLIO MAXIMUM DRAWDOWN
# ============================================================

    portfolio_running_max = (
        portfolio_cumulative_value.cummax()
    )

    portfolio_drawdown = (
        (
            portfolio_cumulative_value
            - portfolio_running_max
        )
        / portfolio_running_max
    )

    portfolio_max_drawdown = (
        portfolio_drawdown.min()
    )
# ============================================================
# DISPLAY PORTFOLIO METRICS
# ============================================================

    st.subheader(
        "💼 Portfolio Performance"
    )

    portfolio_col1, portfolio_col2, portfolio_col3 = (
        st.columns(3)
    )

    portfolio_col1.metric(
        "Portfolio Return",
        f"{portfolio_total_return * 100:.2f}%"
    )

    portfolio_col2.metric(
        "Annualized Volatility",
        f"{portfolio_annualized_volatility * 100:.2f}%"
    )

    portfolio_col3.metric(
        "Maximum Drawdown",
        f"{portfolio_max_drawdown * 100:.2f}%"
    )
# ============================================================
# PORTFOLIO PERFORMANCE CHART
# ============================================================

    st.subheader(
        "📈 Portfolio Growth"
    )

    portfolio_chart = go.Figure()

    portfolio_chart.add_trace(
        go.Scatter(
            x=portfolio_cumulative_value.index,
            y=portfolio_cumulative_value * 100,
            mode="lines",
            name="Portfolio Value"
        )
    )

    portfolio_chart.update_layout(
        xaxis_title="Date",
        yaxis_title="Portfolio Value Index"
    )

    st.plotly_chart(
        portfolio_chart,
        width="stretch"
    )
# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Investment Recommendation System | "
    "Finance Capstone Project"
)