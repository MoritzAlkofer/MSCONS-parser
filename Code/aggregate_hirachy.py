import json
import os
import pandas as pd

def load_tables(path, files):
     tables = []
     for file in files:
          table = json.load(open(f'{path}/{file}', 'r'))
          table = pd.DataFrame(table)
          tables.append(table)
     return tables

def drop_duplicates_with_STS(df):
     duplicated_with_STS = df[(df.duplicated(subset='start'))&(~df.status_reason.isna())] 
     df = df.drop(duplicated_with_STS.index)
     return df

def drop_remaining_duplicates(df):
     df = df.sort_values(by=['start', 'quantity_qualifier-6063']).drop_duplicates(subset='start', keep='first')
     df['quantity_value-6060'] = df['quantity_value-6060'].str.replace(',', '.').astype(float)
     return df

def add_220_plus_qualifier(df):
     filter = (df['quantity_qualifier-6063'] == '220+') & (df['status_reason'].isna())
     df.loc[filter,'quantity_qualifier-6063'] = '220+'
     return df

if __name__ == '__main__':
     files = os.listdir('Data/quantity_data')
     files = [file for file in files if file.split('_')[1] == 'TL']
     tables = load_tables('Data/quantity_data', files)
     df = pd.concat(tables).reset_index(drop=True) # merge all tables into one
     df = drop_duplicates_with_STS(df)
     df = drop_remaining_duplicates(df)
     df = add_220_plus_qualifier(df)

     df.to_csv('Data/quantity_data.csv', index=False)