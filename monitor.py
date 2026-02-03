import yfinance as yf
import pandas as pd
import time
import os
from datetime import datetime

# Configuration
CSV_FILE = "stocks.csv"
HTML_FILE = "dashboard.html"
TICKERS_FILE = "tickers.csv"
UPDATE_INTERVAL_SECONDS = 600  # 10 minutes

def get_tickers():
    """Reads tickers from the configuration CSV."""
    default_tickers = ["PSLV", "SLVR", "GLDM"]
    if not os.path.exists(TICKERS_FILE):
        print(f"Warning: {TICKERS_FILE} not found. Using defaults.")
        return default_tickers
    
    try:
        df = pd.read_csv(TICKERS_FILE)
        if "Ticker" in df.columns:
            # Clean whitespace and return list
            return df["Ticker"].astype(str).str.strip().tolist()
        else:
            print("Error: 'Ticker' column not found in CSV. Using defaults.")
            return default_tickers
    except Exception as e:
        print(f"Error reading tickers file: {e}")
        return default_tickers

def fetch_prices():
    """Fetches current prices for all tickers."""
    data = {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    current_tickers = get_tickers()
    print(f"[{timestamp}] Fetching prices for: {', '.join(current_tickers)}")
    
    for ticker in current_tickers:
        try:
            stock = yf.Ticker(ticker)
            # fast_info is often faster/more reliable for current price than history
            price = stock.fast_info.last_price
            if price is None: 
                 # Fallback to history if fast_info fails
                 hist = stock.history(period="1d")
                 if not hist.empty:
                     price = hist['Close'].iloc[-1]
            
            if price:
                data[ticker] = round(price, 2)
                print(f"  {ticker}: ${price:.2f}")
            else:
                print(f"  {ticker}: Failed to fetch")
                
        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")
            
    return timestamp, data

def update_csv(timestamp, prices):
    """Appends new data to the CSV file, handling new columns if tickers change."""
    # Prepare new row data
    row = {"Timestamp": timestamp}
    row.update(prices)
    df_new = pd.DataFrame([row])
    
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False)
        print(f"  Created {CSV_FILE}")
    else:
        try:
            # Read existing data
            # on_bad_lines='skip' avoids crashing if file is slightly corrupted, 
            # though we want to ideally header-match. 
            # We read everything as object to avoid type errors during merge, then infer later if needed.
            df_old = pd.read_csv(CSV_FILE)
            
            # Combine old and new data
            # pd.concat aligns columns automatically, adding NaNs for missing data in old rows
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            
            # Write back the full file (updates header if new columns appeared)
            df_combined.to_csv(CSV_FILE, index=False)
            print(f"  Data saved to {CSV_FILE} (Schema updated)")
            
        except Exception as e:
            print(f"  Error updating CSV: {e}")
            # Fallback: Just append if read failed (might cause the original issue, but best effort)
            try:
                df_new.to_csv(CSV_FILE, mode='a', header=False, index=False)
            except:
                pass

from plotly.subplots import make_subplots
import plotly.graph_objects as go

def generate_dashboard():
    """Reads the CSV and generates an interactive HTML dashboard with Dual Y-Axes."""
    if not os.path.exists(CSV_FILE):
        print("  No data to graph yet.")
        return

    try:
        # on_bad_lines='skip' ignores rows with mismatching fields (like the ones causing the crash)
        df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Get list of tickers (excluding Timestamp)
        tickers = [col for col in df.columns if col != "Timestamp"]
        
        for ticker in tickers:
            # Determine which axis to use based on the last valid price
            # If price > 1000, use Right Axis (Secondary)
            last_price = df[ticker].iloc[-1] if not df[ticker].empty else 0
            
            is_secondary = False
            if pd.notna(last_price) and last_price > 1000:
                is_secondary = True
                
            fig.add_trace(
                go.Scatter(x=df["Timestamp"], y=df[ticker], name=ticker),
                secondary_y=is_secondary,
            )
            
        fig.update_layout(
            title_text="Stock Price Tracker (Dual Axis)",
            template="plotly_dark",
            hovermode="x unified" # Shows all values for a timestamp on hover
        )
        
        # Set y-axis titles
        fig.update_yaxes(title_text="Primary Price ($)", secondary_y=False)
        fig.update_yaxes(title_text="High Value Price ($)", secondary_y=True)
        
        # Auto-refresh the page every 600 seconds (10 mins) using meta tag
        # We inject this into the generated HTML
        fig.write_html(HTML_FILE)
        
        # Add auto-refresh to the HTML file
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Inject meta refresh tag in the head/body
        refresh_tag = f'<meta http-equiv="refresh" content="{UPDATE_INTERVAL_SECONDS}">'
        updated_content = content.replace("<head>", f"<head>{refresh_tag}")
        
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
        print(f"  Dashboard updated: {HTML_FILE}")
        
    except Exception as e:
        print(f"  Error generating dashboard: {e}")

def main():
    print("Starting Stock Tracker Monitor...")
    print(f"Reading tickers from {TICKERS_FILE}...")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            timestamp, prices = fetch_prices()
            
            if prices:
                update_csv(timestamp, prices)
                generate_dashboard()
            
            print(f"Sleeping for {UPDATE_INTERVAL_SECONDS} seconds...")
            time.sleep(UPDATE_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\nStopping monitor.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(60) # Retry after a minute on crash

if __name__ == "__main__":
    main()
