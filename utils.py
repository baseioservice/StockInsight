import datetime
import pytz
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Tuple, Optional

def is_indian_market_open() -> Tuple[bool, str]:
    """Check if Indian market is open and return next opening time if closed."""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist)

    # Market hours: 9:15 AM to 3:30 PM IST, Monday to Friday
    market_start = current_time.replace(hour=9, minute=15, second=0)
    market_end = current_time.replace(hour=15, minute=30, second=0)

    # Calculate next opening time
    next_opening = None
    if current_time.weekday() >= 5:  # Weekend
        days_until_monday = (7 - current_time.weekday()) % 7
        next_opening = (current_time + datetime.timedelta(days=days_until_monday)).replace(
            hour=9, minute=15, second=0
        )
        return False, f"Market is closed (Weekend) - Opens on {next_opening.strftime('%A, %B %d at %I:%M %p')} IST"

    if current_time > market_end:
        # After market hours, will open tomorrow
        next_day = current_time + datetime.timedelta(days=1)
        if next_day.weekday() >= 5:  # If tomorrow is weekend
            days_until_monday = (7 - next_day.weekday()) % 7
            next_opening = (next_day + datetime.timedelta(days=days_until_monday))
        else:
            next_opening = next_day
        next_opening = next_opening.replace(hour=9, minute=15, second=0)
        return False, f"Market is closed - Opens on {next_opening.strftime('%A, %B %d at %I:%M %p')} IST"

    if current_time < market_start:
        return False, f"Market is closed - Opens today at {market_start.strftime('%I:%M %p')} IST"

    return True, "Market is open"

def calculate_rsi(data: pd.Series, periods: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_stock_data(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[dict], str]:
    """Fetch stock data from Yahoo Finance."""
    try:
        # Append .NS or .BO if not present
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"  # Default to NSE

        stock = yf.Ticker(symbol)
        info = stock.info

        # Check if valid stock
        if 'regularMarketPrice' not in info:
            return None, None, "Invalid stock symbol"

        # Get historical data
        hist = stock.history(period="1y")
        if hist.empty:
            return None, None, "No historical data available"

        # Calculate technical indicators
        # Moving averages
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()

        # RSI
        hist['RSI'] = calculate_rsi(hist['Close'])

        return hist, info, "success"

    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}"

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
        'Market Cap': info.get('marketCap', None),
        'Volume': info.get('volume', None)
    }

    df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
    df['Value'] = df['Value'].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else 'N/A')
    return df