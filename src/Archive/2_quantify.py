import pandas as pd
import os 
import json
import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

def load_parsed_interchange(file_path):
    with open(file_path, 'r') as f:
        parsed_interchange = json.load(f)
    return parsed_interchange

def convert_time(time):
    time = time.split('+')[0]
    return datetime.datetime.strptime(time, '%Y%m%d%H%M')

def quantify_message(parsed_interchange):
    """
    Extract and structure quantity data from parsed EDIFACT interchange.
    
    Args:
        parsed_interchange (list): List of parsed EDIFACT segments
        
    Returns:
        pd.DataFrame: DataFrame containing structured quantity data
    """
    # Initialize data structure
    data = {
        'message_function_code-1001': [],
        'party_id-3039': [],
        'product_number-7140': [],
        'location_code-3225': [],
        'start': [],
        'end': [],
        'quantity_value-6060': [],
        'quantity_qualifier-6063': []
    }
    
    # Process each segment
    for i, segment in enumerate(parsed_interchange):

        if segment['segment_tag'] == 'BGM':
            message_function_code = segment['document_code-1001']

        if segment['segment_tag'] == 'NAD':
            if segment['party_qualifier-3035'] == 'MR':  # Receiver
                current_party = segment['party_id-3039']
                
        elif segment['segment_tag'] == 'PIA':
            current_product = segment['product_number-7140']

        elif segment['segment_tag'] == 'LOC':
            if segment['location_qualifier-3227'] == '172':
                current_location = segment['location_code-3225']
            
        elif segment['segment_tag'] == 'QTY':
            # Get the quantity segment and following date segments
            qty = parsed_interchange[i]
            start_date = parsed_interchange[i+1]
            end_date = parsed_interchange[i+2]
            
            # Add data to structure
            data['message_function_code-1001'].append(message_function_code)
            data['party_id-3039'].append(current_party)
            data['product_number-7140'].append(current_product)
            data['location_code-3225'].append(current_location)
            data['quantity_value-6060'].append(float(qty['quantity_value-6060'].replace(',', '.')))
            data['quantity_qualifier-6063'].append(qty['quantity_qualifier-6063'])
            data['start'].append(convert_time(start_date['value-2380']))
            data['end'].append(convert_time(end_date['value-2380']))
    
    return pd.DataFrame(data)

def count_reports(parsed_interchange):
    """
    Determines if the interchange is a monthly report by checking the BGM document code.
    Z48 indicates a load profile message, while Z01 indicates a monthly report.

    Args:
        parsed_interchange (list): List of parsed EDI segments

    Returns:
        bool: True if monthly report, False otherwise
    """
    n_report = 0
    for segment in parsed_interchange:
        if segment['segment_tag'] == 'UNH':
            n_report+=1
    return n_report

if __name__ == '__main__':
    folder = 'Data/Parsed_messages'
    for message in tqdm(os.listdir(folder)):
        parsed_interchange = load_parsed_interchange(f'{folder}/{message}')
        df = quantify_message(parsed_interchange)
        if count_reports(parsed_interchange) == 1:
            df.to_csv(f'Data/a_daily_reports/{message.strip(".json")}.csv', index=False)
        else:
            df.to_csv(f'Data/a_monthly_reports/{message.strip(".json")}.csv', index=False)
