import os 
from reading import parse_interchange
import json
from tqdm import tqdm

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
        interchange = load_interchange(file)    
        parsed_interchange = parse_interchange(interchange)
        save_parsed_interchange(f'Data/Parsed_Messages/{file.strip(".txt")}.json', parsed_interchange)
