import yfinance as yf

tickers = ["XAU", "XAUUSD=X", "GC=F"]
print("Testing tickers...")
for t in tickers:
    try:
        stock = yf.Ticker(t)
        price = stock.fast_info.last_price
        history = stock.history(period="1d")
        if price:
            print(f"{t}: Found! Price={price}")
        elif not history.empty:
             print(f"{t}: Found (via history)! Price={history['Close'].iloc[-1]}")
        else:
            print(f"{t}: Not found or no data.")
    except Exception as e:
        print(f"{t}: Error - {e}")
