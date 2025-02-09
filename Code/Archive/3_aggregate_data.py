import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime


def get_dfs(csv_files):
    # Read and concatenate all CSV files
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)

    # Combine all dataframes
    df = pd.concat(dfs, ignore_index=True)
    return df

def deduplicate_by_quality(df):
    df["quantity_qualifier-6063"] = df["quantity_qualifier-6063"].astype(str) # Convert quantity_qualifier-6063 to string
    
    # Create a custom sort order for quality indicators
    quality_order = {'220': 0,  # True value (highest priority)
                    '67': 1,    # Replacement value
                    'Z18': 2}   # Preliminary value (lowest priority)
    
    # Map the quality indicators to their sort order
    df['quality_sort'] = df['quantity_qualifier-6063'].map(quality_order)
    
    # Sort by start time first, then by quality sort order
    df = df.sort_values(by=['start', 'quality_sort'])
    
    # Drop the temporary sorting column
    df = df.drop('quality_sort', axis=1)

    # Drop duplicate start times, keeping best quality data
    df = df.drop_duplicates(subset='start', keep='first')
    return df

if __name__ == "__main__":
    # Get list of all CSV files in the Quantified_messages directory
    csv_files = glob.glob('Data/a_daily_reports/*.csv')
    csv_files = [f for f in csv_files if  f.split('_')[3]=='TL'] # this is ugly!

    df = get_dfs(csv_files)
    # df = deduplicate_by_quality(df)
    df.drop(columns=['message'])            
    # Sort by quality indicator preference (220 > 67 > Z18)
    df = df.sort_values(by=['start', 'quantity_qualifier-6063']).drop_duplicates(subset='start', keep='first')
    
    df.to_csv('Data/TL_data.csv', index=False)  

    
    