import streamlit as st
import plotly.graph_objects as go
from utils import (
    generate_portfolio_snapshot
)
import pandas as pd
import datetime

def show():
    #st.title("Stock Insight")
    pagecontent()

def pagecontent():
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
                process_symbols(symbols)

                # # Generate snapshot
                # portfolio_df, summary, message = generate_portfolio_snapshot(symbols)

                # if message != "success":
                #     st.error(message)
                # else:
                #     # Display summary metrics
                #     st.subheader("Portfolio Summary")
                #     col1, col2, col3 = st.columns(3)

                #     with col1:
                #         st.metric(
                #             "Total Portfolio Value",
                #             f"₹{summary['Total Value']:,.2f}",
                #             f"{summary['Total Change']:,.2f} ({summary['Total Change %']:.2f}%)",
                #             delta_color="normal" if summary['Total Change'] >= 0 else "inverse"
                #         )

                #     with col2:
                #         st.metric("Best Performer", summary['Best Performer'])

                #     with col3:
                #         st.metric("Worst Performer", summary['Worst Performer'])

                #     # Display timestamp
                #     st.caption(f"Last Updated: {summary['Timestamp']}")

                #     # Display invalid symbols if any
                #     if 'Invalid Symbols' in summary and summary['Invalid Symbols']:
                #         st.warning(f"Unable to fetch data for the following symbols: {', '.join(summary['Invalid Symbols'])}")

                #     # Display portfolio table
                #     st.subheader("Portfolio Details")
                #     st.dataframe(
                #         portfolio_df,
                #         column_config={
                #             "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
                #             "Current Price": st.column_config.TextColumn("Current Price", width="medium"),
                #             "Change": st.column_config.TextColumn("Change", width="medium"),
                #             "Change %": st.column_config.TextColumn("Change %", width="medium"),
                #             "52W High": st.column_config.TextColumn("52W High", width="medium"),
                #             "52W Low": st.column_config.TextColumn("52W Low", width="medium"),
                #             "Distance from 52W High %": st.column_config.TextColumn("Distance from 52W High", width="medium"),
                #             "Distance from 52W Low %": st.column_config.TextColumn("Distance from 52W Low", width="medium")
                #         },
                #         hide_index=True
                #     )

                #     # Download button for portfolio data
                #     csv = portfolio_df.to_csv(index=False)
                #     st.download_button(
                #         label="Download Portfolio Snapshot",
                #         data=csv,
                #         file_name=f"portfolio_snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                #         mime="text/csv"
                #     )

def process_symbols(symbols):
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

        # Display invalid symbols if any
        if 'Invalid Symbols' in summary and summary['Invalid Symbols']:
            st.warning(f"Unable to fetch data for the following symbols: {', '.join(summary['Invalid Symbols'])}")

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