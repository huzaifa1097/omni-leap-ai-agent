#!/usr/bin/env python3
"""
Simple Stock Test Script - No LangChain Dependencies
"""

import os
import sys

# Create static directory
os.makedirs('static', exist_ok=True)

try:
    import yfinance as yf
    import matplotlib.pyplot as plt
    import pandas as pd
    
    print("✓ All packages imported successfully!")
    
    def simple_stock_comparison():
        """Simple stock comparison without any complex dependencies"""
        print("\nDownloading stock data...")
        
        # Download data for Tesla and Nvidia
        tickers = ['TSLA', 'NVDA']
        data = {}
        
        for ticker in tickers:
            try:
                print(f"Fetching {ticker}...")
                stock_data = yf.download(ticker, period='6mo', progress=False)
                
                if not stock_data.empty:
                    data[ticker] = stock_data
                    current_price = stock_data['Close'].iloc[-1]
                    start_price = stock_data['Close'].iloc[0]
                    change_percent = ((current_price - start_price) / start_price) * 100
                    
                    print(f"✓ {ticker}: ${current_price:.2f} ({change_percent:+.2f}%)")
                else:
                    print(f"✗ No data for {ticker}")
                    
            except Exception as e:
                print(f"✗ Error with {ticker}: {e}")
        
        if not data:
            print("❌ No data retrieved. Cannot create chart.")
            return
        
        # Create the chart
        print("\nCreating chart...")
        plt.figure(figsize=(12, 6))
        
        colors = ['#1f77b4', '#ff7f0e']
        for i, (ticker, stock_data) in enumerate(data.items()):
            plt.plot(stock_data.index, stock_data['Close'], 
                    label=f'{ticker}', linewidth=2.5, color=colors[i])
        
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Stock Price ($)', fontsize=12)
        plt.title('Tesla vs Nvidia Stock Price Comparison (6 months)', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the chart
        chart_path = 'static/plot.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved to: {chart_path}")
        
        # Create JSON data for frontend
        json_data = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'tickers': list(data.keys()),
            'data': {}
        }
        
        for ticker, stock_data in data.items():
            json_data['data'][ticker] = {
                'current_price': float(stock_data['Close'].iloc[-1]),
                'prices': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'close': float(row['Close'])
                    }
                    for date, row in stock_data.iterrows()
                ]
            }
        
        # Save JSON
        import json
        with open('static/stock_data.json', 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print("✅ JSON data saved to: static/stock_data.json")
        print("\n🎉 All done! Check the static/ folder for outputs.")
    
    if __name__ == "__main__":
        simple_stock_comparison()

except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("\n📦 Install required packages:")
    print("pip install yfinance matplotlib pandas")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)