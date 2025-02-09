import datetime
import pandas as pd
import glob


def load_csv(file_path):
    """Load a CSV file into a DataFrame."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


def find_em_file():
    """Find the first EM file in 'Data/Tabularized_interchanges/'."""
    em_files = glob.glob('Data/Tabularized_interchanges/*.csv')
    return next((f for f in em_files if f.split('_')[2] == 'EM'), None)


def align_dates(df):
    """Convert start and end columns to datetime and remove timezone information."""
    df['start'] = pd.to_datetime(df['start']).dt.tz_localize(None)
    df['end'] = pd.to_datetime(df['end']).dt.tz_localize(None)
    return df


def filter_by_date(df, start_date, end_date):
    """Filter DataFrame to only include rows within the given date range."""
    return df[(df['start'] >= start_date) & (df['start'] <= end_date)]


def calculate_difference(tl_sum, em_sum):
    """Calculate the percentage difference between TL and EM sums."""
    return ((tl_sum - em_sum) / em_sum) * 100 if em_sum != 0 else 0


def main():
    """Main execution function for data processing."""
    
    # 📌 Load TL Data
    tl_data_path = 'Data/quantity_data.csv'
    df_tl = load_csv(tl_data_path)
    
    # 📌 Find and Load EM Data
    em_file_path = find_em_file()
    if not em_file_path:
        raise FileNotFoundError("No EM message file found in 'Data/Tabularized_interchanges/'.")

    df_em = load_csv(em_file_path)

    # 📌 Align Dates
    df_tl = align_dates(df_tl)
    df_em = align_dates(df_em)

    # 📌 Define Date Range for December
    start_date = datetime.datetime(2024, 11, 30, 0, 0, 0)
    end_date = datetime.datetime(2024, 12, 31, 0, 0, 0)

    # 📌 Filter TL Data for December
    df_december_tl = filter_by_date(df_tl, start_date, end_date)

    # 📌 Compute Totals
    tl_sum_dec = df_december_tl['quantity_value-6060'].sum()
    em_sum_dec = df_em['quantity_value-6060'].sum()

    # 📌 Compute Difference
    difference = calculate_difference(tl_sum_dec, em_sum_dec)

    # 📌 Print Results
    print(f"📅 **December Totals**")
    print(f"🔹 TL Total: {tl_sum_dec}")
    print(f"🔹 EM Total: {em_sum_dec}")
    print(f"📉 **Difference:** {difference:.2f}%")

    
if __name__ == "__main__":
    main()
