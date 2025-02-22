import datetime
import pytz
import pandas as pd
import yfinance as yf
from typing import Tuple, Optional

def is_indian_market_open() -> Tuple[bool, str]:
    """Check if Indian market is open."""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist)
    
    # Market hours: 9:15 AM to 3:30 PM IST, Monday to Friday
    market_start = current_time.replace(hour=9, minute=15, second=0)
    market_end = current_time.replace(hour=15, minute=30, second=0)
    
    if current_time.weekday() >= 5:  # Saturday or Sunday
        return False, "Market is closed (Weekend)"
    
    if market_start <= current_time <= market_end:
        return True, "Market is open"
    
    return False, "Market is closed (Trading hours: 9:15 AM - 3:30 PM IST)"

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
