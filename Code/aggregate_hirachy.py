import json
import os
import pandas as pd

def load_tables(path, files):
     tables = []
     for file in files:
          table = pd.read_csv(f'{path}/{file}')
          tables.append(table)
     return tables

def drop_duplicates(df):
     df = df.sort_values(by=['start', 'quantity_qualifier-6063']).drop_duplicates(subset='start', keep='first')
     df['quantity_value-6060'] = df['quantity_value-6060'].str.replace(',', '.').astype(float)
     return df

if __name__ == '__main__':
     files = os.listdir('Data/quantity_data')
     files = [file for file in files if file.split('_')[1] == 'TL']
     tables = load_tables('Data/quantity_data', files)
     df = pd.concat(tables).reset_index(drop=True) # merge all tables into one
     # sort by status

     df = drop_duplicates(df)

     df.to_csv('Data/quantity_data.csv', index=False)

