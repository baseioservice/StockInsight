import datetime
import pytz
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Tuple, Optional, Dict, List
import requests


NSE_HOLIDAY_URL = "https://www.nseindia.com/api/holiday-master?type=trading"

def get_nse_holidays() -> list:
    """Fetch Indian market holidays from NSE."""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(NSE_HOLIDAY_URL, headers=headers)
        data = response.json()
        holidays = [item['tradingDate'] for item in data['CM'] if item['holidayType'] == 'TRADING']
        return holidays
    except Exception as e:
        print("Error fetching NSE holidays:", e)
        return []

def is_indian_market_open() -> Tuple[bool, str]:
    """Check if the Indian market is open, considering holidays."""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist)

    # Market hours: 9:15 AM to 3:30 PM IST, Monday to Friday
    market_start = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = current_time.replace(hour=15, minute=30, second=0, microsecond=0)

    # # Fetch real-time holidays
    # holidays = get_nse_holidays()
    
    # # Convert holiday dates to datetime format
    # holiday_dates = [datetime.datetime.strptime(date, "%d-%b-%Y").date() for date in holidays]

    # # Check if today is a holiday
    # if current_time.date() in holiday_dates:
    #     return False, f"Market is closed (Holiday)" # - Next Open Date Unknown"

    # Check if today is a weekend
    if current_time.weekday() >= 5:  # Saturday or Sunday
        return False, "Market is closed (Weekend) - Opens on Monday at 9:15 AM IST"

    # Check if market hours
    if current_time < market_start:
        return False, f"Market is closed - Opens today at {market_start.strftime('%I:%M %p')} IST"

    if current_time > market_end:
        return False, f"Market is closed - Opens tomorrow at 9:15 AM IST"

    return True, "Market is open"

# Example Usage
# market_status, message = is_indian_market_open()
# print(market_status, message)


# def is_indian_market_open() -> Tuple[bool, str]:
#     """Check if Indian market is open and return next opening time if closed."""
#     ist = pytz.timezone('Asia/Kolkata')
#     current_time = datetime.datetime.now(ist)

#     # Market hours: 9:15 AM to 3:30 PM IST, Monday to Friday
#     market_start = current_time.replace(hour=9, minute=15, second=0)
#     market_end = current_time.replace(hour=15, minute=30, second=0)

#     # Calculate next opening time
#     next_opening = None
#     if current_time.weekday() >= 5:  # Weekend
#         days_until_monday = (7 - current_time.weekday()) % 7
#         next_opening = (current_time + datetime.timedelta(days=days_until_monday)).replace(
#             hour=9, minute=15, second=0
#         )
#         return False, f"Market is closed (Weekend) - Opens on {next_opening.strftime('%A, %B %d at %I:%M %p')} IST"

#     if current_time > market_end:
#         # After market hours, will open tomorrow
#         next_day = current_time + datetime.timedelta(days=1)
#         if next_day.weekday() >= 5:  # If tomorrow is weekend
#             days_until_monday = (7 - next_day.weekday()) % 7
#             next_opening = (next_day + datetime.timedelta(days=days_until_monday))
#         else:
#             next_opening = next_day
#         next_opening = next_opening.replace(hour=9, minute=15, second=0)
#         return False, f"Market is closed - Opens on {next_opening.strftime('%A, %B %d at %I:%M %p')} IST"

#     if current_time < market_start:
#         return False, f"Market is closed - Opens today at {market_start.strftime('%I:%M %p')} IST"

