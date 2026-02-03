import yfinance as yf

tickers = ["GC=F", "GLD", "^XAU", "XAU-USD"]
print("Testing tickers...")
for t in tickers:
    try:
        stock = yf.Ticker(t)
        info = stock.fast_info
        print(f"--- {t} ---")
        print(f"Price: {info.last_price}")
        print(f"Currency: {info.currency}")
        print(f"Exchange: {info.exchange}")
    except Exception as e:
        print(f"{t}: Error - {e}")
