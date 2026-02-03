import pandas as pd
import os

CSV_FILE = "stocks.csv"

def check_outliers():
    if not os.path.exists(CSV_FILE):
        print("CSV not found")
        return

    try:
        df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
        print("--- Stats ---")
        print(df.describe())
        
        print("\n--- Potential Outliers (SLVR > 500) ---")
        outliers = df[df["SLVR"] > 500]
        if not outliers.empty:
            print(outliers)
        else:
            print("No SLVR outliers found > 500.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_outliers()
