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
     return df

if __name__ == '__main__':
     # load all tables related to TL
     table_names = os.listdir('Data/Tabularized_interchanges')

     tables = load_tables('Data/Tabularized_interchanges', table_names)
     df = pd.concat(tables).reset_index(drop=True) # merge all tables into one
     # sort by status
     df = df.sort_values(by=['start', 'quantity_qualifier-6063'])
     df = df[df['message_type'] == 'TL']
     df = drop_duplicates(df)

     df.to_csv('Data/Aggregated_data.csv', index=False)

