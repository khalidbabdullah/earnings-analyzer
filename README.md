# 📊 Automated Earnings Analyzer

> 🚧 **Under Construction** — actively being developed. Core dashboard is live.

An interactive Streamlit web app that pulls live financial data for any publicly traded company and generates a full earnings analysis dashboard automatically.

## 🔴 [Live App](https://earnings-analyzer-khalid.streamlit.app)

## What It Does

Enter any ticker symbol and the app instantly pulls and analyzes:

- **Quarterly Revenue** — with QoQ and YoY growth rates
- **Valuation Metrics** — P/E, Forward P/E, EV/EBITDA, Price/Sales, 52-week range, analyst price target
- **Net Income & Profit Margin** — trend across recent quarters
- **Free Cash Flow** — with FCF margin calculation
- **EPS Beat/Miss** — actual vs analyst estimate with beat rate and surprise %
- **Quarterly Summary Table** — revenue, net income, gross profit, net margin

## Stack

- Python, Streamlit, yfinance, Pandas, Plotly

## Roadmap

- [ ] Revenue beat/miss history
- [ ] Peer comparison across sector
- [ ] Automated narrative summary
- [ ] DCF valuation integration
