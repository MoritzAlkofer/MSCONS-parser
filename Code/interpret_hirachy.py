import json
import os

# Load the first available structured message
messages = os.listdir('Data/Structured_parsed_messages')
message = messages[0]

with open(f'Data/Structured_parsed_messages/{message}', 'r') as f:
    segments = json.load(f)


def extract_quantity_data(segments):
    # Initialize storage for extracted data
    sg10_data = []

    # Iterate over all SG5, SG6, SG9 dynamically using a counter
    sg5_index = 1
    while f"SG5.{sg5_index}" in segments:
        sg6_index = 1
        while f"SG5.{sg5_index}.SG6.{sg6_index}" in segments:
            sg9_index = 1
            while f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}" in segments:
                sg10_index = 1
                while f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}.SG10.{sg10_index}" in segments:
                    base_path = f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}.SG10.{sg10_index}"

                    # Extract product ID from PIA.1 at SG9 level
                    product_path = f"SG5.{sg5_index}.SG6.{sg6_index}.SG9.{sg9_index}.PIA.1"
                    product_id = segments.get(product_path, {}).get("product_number-7140", "N/A")

                    # Extract values from SG10
                    value = segments[base_path].get("quantity_value-6060", "N/A")
                    qualifier = segments[base_path].get("quantity_qualifier-6063", "N/A")

                    # Extract DTM values (if available)
                    start = segments.get(f"{base_path}.DTM.1", {}).get("value-2380", "N/A")
                    end = segments.get(f"{base_path}.DTM.2", {}).get("value-2380", "N/A")

                    # Extract STS values (if available)
                    sts_index = 1
                    status_category = None
                    status_reason = None
                    while f"{base_path}.STS.{sts_index}" in segments:
                        sts_segment = segments[f"{base_path}.STS.{sts_index}"]
                        status_category = sts_segment.get("status_category_code-9015", "N/A")
                        status_reason = sts_segment.get("status_reason_code-9013", "N/A")
                        sts_index += 1

                    # Append extracted data
                    sg10_data.append({
                        "product_id": product_id,
                        "quantity_value-6060": value,
                        "quantity_qualifier-6063": qualifier,
                        "start": start,
                        "end": end,
                        "status_category": status_category,
                        "status_reason": status_reason
                    })

                    sg10_index += 1  # Move to next SG10
                sg9_index += 1  # Move to next SG9
            sg6_index += 1  # Move to next SG6
        sg5_index += 1  # Move to next SG5

    return sg10_data

if __name__ == '__main__':
    for message in os.listdir('Data/Structured_parsed_messages'):
        segments = json.load(open(f'Data/Structured_parsed_messages/{message}', 'r'))
        quantity_data = extract_quantity_data(segments)
        with open(f'Data/quantity_data/{message}', 'w') as f:
            json.dump(quantity_data, f)