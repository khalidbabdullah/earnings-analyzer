import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PAGE SETUP ---
st.set_page_config(page_title="Earnings Analyzer", layout="wide")
st.title("📊 Automated Earnings Analyzer")
st.markdown("Enter a ticker to analyze the last 8 quarters of earnings performance.")

# --- INPUT ---
ticker = st.text_input("Ticker Symbol", value="NFLX").upper().strip()

@st.cache_data
def get_financials(ticker):
    stock = yf.Ticker(ticker)
    income = stock.quarterly_financials.T
    cashflow = stock.quarterly_cashflow.T
    info = stock.info
    try:
        eps = stock.earnings_dates
    except Exception:
        eps = None
    return income, cashflow, info, eps

if ticker:
    with st.spinner(f"Pulling data for {ticker}..."):
        income, cashflow, info, eps = get_financials(ticker)

    # --- CLEAN DATA ---
    income.index = pd.to_datetime(income.index)
    income = income.sort_index().tail(8)

    cashflow.index = pd.to_datetime(cashflow.index)
    cashflow = cashflow.sort_index().tail(8)

    # Extract key metrics
    revenue = income.get("Total Revenue", pd.Series())
    net_income = income.get("Net Income", pd.Series())
    gross_profit = income.get("Gross Profit", pd.Series())

    # --- COMPANY HEADER ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Company", info.get("shortName", ticker))
    col2.metric("Sector", info.get("sector", "N/A"))
    col3.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B")

    st.divider()

    # --- REVENUE ---
    st.subheader("📈 Quarterly Revenue")
    if not revenue.empty:
        rev_billions = revenue / 1e9
        qoq = revenue.pct_change() * 100
        yoy = revenue.pct_change(4) * 100

        fig_rev = go.Figure()
        fig_rev.add_trace(go.Bar(
            x=[str(d.date()) for d in rev_billions.index],
            y=rev_billions.values,
            marker_color=["#00C49F" if v >= 0 else "#FF4B4B" for v in qoq.fillna(0)],
            text=[f"${v:.1f}B" for v in rev_billions.values],
            textposition="outside"
        ))
        fig_rev.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="Revenue (Billions)", range=[0, rev_billions.max() * 1.2]),
            xaxis=dict(type="category"),
            showlegend=False,
            height=350
        )
        st.plotly_chart(fig_rev, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("Latest QoQ Growth", f"{qoq.iloc[-1]:.1f}%" if not pd.isna(qoq.iloc[-1]) else "N/A")
        col2.metric("Latest YoY Growth", f"{yoy.iloc[-1]:.1f}%" if not pd.isna(yoy.iloc[-1]) else "N/A")

        # --- VALUATION METRICS ---
        st.subheader("📐 Valuation Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.1f}x" if isinstance(info.get('trailingPE'), float) else "N/A")
        col2.metric("Forward P/E", f"{info.get('forwardPE', 'N/A'):.1f}x" if isinstance(info.get('forwardPE'), float) else "N/A")
        col3.metric("EV/EBITDA", f"{info.get('enterpriseToEbitda', 'N/A'):.1f}x" if isinstance(info.get('enterpriseToEbitda'), float) else "N/A")
        col4.metric("Price/Sales", f"{info.get('priceToSalesTrailing12Months', 'N/A'):.1f}x" if isinstance(info.get('priceToSalesTrailing12Months'), float) else "N/A")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
        col2.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
        col3.metric("52W Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}")
        col4.metric("Analyst Target", f"${info.get('targetMeanPrice', 0):.2f}")

    st.divider()

    # --- NET INCOME & MARGIN ---
    st.subheader("💰 Net Income & Profit Margin")
    if not net_income.empty and not revenue.empty:
        margin = (net_income / revenue) * 100

        fig_ni = go.Figure()
        fig_ni.add_trace(go.Bar(
            x=[str(d.date()) for d in net_income.index],
            y=net_income.values / 1e9,
            marker_color="#636EFA",
            text=[f"${v:.1f}B" for v in net_income.values / 1e9],
            textposition="outside"
        ))
        fig_ni.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="Net Income ($B)", range=[0, (net_income.max() / 1e9) * 1.2]),
            xaxis=dict(type="category"),
            height=320,
            showlegend=False
        )
        st.plotly_chart(fig_ni, use_container_width=True)

        fig_margin = go.Figure()
        fig_margin.add_trace(go.Scatter(
            x=[str(d.date()) for d in margin.index],
            y=margin.values,
            mode="lines+markers",
            line=dict(color="#FFA15A", width=2),
            marker=dict(size=7),
            text=[f"{v:.1f}%" for v in margin.values],
            textposition="top center"
        ))
        fig_margin.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="Net Margin (%)"),
            xaxis=dict(type="category"),
            height=280,
            showlegend=False
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    st.divider()

    # --- FREE CASH FLOW ---
    st.subheader("💵 Free Cash Flow")
    try:
        operating_cf = cashflow.get("Operating Cash Flow", pd.Series())
        capex = cashflow.get("Capital Expenditure", pd.Series())

        if not operating_cf.empty and not capex.empty:
            fcf = operating_cf + capex
            fcf_billions = fcf / 1e9

            fig_fcf = go.Figure()
            fig_fcf.add_trace(go.Bar(
                x=[str(d.date()) for d in fcf.index],
                y=fcf_billions.values,
                marker_color=["#00C49F" if v >= 0 else "#FF4B4B" for v in fcf_billions],
                text=[f"${v:.1f}B" if not pd.isna(v) else "" for v in fcf_billions.values],
                textposition="outside"
            ))
            fig_fcf.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title="FCF (Billions)", range=[min(fcf_billions.min() * 1.3, 0), fcf_billions.max() * 1.3]),
                xaxis=dict(type="category"),
                height=320,
                showlegend=False
            )
            st.plotly_chart(fig_fcf, use_container_width=True)

            col1, col2 = st.columns(2)
            col1.metric("Latest FCF", f"${fcf_billions.iloc[-1]:.1f}B")
            col2.metric("FCF Margin", f"{(fcf.iloc[-1] / revenue.iloc[-1] * 100):.1f}%" if not revenue.empty else "N/A")
    except Exception as e:
        st.info("Free cash flow data not available.")

    st.divider()

    # --- EPS BEAT/MISS ---
    st.subheader("🎯 EPS: Actual vs Estimate")
    if eps is not None and not eps.empty:
        eps_clean = eps[["EPS Estimate", "Reported EPS"]].dropna()
        eps_clean = eps_clean[eps_clean.index <= pd.Timestamp.now(tz=eps_clean.index.tz)]
        eps_clean = eps_clean.sort_index().tail(5)
        eps_clean.index = eps_clean.index.tz_localize(None)
        eps_clean["Beat"] = eps_clean["Reported EPS"] >= eps_clean["EPS Estimate"]
        eps_clean["Surprise %"] = ((eps_clean["Reported EPS"] - eps_clean["EPS Estimate"]) / eps_clean["EPS Estimate"].abs()) * 100

        fig_eps = go.Figure()
        fig_eps.add_trace(go.Bar(
            x=[str(d.date()) for d in eps_clean.index],
            y=eps_clean["EPS Estimate"],
            name="EPS Estimate",
            marker_color="#A0A0A0"
        ))
        fig_eps.add_trace(go.Bar(
            x=[str(d.date()) for d in eps_clean.index],
            y=eps_clean["Reported EPS"],
            name="Reported EPS",
            marker_color=["#00C49F" if b else "#FF4B4B" for b in eps_clean["Beat"]]
        ))
        fig_eps.update_layout(
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(type="category"),
            height=350,
            legend=dict(orientation="h")
        )
        st.plotly_chart(fig_eps, use_container_width=True)

        beats = eps_clean["Beat"].sum()
        total = len(eps_clean)
        st.metric("Beat Rate", f"{beats}/{total} quarters ({beats/total*100:.0f}%)")
        st.dataframe(eps_clean[["EPS Estimate", "Reported EPS", "Surprise %"]].style.format("{:.2f}"))
    else:
        st.info("EPS beat/miss data not available for this ticker.")

    st.divider()

    # --- SUMMARY TABLE ---
    st.subheader("📋 Quarterly Summary")
    summary = pd.DataFrame({
        "Revenue ($B)": (revenue / 1e9).round(2),
        "Net Income ($B)": (net_income / 1e9).round(2),
        "Gross Profit ($B)": (gross_profit / 1e9).round(2),
        "Net Margin (%)": ((net_income / revenue) * 100).round(1)
    })
    summary.index = [str(d.date()) for d in summary.index]
    st.dataframe(summary)
