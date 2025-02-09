import datetime 
import pandas as pd
import glob

# Read the TL_data.csv file
df = pd.read_csv('Data/TL_data.csv')

# get EM data
csv_files = glob.glob('Data/Quantified_messages/*.csv')
csv_files = [f for f in csv_files if  f.split('_')[2]=='EM']

df_em = pd.read_csv(csv_files[0])


# align dates
start_date = datetime.datetime(2024, 11, 30, 0, 0, 0)
end_date = datetime.datetime(2024, 12, 31, 0, 0, 0)

df['start'] = pd.to_datetime(df['end'])
df['end'] = pd.to_datetime(df['end'])

df_december = df[(df['start'] >= start_date) & (df['start'] <= end_date)]

TL_sum_dec = df_december['quantity_value-6060'].sum()
EM_sum_dec = df_em['quantity_value-6060'].sum()

print(f"December TL: {TL_sum_dec} \nDecember EM: {EM_sum_dec} \nDifference: {((TL_sum_dec - EM_sum_dec)/EM_sum_dec)*100:.2f}%")



