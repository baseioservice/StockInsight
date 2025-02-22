import streamlit as st
import plotly.graph_objects as go
from utils import (
    is_indian_market_open, 
    get_stock_data, 
    prepare_summary_data, 
    get_nse_indices,
    generate_portfolio_snapshot
)
import pandas as pd
import datetime

# Page config
st.set_page_config(
    page_title="Indian Stock Market Tracker",
    page_icon="📈",
    layout="wide"
)

# Force clear cache and session state
st.cache_data.clear()
if 'last_symbol' in st.session_state:
    del st.session_state['last_symbol']

# Title and description
st.title("📈 Indian Stock Market Tracker")
st.markdown("""
    Track NSE and BSE stocks with real-time data and interactive charts.
    Enter a stock symbol (e.g., 'GAIL' or 'TCS' for NSE, add '.BO' for BSE stocks)
""")

# Market status
is_open, market_status = is_indian_market_open()
status_color = "green" if is_open else "red"
st.markdown(
    f"""
    <div style='background-color: {'#E8F5E9' if is_open else '#FFEBEE'}; padding: 10px; border-radius: 5px;'>
        <h3 style='color: {status_color}; margin: 0;'>📊 {market_status}</h3>
        {'' if is_open else '<p style="margin: 5px 0 0 0; color: #666;">Showing last available market data</p>'}
    </div>
    """,
    unsafe_allow_html=True
)

# NSE Indices Section
st.subheader("📊 NSE Indices")
indices_data = get_nse_indices()

# Create two columns for Nifty 50 and Bank Nifty
nifty_col, banknifty_col = st.columns(2)

# Display Nifty 50
with nifty_col:
    hist_data, info, message = indices_data['NIFTY 50']
    if message == "success":
        st.subheader("NIFTY 50")
        current_price = info.get('regularMarketPrice', 'N/A')
        prev_close = info.get('regularMarketPreviousClose', 'N/A')
        change = current_price - prev_close if isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)) else 0
        change_percent = (change / prev_close * 100) if prev_close else 0

        # Display current value and change
        st.metric(
            "Current Value",
            f"₹{current_price:,.2f}",
            f"{change:,.2f} ({change_percent:.2f}%)",
            delta_color="normal" if change >= 0 else "inverse"
        )

        # Nifty 50 Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data['Close'],
            name='NIFTY 50',
            line=dict(color='blue', width=1)
        ))

        fig.update_layout(
            title="NIFTY 50 Historical Trend",
            yaxis_title="Value",
            xaxis_title="Date",
            template="plotly_white",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Error loading NIFTY 50 data: {message}")

# Display Bank Nifty
with banknifty_col:
    hist_data, info, message = indices_data['BANK NIFTY']
    if message == "success":
        st.subheader("BANK NIFTY")
        current_price = info.get('regularMarketPrice', 'N/A')
        prev_close = info.get('regularMarketPreviousClose', 'N/A')
        change = current_price - prev_close if isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)) else 0
        change_percent = (change / prev_close * 100) if prev_close else 0

        # Display current value and change
        st.metric(
            "Current Value",
            f"₹{current_price:,.2f}",
            f"{change:,.2f} ({change_percent:.2f}%)",
            delta_color="normal" if change >= 0 else "inverse"
        )

        # Bank Nifty Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data['Close'],
            name='BANK NIFTY',
            line=dict(color='green', width=1)
        ))

        fig.update_layout(
            title="BANK NIFTY Historical Trend",
            yaxis_title="Value",
            xaxis_title="Date",
            template="plotly_white",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Error loading BANK NIFTY data: {message}")

# Stock input
st.subheader("🔍 Stock Search")
symbol = st.text_input(
    "Enter Stock Symbol:",
    help="Enter stock symbol (e.g., 'TCS' or 'tcs'). Case-insensitive.",
    key="stock_input"
)

if symbol:
    with st.spinner(f'Fetching data for {symbol}...'):
        hist_data, info, message = get_stock_data(symbol)

        if message != "success":
            st.error(message)
        else:
            try:
                # Display basic info
                company_name = info.get('longName', symbol)
                st.subheader(f"{company_name} ({symbol.upper()})")

                # Display summary table
                st.subheader("Stock Summary")
                if not is_open:
                    st.info("Note: Data shown is from the last market close")
                summary_df = prepare_summary_data(info)
                st.table(summary_df)

                # Technical Indicators section
                st.subheader("Technical Indicators")
                col1, col2 = st.columns(2)

                # Moving Average controls
                with col1:
                    st.subheader("Moving Averages")
                    show_ma20 = st.checkbox("20-day MA", value=True)
                    show_ma50 = st.checkbox("50-day MA", value=True)
                    show_ma200 = st.checkbox("200-day MA")

                # RSI controls
                with col2:
                    st.subheader("RSI")
                    show_rsi = st.checkbox("Show RSI", value=True)
                    rsi_period = st.slider("RSI Period", min_value=7, max_value=30, value=14)

                # Interactive price chart
                st.subheader("Price History")
                fig = go.Figure()

                # Main candlestick chart
                fig.add_trace(
                    go.Candlestick(
                        x=hist_data.index,
                        open=hist_data['Open'],
                        high=hist_data['High'],
                        low=hist_data['Low'],
                        close=hist_data['Close'],
                        name='OHLC'
                    )
                )

                # Add Moving Averages
                if show_ma20:
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['MA20'],
                        name='MA20',
                        line=dict(color='blue', width=1)
                    ))

                if show_ma50:
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['MA50'],
                        name='MA50',
                        line=dict(color='orange', width=1)
                    ))

                if show_ma200:
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['MA200'],
                        name='MA200',
                        line=dict(color='red', width=1)
                    ))

                fig.update_layout(
                    title=f"{symbol} Stock Price",
                    yaxis_title="Price (₹)",
                    xaxis_title="Date",
                    template="plotly_white",
                    height=600,
                    xaxis_rangeslider_visible=False
                )

                st.plotly_chart(fig, use_container_width=True)

                # RSI Chart
                if show_rsi:
                    rsi_fig = go.Figure()
                    rsi_fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['RSI'],
                        name='RSI',
                        line=dict(color='purple', width=1)
                    ))

                    # Add overbought/oversold lines
                    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")

                    rsi_fig.update_layout(
                        title="Relative Strength Index (RSI)",
                        yaxis_title="RSI",
                        xaxis_title="Date",
                        template="plotly_white",
                        height=300,
                        yaxis=dict(range=[0, 100])
                    )

                    st.plotly_chart(rsi_fig, use_container_width=True)

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    # Download button for summary
                    csv = summary_df.to_csv(index=False)
                    st.download_button(
                        label="Download Summary CSV",
                        data=csv,
                        file_name=f"{symbol}_summary.csv",
                        mime="text/csv"
                    )

                with col2:
                    # Download button for historical data
                    csv_hist = hist_data.to_csv()
                    st.download_button(
                        label="Download Historical Data CSV",
                        data=csv_hist,
                        file_name=f"{symbol}_historical.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Error displaying data: {str(e)}")
