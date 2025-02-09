import json
import os
from tqdm import tqdm

        
def split_segments(segments):
    uns_index = next(i for i, segment in enumerate(segments) if segment['segment_tag'] == 'UNS')
    unt_index = next(i for i, segment in enumerate(segments) if segment['segment_tag'] == 'UNT')
    header_segments, body_segments, summary_segments = segments[:uns_index+1], segments[uns_index+1:unt_index], segments[unt_index:]
    return header_segments, body_segments, summary_segments

class HeaderStructure:
    def __init__(self):
        self.unb_count = 0
        self.unh_count = 0
        self.bgm_count = 0
        self.dtm_count = 0
        self.sg1_count = 0
        self.sg2_count = 0
        self.sg4_count = 0
        self.nad_count = 0
        self.cta_count = 0
        self.com_count = 0
        self.uns_count = 0
        self.last_sg1_key = None
        self.last_sg2_key = None
        self.data_structure = {}

    def add_UNB(self, segment):
        """Start a new UNB (Interchange Header)."""
        self.unb_count += 1
        key = f"UNB.{self.unb_count}"
        self.data_structure[key] = segment

    def add_UNH(self, segment):
        """Start a new UNH (Message Header)."""
        key = f"UNH.{self.unh_count}"
        self.data_structure[key] = segment

    def add_BGM(self, segment):
        """Add a BGM (Beginning of Message)."""
        key = f"BGM.{self.unb_count}"
        self.data_structure[key] = segment

    def add_SG1(self, segment):
        """Start a new SG1 (Reference group)."""
        self.sg1_count += 1
        key = f"SG1.{self.sg1_count}"
        self.data_structure[key] = segment
        self.last_sg1_key = key

    def add_DTM(self, segment):
        """Attach a DTM (Date/Time) to the last known context (SG1, SG2, SG4)."""
        self.dtm_count += 1

        # If there's a last SG2 key, attach to SG2  
        if self.last_sg2_key:
            key = f"{self.last_sg2_key}.DTM.{self.dtm_count}"
        # Otherwise, attach to UNB or UNH
        else:
            key = f"DTM.{self.dtm_count}"

        self.data_structure[key] = segment

    def add_SG2(self, segment):
        """Start a new SG2 (Party Identification)."""
        self.sg2_count += 1
        self.sg4_count = 0
        key = f"SG2.{self.sg2_count}"
        self.data_structure[key] = segment
        self.last_sg2_key = key  # Store last SG2 for SG4 linkage

    def add_SG4(self, segment):
        """Start SG4 under the last SG2."""
        self.sg4_count += 1
        self.com_count = 0
        if self.last_sg2_key:
            key = f"{self.last_sg2_key}.SG4.{self.sg4_count}"
            self.data_structure[key] = segment

    def add_COM(self, segment):
        """Attach COM to CTA (inside SG4)."""
        self.com_count += 1
        key = f"{self.last_sg2_key}.SG4.{self.sg4_count}.COM.{self.com_count}"
        self.data_structure[key] = segment

    def add_UNS(self, segment):
        """Attach UNS (Interchange Acknowledgment) to UNB."""
        self.uns_count += 1
        key = f"UNS.{self.uns_count}"
        self.data_structure[key] = segment

    def parse_header_segments(self, header_segments):
        """Processes header segments dynamically."""
        for segment in header_segments:
            if segment["segment_tag"] == "UNB":
                self.add_UNB(segment)
            elif segment["segment_tag"] == "UNH":
                self.add_UNH(segment)
            elif segment["segment_tag"] == "BGM":
                self.add_BGM(segment)
            elif segment["segment_tag"] == "DTM":
                self.add_DTM(segment)
            elif segment["segment_tag"] == "RFF":
                self.add_SG1(segment)
            elif segment["segment_tag"] == "SG2":
                self.add_SG2(segment)
            elif segment["segment_tag"] == "NAD":
                self.add_SG2(segment)
            elif segment["segment_tag"] == "CTA":
                self.add_SG4(segment)
            elif segment["segment_tag"] == "COM":
                self.add_COM(segment)
            elif segment["segment_tag"] == "UNS":
                self.add_UNS(segment)
            else:
                print(f"Could not parse {segment['segment_tag']}")

    def get_structure(self):
        """Returns the parsed header structure."""
        return self.data_structure

class BodyStructure:
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
        """Start a new SG6 (Meter Bodys)."""
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
        """Add a measurement to SG10 (Measurement Bodys)."""
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
        
        # Otherwise, attach DTM to the last SG6 (Meter Bodys / LOC)
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

    def parse_body_segments(self, body_segments):
        for segment in body_segments:
            if segment['segment_tag'] == 'NAD':
                self.add_SG5(segment)
            elif segment['segment_tag'] == 'LOC':
                self.add_SG6(segment)
            elif segment['segment_tag'] == 'RFF':
                self.add_SG7(segment)
            elif segment['segment_tag'] == 'CCI':
                self.add_SG8(segment)    
            elif segment['segment_tag'] == 'LIN':
                self.add_SG9(segment)
            elif segment['segment_tag'] == 'QTY':
                self.add_SG10(segment)
            elif segment['segment_tag'] == 'STS':
                self.add_STS_to_SG10(segment)
            elif segment['segment_tag'] == 'DTM':
                self.add_DTM_to_SG6_or_SG10(segment)
            elif segment['segment_tag'] == 'PIA':
                self.add_PIA_to_SG9(segment)
            else:
                print(f'cound not parse {segment["segment_tag"]}')

    def get_structure(self):
        return self.data_structure

class FooterStructure:
    def __init__(self):
        self.data_structure = {}
    
    def add_UNT(self, segment):
        self.data_structure['UNT.1'] = segment

    def add_UNZ(self, segment):
        self.data_structure['UNZ.1'] = segment

    def parse_footer_segments(self, summary_segments):
        for segment in summary_segments:
            if segment['segment_tag'] == 'UNT':
                self.add_UNT(segment)
            elif segment['segment_tag'] == 'UNZ':
                self.add_UNZ(segment)

    def get_structure(self):
        return self.data_structure

def test(body_segments, structured_body_segments):
    tags = [body_segment['segment_tag'] for body_segment in body_segments]
    elements = [structured_body_segments[key]['segment_tag'] for key in structured_body_segments.keys()]

    set_tags = set(tags)

    for tag in set_tags:
        print(tag, tags.count(tag), elements.count(tag))

if __name__ == '__main__':  
    for message in os.listdir('Data/Parsed_messages'):
        with open(f'Data/Parsed_messages/{message}', 'r') as f:
            segments = json.load(f)
        
        header_segments, body_segments, summary_segments = split_segments(segments)
        
        body_parser = BodyStructure()
        body_parser.parse_body_segments(body_segments)
        structured_body_segments = body_parser.get_structure()

        header_parser = HeaderStructure()
        header_parser.parse_header_segments(header_segments)
        structured_header_segments = header_parser.get_structure()

        footer_parser = FooterStructure()
        footer_parser.parse_footer_segments(summary_segments)
        structured_footer_segments = footer_parser.get_structure()

        structured_message = {
            'header': structured_header_segments,
            'body': structured_body_segments,
            'footer': structured_footer_segments
        }

        with open(f'Data/Structured_parsed_messages/{message}', 'w') as f:
            json.dump(structured_message, f)

    print(f'\nTesting for one sample message {message}')
    print('Test counts the number of each segment tag in the original and structured segments')
    print('\nheader')
    test(header_segments, structured_header_segments)
    print('\nbody')
    test(body_segments, structured_body_segments)
    print('\nfooter')
    test(summary_segments, structured_footer_segments)