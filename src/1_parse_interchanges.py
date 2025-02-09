import os 
from reading import parse_interchange
import json
from tqdm import tqdm
from structuring import structure_message    

def load_interchange(file):
    file_path = f'Data/Messages/{file}'
    with open(file_path, 'r') as f:
        interchange = f.read()
    return interchange

def save_parsed_interchange(path, parsed_interchange):
    with open(path, 'w') as f:
        json.dump(parsed_interchange, f, indent=4)

if __name__ == '__main__':

    for file in  tqdm(os.listdir('Data/Messages/')):
        # parse interchange
        interchange = load_interchange(file)    
        parsed_interchange = parse_interchange(interchange)
        with open(f'Data/Parsed_interchanges/{file.strip(".txt")}.json', 'w') as f:
            json.dump(parsed_interchange, f, indent=4)

        # structure interchange
        structured_interchange = structure_message(parsed_interchange)
        with open(f'Data/Structured_interchanges/{file.strip(".txt")}.json', 'w') as f:
            json.dump(structured_interchange, f, indent=4)
