import streamlit as st
import plotly.graph_objects as go
from utils import (
    generate_portfolio_snapshot
)
import pandas as pd
import datetime
from datetime import datetime as dt

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

    # Some defaults
    symbols=["COALINDIA", "GABRIEL", "GAIL", "GSPL", "HINDUNILVR", "IRCTC", "IDBI", "IOC", "KARURVYSYA","KFINTECH", "LTF", "ONGC", "MARICO", "NTPC", "PNBGILTS", "TATACOMM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "WELSPUNLIV", "WIPRO" ]

    # Initialize dictionary with dummy values
    stock_data = {
        'COALINDIA': {
            "avg_purchase_price": 199.14,  
            "last_purchase_price": 202.85,  
            "last_purchase_date": '2022-08-16' 
        },
        'GABRIEL': {
            "avg_purchase_price": 20,  
            "last_purchase_price": 20,  
            "last_purchase_date": '2012-07-19' 
        },
        'GAIL': {
            "avg_purchase_price": 124.96,  
            "last_purchase_price": 146.20,  
            "last_purchase_date": '2022-03-23' 
        },
        'GSPL': {
            "avg_purchase_price": 220.00,  
            "last_purchase_price":220.00,
            "last_purchase_date": '2022-09-10' 
        },
        'HINDUNILVR': {
            "avg_purchase_price": 220,  
            "last_purchase_price": 220,
            "last_purchase_date": '2007-10-16' 
        },
        'IRCTC': {
            "avg_purchase_price": 773.55,  
            "last_purchase_price": 773.55,
            "last_purchase_date": '2022-03-22' 
        },
        'IDBI': {
           "avg_purchase_price": 61.61,  
           "last_purchase_price": 74,
            "last_purchase_date": '2025-02-20' 
        },
        'IOC': {
            "avg_purchase_price": 125.20,  
            "last_purchase_price": 125.20,
            "last_purchase_date": '2025-01-14' 
        },
        'KARURVYSYA': {
            "avg_purchase_price": 72,  
            "last_purchase_price": 94,
            "last_purchase_date": '2022-11-10' 
        },
        'KFINTECH': {
            "avg_purchase_price": 912,  
            "last_purchase_price": 912,
            "last_purchase_date": '2025-03-12' 
        },
        'LTF': {
            "avg_purchase_price": 90.03,  
            "last_purchase_price": 124.60,
            "last_purchase_date": '2023-08-30' 
        },
        'OLAELEC': {
           "avg_purchase_price": 61.30,  
           "last_purchase_price": 61.30,
            "last_purchase_date": '2025-02-20' 
        },
        'ONGC': {
            "avg_purchase_price": 138.16,  
            "last_purchase_price": 138.16,
            "last_purchase_date": '2022-08-16' 
        },
        'MARICO': {
            "avg_purchase_price": 503.41,  
            "last_purchase_price": 503.41,
            "last_purchase_date": '2022-11-14' 
        },
        'NTPC': {
            "avg_purchase_price": 159.66,
            "last_purchase_price": 159.66,  
            "last_purchase_date": '2022-05-12' 
        },
        'PNBGILTS': {
           "avg_purchase_price": 60.41,  
           "last_purchase_price": 62.90,
            "last_purchase_date": '2023-08-31' 
        },

        'TATACOMM': {
            "avg_purchase_price": 750,  
            "last_purchase_price": 750,
            "last_purchase_date": '2007-12-28' 
        },
        'TATAMOTORS': {
            "avg_purchase_price": 434.05,  
            "last_purchase_price": 434.05,
            "last_purchase_date": '2022-03-22' 
        },
        'TATASTEEL': {
           "avg_purchase_price": 106.92,  
           "last_purchase_price": 106.92,
            "last_purchase_date": '2022-09-07' 
        },
        'TATAPOWER': {
            "avg_purchase_price": 247.45,  
            "last_purchase_price": 283.80,
            "last_purchase_date": '2022-05-12'  
        },
        'WELSPUNLIV': {
            "avg_purchase_price": 93.91,
            "last_purchase_price": 93.91,  
            "last_purchase_date": '2022-04-21'  
        },
        'WIPRO': {
            "avg_purchase_price": 234.89,  
            "last_purchase_price": 234.89,
            "last_purchase_date": '2022-06-09'  
        },
        
    }


    with st.spinner("Generating portfolio snapshot..."):
        process_symbols(symbols,stock_data)

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
                process_symbols(symbols,stock_data)

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

def clean_price(price):
    # Check if the price is a string (which contains '₹' and commas)
    if isinstance(price, str):
        return float(price.replace("₹", "").replace(",", ""))
    return price  # If it's already a float, just return it

def color_current_price(value, average_buy):
    # Clean both values, remove ₹ and commas, then convert to float
    value = clean_price(value)
    average_buy = clean_price(average_buy)
    
    # Compare and apply color formatting for display
    if value < average_buy:
        return f'<span style="color: red;">₹{value:.2f}</span>'
    else:
        return f'<span style="color: black;">₹{value:.2f}</span>'

def calculate_gain_loss(df):
    today = dt.today()

    def compute(row):
        last_buy_price = clean_price(row["Last Buy"])
        current_price = clean_price(row["Current Price"])

        # Check if the Last Buy Date is None or empty
        if pd.isna(row["Last Buy Date"]) or row["Last Buy Date"] is None:
            # Handle missing date (you can skip the row, set to a default, etc.)
            return pd.Series([None, None, None])  # Return None for all calculations if date is missing

        # If the date is valid, parse it
        buy_date = dt.strptime(row["Last Buy Date"], "%Y-%m-%d")
        years_held = (today - buy_date).days / 365.25  # Account for leap years

        # Price difference
        price_difference = current_price - last_buy_price

        # Percentage gain/loss
        percentage_gain = (price_difference / last_buy_price) * 100

        # Avoid division by zero for annualized return
        if years_held > 0:
            annualized_return = ((1 + (percentage_gain / 100)) ** (1 / years_held) - 1) * 100
        else:
            annualized_return = percentage_gain  # If held for less than a year

        years_held="{:.1f}".format(years_held)   # round to one decimal place
        annualized_return="{:.2f}".format(annualized_return)   # round to 2 decimal place

        return pd.Series([price_difference, percentage_gain,years_held, annualized_return])

    # Apply calculation to each row
    df[["Price Difference", "Total Gain %","Years", "Annualized Gain %"]] = df.apply(compute, axis=1)
    #print(df[["Price Difference", "Total Gain %", "Annualized Gain %"]])
    return df


def process_symbols(symbols, stock_data):
    # Generate snapshot
    portfolio_df, summary, message = generate_portfolio_snapshot(symbols, stock_data)

    if message != "success":
        st.error(message)
    else:
        portfolio_data = pd.DataFrame(portfolio_df)

        # Apply calculations and get the modified DataFrame
        df = calculate_gain_loss(portfolio_df)

        # Option 1: Assign the calculated columns from df to portfolio_data
        portfolio_data["Price Difference"] = df["Price Difference"]
        portfolio_data["Total Gain %"] = df["Total Gain %"]
        portfolio_data["Years"] = df["Years"]
        portfolio_data["Annualized Gain %"] = df["Annualized Gain %"]

        # Apply formatting for display, separate from calculations
        # portfolio_df["Current Price"] = portfolio_df.apply(lambda row: color_current_price(row["Current Price"], row["Last Buy"]), axis=1)
        # portfolio_df["Current Price"] = portfolio_df["Current Price"].apply(lambda x: f'<span style="color: red;">₹{x}</span>' if x < row["Last Buy"] else f'<span style="color: black;">₹{x}</span>')

        portfolio_df["Current Price"] = portfolio_df.apply(
                lambda row: color_current_price(row["Current Price"], row["Last Buy"]), axis=1
        )
        

        # # Display DataFrame with Streamlit
        # st.markdown(
        #     portfolio_df.to_html(escape=False, index=False), unsafe_allow_html=True
        # )

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

        # # Display portfolio table
        # st.subheader("Portfolio Details")
        # #print(portfolio_data)
        # st.dataframe(
        #     portfolio_data,
        #     column_config={
        #         "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
        #         "Average Buy": st.column_config.TextColumn("Average Buy", width="medium"),
        #         "Last Buy": st.column_config.TextColumn("Last Buy", width="medium"),
        #         "Last Buy Date": st.column_config.TextColumn("Last Buy Date", width="medium"),

        #         "Price Difference": st.column_config.TextColumn("Price Difference", width="medium"),
        #         "Total Gain %": st.column_config.TextColumn("Total Gain %", width="medium"),
        #         "Annualized Gain %": st.column_config.TextColumn("Annualized Gain %", width="medium"),

        #         "Current Price": st.column_config.TextColumn("Current Price", width="medium"),
        #         "Change": st.column_config.TextColumn("Change", width="medium"),
        #         "Change %": st.column_config.TextColumn("Change %", width="medium"),
        #         "52W High": st.column_config.TextColumn("52W High", width="medium"),
        #         "52W Low": st.column_config.TextColumn("52W Low", width="medium"),
        #         "Distance from 52W High %": st.column_config.TextColumn("Distance from 52W High", width="medium"),
        #         "Distance from 52W Low %": st.column_config.TextColumn("Distance from 52W Low", width="medium")
        #     },
        #     hide_index=True
        # )

        # # Download button for portfolio data
        # csv = portfolio_df.to_csv(index=False)
        # st.download_button(
        #     label="Download Portfolio Snapshot",
        #     data=csv,
        #     file_name=f"portfolio_snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        #     mime="text/csv"
        # )

        # Display DataFrame with Streamlit
        st.markdown(
            portfolio_df.to_html(escape=False, index=False), unsafe_allow_html=True
        )