else:
    st.info("Please enter a stock symbol to view data")


# Portfolio Snapshot Section
st.subheader("📊 Portfolio Snapshot Generator")
st.markdown("""
    Generate a quick snapshot of your portfolio performance.
    Enter stock symbols separated by commas (e.g., TCS, INFY, RELIANCE or tcs, infy, reliance). Case-insensitive.
""")

portfolio_input = st.text_input(
    "Enter Portfolio Symbols:",
    help="Enter multiple stock symbols separated by commas (case-insensitive)",
    key="portfolio_input"
)

if st.button("Generate Portfolio Snapshot", key="generate_snapshot"):
    if not portfolio_input:
        st.warning("Please enter at least one stock symbol")
    else:
        with st.spinner("Generating portfolio snapshot..."):
            # Process symbols
            symbols = [sym.strip() for sym in portfolio_input.split(',')]

            # Generate snapshot
            portfolio_df, summary, message = generate_portfolio_snapshot(symbols)

            if message != "success":
                st.error(message)
            else:
                # Display summary metrics
                st.subheader("Portfolio Summary")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Total Portfolio Value",
                        f"₹{summary['Total Value']:,.2f}",
                        f"{summary['Total Change']:,.2f} ({summary['Total Change %']:.2f}%)",
                        delta_color="normal" if summary['Total Change'] >= 0 else "inverse"
                    )

                with col2:
                    st.metric("Best Performer", summary['Best Performer'])

                with col3:
                    st.metric("Worst Performer", summary['Worst Performer'])

                # Display timestamp
                st.caption(f"Last Updated: {summary['Timestamp']}")

                # Display portfolio table
                st.subheader("Portfolio Details")
                st.dataframe(
                    portfolio_df,
                    column_config={
                        "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
                        "Current Price": st.column_config.TextColumn("Current Price", width="medium"),
                        "Change": st.column_config.TextColumn("Change", width="medium"),
                        "Change %": st.column_config.TextColumn("Change %", width="medium"),
                        "52W High": st.column_config.TextColumn("52W High", width="medium"),
                        "52W Low": st.column_config.TextColumn("52W Low", width="medium"),
                        "Distance from 52W High %": st.column_config.TextColumn("Distance from 52W High", width="medium"),
                        "Distance from 52W Low %": st.column_config.TextColumn("Distance from 52W Low", width="medium")
                    },
                    hide_index=True
                )

                # Download button for portfolio data
                csv = portfolio_df.to_csv(index=False)
                st.download_button(
                    label="Download Portfolio Snapshot",
                    data=csv,
                    file_name=f"portfolio_snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Footer
st.markdown("""
---
Data provided by Yahoo Finance. Updated during market hours (9:15 AM - 3:30 PM IST, Mon-Fri).
""")