import json
import os
from tqdm import tqdm

class Hierachy:
    def __init__(self):
        self.sg5_count = 0
        self.sg6_count = 0
        self.sg7_count = 0
        self.sg8_count = 0
        self.sg9_count = 0
        self.sg10_count = 0
        self.sts_count = 0
        self.dtm_count = 0
        self.pia_count = 0
        self.last_sg6_key = None
        self.last_sg10_key = None  # Store the last SG10 key for DTM updates

        self.data_structure = {}

    def add_SG5(self, segment):
        """Start a new SG5 (Delivery Party)."""
        self.sg5_count += 1
        self.sg6_count = 0  # Reset SG6 counter for this delivery party
        key = f"SG5.{self.sg5_count}"
        self.data_structure[key] = segment

    def add_SG6(self, segment):
        """Start a new SG6 (Meter Details)."""
        self.sg6_count += 1
        self.sg9_count = 0  # Reset SG9 counter for this meter
        self.last_sg6_key = None
        self.last_sg10_key = None
        key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}"
        self.data_structure[key] = segment
        self.last_sg6_key = key

    def add_SG7(self, segment):
        """Start a new SG7 (Meter References)."""
        self.sg7_count += 1
        key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}.SG7.{self.sg7_count}"
        self.data_structure[key] = segment

    def add_SG8(self, segment):
        """Start a new SG8 (Meter Characteristics)."""
        self.sg8_count += 1
        key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}.SG8.{self.sg8_count}"
        self.data_structure[key] = segment

    def add_SG9(self, segment):
        """Start a new SG9 (Product/Service)."""
        self.sg9_count += 1
        self.sg10_count = 0  # Reset SG10 counter for this product
        self.pia_count = 0
        self.last_sg9_key = None
        key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}.SG9.{self.sg9_count}"
        self.data_structure[key] = segment

    def add_SG10(self, segment):
        """Add a measurement to SG10 (Measurement Details)."""
        self.sg10_count += 1
        self.sts_count = 0
        self.dtm_count = 0
        key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}.SG9.{self.sg9_count}.SG10.{self.sg10_count}"
        self.data_structure[key] = segment
        self.last_sg10_key = key

    def add_DTM_to_SG6_or_SG10(self, segment):
        """Attach DTM (time reference) to either the last SG10 or SG6 if no QTY exists."""
        self.dtm_count += 1  # Increment DTM counter

        # If a QTY (SG10) exists, attach DTM to the last SG10
        if hasattr(self, 'last_sg10_key') and self.last_sg10_key in self.data_structure:
            key = f"{self.last_sg10_key}.DTM.{self.dtm_count}"
            self.data_structure[key] = segment
            return  # Exit after attaching to SG10
        
        # Otherwise, attach DTM to the last SG6 (Meter Details / LOC)
        if hasattr(self, 'last_sg6_key') and self.last_sg6_key in self.data_structure:
            key = f"{self.last_sg6_key}.DTM.{self.dtm_count}"
            self.data_structure[key] = segment
        else:
            print("Warning: No valid SG6 or SG10 found to attach DTM.")

    def add_PIA_to_SG9(self, segment):
        """Attach PIA (Product Identification) to the last SG9."""
        self.pia_count += 1
        key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}.SG9.{self.sg9_count}.PIA.{self.pia_count}"
        self.data_structure[key] = segment

    def add_STS_to_SG10(self, segment):
        """Attach DTM (time reference) to the last SG10."""
        self.sts_count += 1
        if hasattr(self, 'last_sg10_key') and self.last_sg10_key in self.data_structure:
            key = f"SG5.{self.sg5_count}.SG6.{self.sg6_count}.SG9.{self.sg9_count}.SG10.{self.sg10_count}.STS.{self.sts_count}"
            self.data_structure[key] = segment
        else:
            print("Warning: No SG10 exists to attach STS.")

    def get_structure(self):
        return self.data_structure

def parse_detail_segments(detail_segments):
    structure = Hierachy()
    for segment in tqdm(detail_segments):
        if segment['segment_tag'] == 'NAD':
            structure.add_SG5(segment)
        elif segment['segment_tag'] == 'LOC':
            structure.add_SG6(segment)
        elif segment['segment_tag'] == 'RFF':
            structure.add_SG7(segment)
        elif segment['segment_tag'] == 'CCI':
            structure.add_SG8(segment)    
        elif segment['segment_tag'] == 'LIN':
            structure.add_SG9(segment)
        elif segment['segment_tag'] == 'QTY':
            structure.add_SG10(segment)
        elif segment['segment_tag'] == 'STS':
            structure.add_STS_to_SG10(segment)
        elif segment['segment_tag'] == 'DTM':
            structure.add_DTM_to_SG6_or_SG10(segment)
        elif segment['segment_tag'] == 'PIA':
            structure.add_PIA_to_SG9(segment)
        else:
            print(f'cound not parse {segment["segment_tag"]}')
    return structure.get_structure()

def test(detail_segments, structured_detail_segments):
    tags = [detail_segment['segment_tag'] for detail_segment in detail_segments]
    elements = [structured_detail_segments[key]['segment_tag'] for key in structured_detail_segments.keys()]

    set_tags = set(tags)

    for tag in set_tags:
        print(tag, tags.count(tag), elements.count(tag))
        
def split_segments(segments):
    uns_index = next(i for i, segment in enumerate(segments) if segment['segment_tag'] == 'UNS')
    unt_index = next(i for i, segment in enumerate(segments) if segment['segment_tag'] == 'UNT')
    header_segments, detail_segments, summary_segments = segments[:uns_index+1], segments[uns_index+1:unt_index], segments[unt_index:]
    return header_segments, detail_segments, summary_segments

if __name__ == '__main__':  
    for message in os.listdir('Data/Parsed_messages'):
        with open(f'Data/Parsed_messages/{message}', 'r') as f:
            segments = json.load(f)
            print(len(segments))

        header_segments, detail_segments, summary_segments = split_segments(segments)
        structured_detail_segments = parse_detail_segments(detail_segments)

        with open(f'Data/Structured_parsed_messages/{message}', 'w') as f:
            json.dump(structured_detail_segments, f)

    test(detail_segments, structured_detail_segments)