#     return True, "Market is open"


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI) for a given series."""
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_nse_indices() -> Dict[str, Tuple[Optional[pd.DataFrame], Optional[dict], str]]:
    """Fetch NSE & BSE indices data (Nifty 50, Bank Nifty, and Sensex)."""
    indices = {
        'NIFTY 50': '^NSEI',
        'BANK NIFTY': '^NSEBANK',
        'SENSEX': '^BSESN'
    }

    result = {}
    for index_name, symbol in indices.items():
        try:
            index = yf.Ticker(symbol)
            info = index.info

            if 'regularMarketPrice' not in info:
                result[index_name] = (None, None, f"Unable to fetch {index_name} data")
                continue

            hist = index.history(period="1y")
            if hist.empty:
                result[index_name] = (None, None, f"No historical data available for {index_name}")
                continue

            # Calculate technical indicators
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            hist['MA200'] = hist['Close'].rolling(window=200).mean()
            hist['RSI'] = calculate_rsi(hist['Close'])

            result[index_name] = (hist, info, "success")

        except Exception as e:
            result[index_name] = (None, None, f"Error fetching {index_name} data: {str(e)}")

    return result


# def get_stock_data(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[dict], str]:
#     """Fetch stock data from Yahoo Finance."""
#     try:
#         # Convert to upper case and append .NS or .BO if not present
#         symbol = symbol.upper()
#         if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
#             symbol = f"{symbol}.NS"  # Default to NSE

#         stock = yf.Ticker(symbol)
#         info = stock.info

#         # Check if valid stock
#         if 'regularMarketPrice' not in info:
#             return None, None, "Invalid stock symbol"

#         # Get historical data
#         hist = stock.history(period="1y")
#         if hist.empty:
#             return None, None, "No historical data available"

#         # Calculate technical indicators
#         # Moving averages
#         hist['MA20'] = hist['Close'].rolling(window=20).mean()
#         hist['MA50'] = hist['Close'].rolling(window=50).mean()
#         hist['MA200'] = hist['Close'].rolling(window=200).mean()

#         # RSI
#         hist['RSI'] = calculate_rsi(hist['Close'])

#         return hist, info, "success"

#     except Exception as e:
#         return None, None, f"Error fetching data: {str(e)}"

import yfinance as yf
import pandas as pd
from typing import Optional, Tuple, Dict, List

def get_stock_data(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[dict], str, Optional[dict]]:
    """Fetch stock data and provide insights with fundamentals, sentiment, and sector analysis."""
    try:
        symbol = symbol.upper()
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"

        stock = yf.Ticker(symbol)
        info = stock.info

        if 'regularMarketPrice' not in info:
            return None, None, "Invalid stock symbol", None

        hist = stock.history(period="1y")
        if hist.empty:
            return None, None, "No historical data available", None

        # Calculate technical indicators
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])

        # Extract key financial data
        current_price = info.get('regularMarketPrice', 0)
        ma50 = hist['MA50'].iloc[-1]
        ma200 = hist['MA200'].iloc[-1]
        rsi = hist['RSI'].iloc[-1]
        pe_ratio = info.get('trailingPE', None)
        eps = info.get('trailingEps', None)
        week52_high = info.get('fiftyTwoWeekHigh', None)
        week52_low = info.get('fiftyTwoWeekLow', None)
        dividend_yield = info.get('dividendYield', None)
        earnings_growth = info.get('earningsGrowth', None)
        debt_to_equity = info.get('debtToEquity', None)
        sector = info.get('sector', 'Unknown')


        # Extract ROE  ROE=Net Income​ / Shareholder’s Equity
        roe = info.get('returnOnEquity', None)  # Usually in decimal form (e.g., 0.15 = 15%)
        if roe is not None:
            roe = round(roe * 100, 2)  # Convert to percentage


        # Generate pros & cons
        pros, cons = [], []

        # P/E= Stock Price​/ Earnings Per Share (EPS)

        # **Technical Analysis Insights**
        if current_price > ma50 and current_price > ma200:
            pros.append("Stock is in an uptrend (above 50-day & 200-day MA).")
        if 30 < rsi < 70:
            pros.append("RSI is in a healthy range (30-70).")
        if current_price >= week52_high * 0.95:
            pros.append("Near 52-week high (strong momentum).")
        if pe_ratio and pe_ratio < 20:
            pros.append(f"Low P/E ratio ({pe_ratio:.2f}), undervalued.")

        if current_price < ma50 or current_price < ma200:
            cons.append("Stock is in a downtrend (below key moving averages).")
        if rsi > 70:
            cons.append("Stock is overbought (RSI > 70), possible correction ahead.")
        if rsi < 30:
            cons.append("Stock is oversold (RSI < 30), indicating weakness.")
        if current_price <= week52_low * 1.05:
            cons.append("Near 52-week low, weak momentum.")
        if pe_ratio and pe_ratio > 50:
            cons.append(f"High P/E ratio ({pe_ratio:.2f}), overvalued.")


        if roe is not None:
            if roe > 15:
                pros.append(f"Strong Return on Equity (ROE): {roe}% - Indicates good profitability and efficient management.")
            elif roe > 8:
                pros.append(f"Moderate Return on Equity (ROE): {roe}% - Decent profitability, but further analysis needed.")
            else:
                cons.append(f"Low Return on Equity (ROE): {roe}% - Could indicate inefficiencies or weak profitability.")


        # EPS (Earnings Per Share)
        if eps is not None:
            if eps > 30:
                pros.append(f"Very strong earnings per share {eps}, indicating high profitability.")
            elif eps > 10:
                pros.append(f"Good EPS {eps}, suggesting a profitable company.")
            else:
                cons.append(f"Low EPS {eps}, company may have profitability concerns.")


        # **Fundamental Insights**
        if dividend_yield and dividend_yield > 0:
            pros.append(f"Pays dividends (Yield: {dividend_yield * 100:.2f}%).")
        else:
            cons.append("No dividends, less passive income potential.")

        # if earnings_growth and earnings_growth > 0:
        #     pros.append(f"Positive earnings growth ({earnings_growth * 100:.2f}%).")
        # else:
        #     cons.append("Negative earnings growth, may indicate weaker future performance.")

        # if debt_to_equity and debt_to_equity < 1:
        #     pros.append(f"Low debt-to-equity ratio ({debt_to_equity:.2f}), financially stable.")
        # else:
        #     cons.append(f"High debt-to-equity ratio ({debt_to_equity:.2f}), may struggle with debt.")

        # **Sector Comparison Insights**
        industry_avg_pe = get_sector_avg_pe(sector)
        if pe_ratio and industry_avg_pe:
            if pe_ratio < industry_avg_pe:
                pros.append(f"P/E ratio ({pe_ratio:.2f}) is lower than sector average ({industry_avg_pe:.2f}).")
            else:
                cons.append(f"P/E ratio ({pe_ratio:.2f}) is higher than sector average ({industry_avg_pe:.2f}), overvalued.")

        # **News Sentiment Analysis**
        sentiment = get_news_sentiment(symbol)
        if sentiment == "Positive":
            pros.append("Positive news sentiment, good market perception.")
        elif sentiment == "Negative":
            cons.append("Negative news sentiment, possible market concerns.")
        else:
            pros.append("Neutral news sentiment, no strong bias.")

        insights = {"Pros": pros, "Cons": cons}

        return hist, info, "success", insights

    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}", None

# **Helper function to get sector average P/E ratio**
def get_sector_avg_pe(sector: str) -> Optional[float]:
    """Mock function to return average P/E ratio of a sector (replace with real data)."""
    sector_pe_data = {
        "Technology": 25,
        "Finance": 15,
        "Healthcare": 18,
        "Consumer Goods": 22,
        "Energy": 12
    }
    return sector_pe_data.get(sector, None)

# **Helper function to get news sentiment analysis**
def get_news_sentiment(symbol: str) -> str:
    """Mock function for news sentiment analysis (replace with real API)."""
    # In a real implementation, you can use a news API + sentiment analysis (e.g., NLP models)
    sentiment_data = {
        "TCS.NS": "Positive",
        "INFY.NS": "Neutral",
        "HDFC.NS": "Negative"
    }
    return sentiment_data.get(symbol, "Neutral")



def format_currency(value: float) -> str:
    """Format number with Indian Rupee symbol."""
    if pd.isna(value):
        return "N/A"
    return f"₹{value:,.2f}"

def prepare_summary_data(info: dict) -> pd.DataFrame:
    """Prepare summary table data."""
    metrics = {
        'Current Price': info.get('regularMarketPrice', None),
        'Previous Close': info.get('regularMarketPreviousClose', None),
        'Open': info.get('regularMarketOpen', None),
        'Day High': info.get('dayHigh', None),
        'Day Low': info.get('dayLow', None),
        '52 Week High': info.get('fiftyTwoWeekHigh', None),
        '52 Week Low': info.get('fiftyTwoWeekLow', None),
        'Stock P/E [igone currency symbol]': info.get('trailingPE', None),
        'EPS': info.get('trailingEps', None),
        'Market Cap': info.get('marketCap', None),
        'Volume': info.get('volume', None)
    }

    df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
    df['Value'] = df['Value'].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else 'N/A')
    return df

def generate_portfolio_snapshot(symbols: List[str]) -> Tuple[Optional[pd.DataFrame], Dict, str]:
    """Generate a snapshot of the portfolio performance."""
    try:
        portfolio_data = []
        total_value = 0
        total_change = 0
        invalid_symbols = []

        for symbol in symbols:
            try:
                # Convert to upper case and append .NS if not present
                symbol = symbol.strip().upper()
                if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
                    symbol = f"{symbol}.NS"

                stock = yf.Ticker(symbol)
                info = stock.info

                if not info or 'regularMarketPrice' not in info:
                    invalid_symbols.append(symbol.replace('.NS', ''))
                    continue

                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('regularMarketPreviousClose', 0)
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close else 0

                # Get 52-week data
                week_high = info.get('fiftyTwoWeekHigh', 0)
                week_low = info.get('fiftyTwoWeekLow', 0)

                # Add to total value (assuming equal weights for simplicity)
                total_value += current_price
                total_change += change

                portfolio_data.append({
                    'Symbol': symbol.replace('.NS', ''),
                    'Current Price': current_price,
                    'Change': change,
                    'Change %': change_percent,
                    '52W High': week_high,
                    '52W Low': week_low,
                    'Distance from 52W High %': ((week_high - current_price) / week_high * 100) if week_high else 0,
                    'Distance from 52W Low %': ((current_price - week_low) / week_low * 100) if week_low else 0
                })
            except Exception as e:
                invalid_symbols.append(symbol.replace('.NS', ''))
                continue

        if not portfolio_data:
            invalid_symbols_str = ", ".join(invalid_symbols)
            return None, None, f"No valid stocks found in portfolio. Invalid symbols: {invalid_symbols_str}"

        # Create DataFrame
        df = pd.DataFrame(portfolio_data)

        # Format the DataFrame
        for col in ['Current Price', 'Change', '52W High', '52W Low']:
            df[col] = df[col].apply(format_currency)

        for col in ['Change %', 'Distance from 52W High %', 'Distance from 52W Low %']:
            df[col] = df[col].apply(lambda x: f"{x:.2f}%")

        # Calculate portfolio summary
        summary = {
            'Total Value': total_value,
            'Total Change': total_change,
            'Total Change %': (total_change / (total_value - total_change) * 100) if (total_value - total_change) != 0 else 0,
            'Best Performer': df.iloc[df['Change %'].str.rstrip('%').astype(float).idxmax()]['Symbol'],
            'Worst Performer': df.iloc[df['Change %'].str.rstrip('%').astype(float).idxmin()]['Symbol'],
            'Timestamp': datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')
        }

        # Add invalid symbols to summary if any
        if invalid_symbols:
            summary['Invalid Symbols'] = invalid_symbols

        return df, summary, "success"

    except Exception as e:
        return None, None, f"Error generating portfolio snapshot: {str(e)}"