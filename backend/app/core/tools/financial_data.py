import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from langchain.tools import tool

# Try to import optional dependencies
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available. Some features will be limited.")

try:
    from alpha_vantage.timeseries import TimeSeries
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    print("Warning: alpha_vantage not available. Some features will be limited.")

def ensure_static_dir():
    """Ensure static directory exists"""
    os.makedirs('static', exist_ok=True)

@tool
def get_daily_stock_prices(ticker_symbol: str) -> str:
    """
    Use this tool to get the daily closing stock prices for a single ticker symbol.
    Input: A single ticker symbol like 'TSLA' or 'NVDA' (NOT multiple tickers).
    For multiple tickers, call this tool multiple times or use get_multiple_stock_prices.
    The output will be a string representation of a table with date and price.
    """
    ticker_symbol = ticker_symbol.strip().upper()
    
    # Remove any invalid characters or phrases
    if ' AND ' in ticker_symbol or ',' in ticker_symbol:
        return f"Error: This tool accepts only ONE ticker symbol at a time. You provided: '{ticker_symbol}'. Please use a single ticker like 'TSLA' or 'NVDA'."
    
    try:
        # Try Alpha Vantage first if API key is available
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if api_key and ALPHA_VANTAGE_AVAILABLE:
            try:
                ts = TimeSeries(key=api_key, output_format='pandas')
                data, meta_data = ts.get_daily(symbol=ticker_symbol, outputsize='compact')
                
                data.index.name = 'date'
                closing_prices = data[['4. close']].rename(columns={'4. close': 'price'})
                return closing_prices.to_string()
            except Exception as av_error:
                print(f"Alpha Vantage failed: {av_error}")
        
        # Fallback to yfinance
        if YFINANCE_AVAILABLE:
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period="3mo")
            
            if hist.empty:
                return f"Error: No data found for ticker symbol '{ticker_symbol}'. Please verify the ticker symbol is correct."
            
            closing_prices = hist[['Close']].rename(columns={'Close': 'price'})
            closing_prices.index.name = 'date'
            return closing_prices.to_string()
        else:
            return "Error: Neither Alpha Vantage nor yfinance is available. Please install the required packages."
    
    except Exception as e:
        return f"An error occurred while fetching stock data for {ticker_symbol}: {e}"

@tool
def get_multiple_stock_prices(ticker_symbols: str) -> str:
    """
    Use this tool to get daily stock prices for multiple ticker symbols.
    Input should be comma-separated ticker symbols, e.g., 'TSLA,NVDA,GOOGL'.
    Returns a JSON string with stock data for each ticker.
    """
    try:
        if not YFINANCE_AVAILABLE:
            return "Error: yfinance package is required for multiple stock downloads. Please install it with: pip install yfinance"
        
        # Parse ticker symbols
        tickers = [ticker.strip().upper() for ticker in ticker_symbols.split(',')]
        
        if len(tickers) == 0:
            return "Error: No valid ticker symbols provided."
        
        all_data = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")
                
                if not hist.empty:
                    closing_prices = hist[['Close']].rename(columns={'Close': 'price'})
                    closing_prices.index = closing_prices.index.strftime('%Y-%m-%d')
                    all_data[ticker] = closing_prices.to_dict()['price']
                else:
                    all_data[ticker] = "No data found"
            except Exception as ticker_error:
                all_data[ticker] = f"Error: {ticker_error}"
        
        return json.dumps(all_data, indent=2)
    
    except Exception as e:
        return f"An error occurred while fetching multiple stock data: {e}"

@tool
def create_stock_comparison_chart(ticker_symbols: str, period: str = "1y") -> str:
    """
    Create a comparison chart for multiple stocks and save it to static/plot.png.
    Input: comma-separated ticker symbols, e.g., 'TSLA,NVDA'
    Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    Returns: Success message with path to the saved chart file
    """
    try:
        if not YFINANCE_AVAILABLE:
            return "Error: yfinance package is required for chart creation. Please install it with: pip install yfinance"
        
        ensure_static_dir()
        
        # Parse ticker symbols
        tickers = [ticker.strip().upper() for ticker in ticker_symbols.split(',')]
        
        if len(tickers) == 0:
            return "Error: No valid ticker symbols provided."
        
        # Create figure
        plt.figure(figsize=(14, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        successful_tickers = []
        
        for i, ticker in enumerate(tickers):
            try:
                stock_data = yf.download(ticker, period=period, progress=False)
                
                if not stock_data.empty:
                    color = colors[i % len(colors)]
                    plt.plot(stock_data.index, stock_data['Close'], 
                            label=f'{ticker}', linewidth=2.5, color=color)
                    successful_tickers.append(ticker)
                    
            except Exception as ticker_error:
                print(f"Error downloading {ticker}: {ticker_error}")
        
        if not successful_tickers:
            return "Error: No valid stock data could be retrieved for any of the provided tickers."
        
        # Customize chart
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Stock Price ($)', fontsize=12, fontweight='bold')
        plt.title(f'Stock Price Comparison: {", ".join(successful_tickers)}', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.legend(fontsize=11, loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plot_path = 'static/plot.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"Successfully created stock comparison chart at {plot_path} for tickers: {', '.join(successful_tickers)}"
    
    except Exception as e:
        return f"Error creating stock comparison chart: {e}"

@tool
def simple_stock_chart_code() -> str:
    """
    Returns Python code that can be executed with code_interpreter_tool to create a stock chart.
    This is a fallback when other tools fail.
    """
    code = '''
import yfinance as yf
import matplotlib.pyplot as plt
import os

# Create static directory
os.makedirs('static', exist_ok=True)

# Download stock data
tesla = yf.download('TSLA', period='6mo', progress=False)
nvidia = yf.download('NVDA', period='6mo', progress=False)

# Create plot
plt.figure(figsize=(12, 6))
plt.plot(tesla.index, tesla['Close'], label='Tesla (TSLA)', linewidth=2)
plt.plot(nvidia.index, nvidia['Close'], label='Nvidia (NVDA)', linewidth=2)

plt.xlabel('Date')
plt.ylabel('Stock Price ($)')
plt.title('Tesla vs Nvidia Stock Price Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('static/plot.png', dpi=300, bbox_inches='tight')
print('Chart saved to static/plot.png')
'''
    return code

# Test function to verify everything works
def test_tools():
    """Test function to verify the tools work"""
    print("Testing financial tools...")
    
    # Test single ticker
    print("\n1. Testing single ticker (TSLA):")
    result1 = get_daily_stock_prices("TSLA")
    print("Success!" if "Error:" not in result1 else f"Failed: {result1}")
    
    # Test multiple tickers
    print("\n2. Testing multiple tickers (TSLA,NVDA):")
    result2 = get_multiple_stock_prices("TSLA,NVDA")
    print("Success!" if "Error:" not in result2 else f"Failed: {result2}")
    
    # Test chart creation
    print("\n3. Testing chart creation:")
    result3 = create_stock_comparison_chart("TSLA,NVDA")
    print(result3)

if __name__ == "__main__":
    test_tools()