import json
import os
import pandas as pd
from structuring import structure_message

def get_market_roles(header):
    SG2_elements = [header[key] for key in header.keys() if 'SG2' in key]
    result = {}
    for SG2_element in SG2_elements:
        result[SG2_element['party_qualifier-3035']] = SG2_element['party_id-3039']
    return result

def extract_data(segments, sg5_index, sg6_index, sg9_index, sg10_index, meetering_point_id, obis_code):
    """Extracts quantity, time period, and status data from an SG10 segment."""
    
    # Construct the base path for SG10
    base_path = f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}.SG10.{sg10_index}"

    # Extract quantity data
    value = segments[base_path].get("quantity_value-6060", "N/A")
    qualifier = segments[base_path].get("quantity_qualifier-6063", "N/A")

    # Extract DTM (Time Period) values
    start = segments.get(f"{base_path}.DTM.1", {}).get("value-2380", "N/A")
    end = segments.get(f"{base_path}.DTM.2", {}).get("value-2380", "N/A")

    # Extract STS (Status) values
    sts_index = 1
    status_category = status_reason = None
    while f"{base_path}.STS.{sts_index}" in segments:
        sts_segment = segments[f"{base_path}.STS.{sts_index}"]
        status_category = sts_segment.get("status_category_code-9015", "N/A")
        status_reason = sts_segment.get("status_reason_code-9013", "N/A")
        sts_index += 1

    # Return structured data
    return {
        "meetering_point_id": meetering_point_id,
        "obis_code": obis_code,
        "quantity_value-6060": value,
        "quantity_qualifier-6063": qualifier,
        "start": start,
        "end": end,
        "status_category": status_category,
        "status_reason": status_reason
    }

def extract_quantity_data(segments):
    # Initialize storage for extracted data
    sg10_data = []

    # Iterate over all SG5, SG6, SG9 dynamically using a counter
    sg5_index = 1

    while f"SG5.{sg5_index}" in segments:
        sg6_index = 1
        while f"SG5.{sg5_index}.SG6.{sg6_index}" in segments:
            # Extract meetering point ID from LOC.1 at SG6 level
            location_path = f"SG5.{sg5_index}.SG6.{sg6_index}"
            meetering_point_id = segments[location_path].get("location_code-3225", "N/A")
            
            sg9_index = 1
            while f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}" in segments:
                # Extract product number from PIA.1 at SG9 level
                location_path = f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}"
                obis_code = segments[location_path+'.PIA.1'].get("product_number-7140", "N/A")
            
                sg10_index = 1
                while f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}.SG10.{sg10_index}" in segments:
                    sg10_data.append(extract_data(segments, sg5_index, sg6_index, sg9_index, sg10_index, meetering_point_id, obis_code))

                    sg10_index += 1  # Move to next SG10
                sg9_index += 1  # Move to next SG9
            sg6_index += 1  # Move to next SG6
        sg5_index += 1  # Move to next SG5

    return sg10_data

if __name__ == '__main__':
    for message in os.listdir('Data/Structured_interchanges'):
        pass
        segments = json.load(open(f'Data/Structured_interchanges/{message}', 'r'))
        
        header = segments['header']
        body = segments['body']
    
        message_type = header['UNB.1']['application_ref-0026']
        market_roles = get_market_roles(header)
        quantity_data = extract_quantity_data(body)
        quantity_data = pd.DataFrame(quantity_data)
        quantity_data['quantity_value-6060'] = quantity_data['quantity_value-6060'].str.replace(',', '.').astype(float)   
        quantity_data['message_type'] = message_type
        quantity_data['Sender'] = market_roles['MS']
        quantity_data['Receiver'] = market_roles['MR']
        quantity_data.to_csv(f'Data/Tabularized_interchanges/{message.strip(".txt")}.csv', index=False)
        