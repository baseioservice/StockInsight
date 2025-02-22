import datetime
import pytz
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Tuple, Optional, Dict, List

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

def get_nse_indices() -> Dict[str, Tuple[Optional[pd.DataFrame], Optional[dict], str]]:
    """Fetch NSE indices data (Nifty 50 and Bank Nifty)."""
    indices = {
        'NIFTY 50': '^NSEI',
        'BANK NIFTY': '^NSEBANK'
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

def get_stock_data(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[dict], str]:
    """Fetch stock data from Yahoo Finance."""
    try:
        # Convert to upper case and append .NS or .BO if not present
        symbol = symbol.upper()
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

        # Generate sparkline data
        info['sparkline_data'] = generate_sparkline_data(hist)

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

def generate_sparkline_data(hist_data: pd.DataFrame) -> list:
    """Generate normalized data for sparkline visualization."""
    if hist_data is None or hist_data.empty:
        return []

    # Get last 30 days of closing prices
    close_prices = hist_data['Close'].tail(30)

    # Normalize to 0-1 range for consistent visualization
    if len(close_prices) > 0:
        min_price = close_prices.min()
        max_price = close_prices.max()
        if max_price != min_price:
            normalized = (close_prices - min_price) / (max_price - min_price)
            return normalized.tolist()
    return []

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
                hist = stock.history(period="1y")

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

                # Generate sparkline data
                sparkline_data = generate_sparkline_data(hist)

                # Add to total value (assuming equal weights for simplicity)
                total_value += current_price
                total_change += change

                portfolio_data.append({
                    'Symbol': symbol.replace('.NS', ''),
                    'Trend': sparkline_data,
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