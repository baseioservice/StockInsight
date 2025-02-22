import streamlit as st
import plotly.graph_objects as go
from utils import is_indian_market_open, get_stock_data, prepare_summary_data
import pandas as pd

# Page config
st.set_page_config(
    page_title="Indian Stock Market Tracker",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Indian Stock Market Tracker")
st.markdown("""
    Track NSE and BSE stocks with real-time data and interactive charts.
    Enter a stock symbol (e.g., 'RELIANCE' or 'TCS' for NSE, add '.BO' for BSE stocks)
""")

# Market status
is_open, market_status = is_indian_market_open()
status_color = "green" if is_open else "red"
st.markdown(f"<h3 style='color: {status_color};'>Market Status: {market_status}</h3>", unsafe_allow_html=True)

# Stock input
symbol = st.text_input("Enter Stock Symbol:", value="RELIANCE").upper()

if symbol:
    with st.spinner('Fetching data...'):
        hist_data, info, message = get_stock_data(symbol)
        
        if message != "success":
            st.error(message)
        else:
            # Display summary table
            st.subheader("Stock Summary")
            summary_df = prepare_summary_data(info)
            st.table(summary_df)
            
            # Download button for summary
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download Summary CSV",
                data=csv,
                file_name=f"{symbol}_summary.csv",
                mime="text/csv"
            )
            
            # Interactive price chart
            st.subheader("Price History")
            fig = go.Figure()
            
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
            
            fig.update_layout(
                title=f"{symbol} Stock Price",
                yaxis_title="Price (₹)",
                xaxis_title="Date",
                template="plotly_white",
                height=600,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Download button for historical data
            csv_hist = hist_data.to_csv()
            st.download_button(
                label="Download Historical Data CSV",
                data=csv_hist,
                file_name=f"{symbol}_historical.csv",
                mime="text/csv"
            )

# Footer
st.markdown("""
---
Data provided by Yahoo Finance. Updated during market hours (9:15 AM - 3:30 PM IST, Mon-Fri).
""")
