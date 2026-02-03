import pandas as pd
import os

CSV_FILE = "stocks.csv"

def repair_outliers():
    if not os.path.exists(CSV_FILE):
        return

    try:
        df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
        initial_len = len(df)
        
        # Remove rows where SLVR is unrealistically high (> 500)
        # This targets the specific corrupted row 311
        df_clean = df[df["SLVR"] < 500]
        
        final_len = len(df_clean)
        
        if initial_len != final_len:
            df_clean.to_csv(CSV_FILE, index=False)
            print(f"Removed {initial_len - final_len} bad rows.")
        else:
            print("No bad rows found to remove.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    repair_outliers()
