import json

class MSCONSMessageAnalyzer:
    """Class for analyzing and extracting key information from MSCONS messages."""
    
    def __init__(self):
        pass
        
    def extract_my_meters(self, parsed_segments):
        """Extracts metering point IDs from the parsed MSCONS message."""
        metering_points = set()

        for segment in parsed_segments:
            if segment["segment_tag"] == "LOC" and segment["location_qualifier-3227"] == "172":
                metering_points.add(segment["location_code-3225"])

        return metering_points

    def analyze_message(self, parsed_segments):
        """Extracts key information from a parsed MSCONS message to determine provider relevance."""
        return {
            "my_id": self.extract_my_id(parsed_segments),
            "my_meters": self.extract_my_meters(parsed_segments),
            "message_type": self.extract_allowed_types(parsed_segments)
            "all"
        }

class MSCONSValidator:
    def __init__(self, segments, my_id, my_meters=None, allowed_types=None):
        self.segments = segments
        self.my_id = my_id
        self.my_meters = my_meters or set()
        self.allowed_types = allowed_types or set()

    def is_message_for_me(self):
        """Check if the MSCONS message is addressed to this provider."""
        for key in self.segments.keys():
            if key.startswith("NAD+MR"):
                recipient_id = self.segments[key].split("+")[2]  # Extracts the recipient ID
                return recipient_id == self.my_id
        return False  # If no recipient ID is found

    def get_market_roles(self):
        """Find all occurrences of the provider ID in market roles."""
        roles = []
        for key, value in self.segments.items():
            if key.startswith("NAD") and self.my_id in value:
                roles.append(key.split("+")[1])  # Extracts role type (MS, MR, DP, etc.)
        return roles

    def is_metering_point_relevant(self):
        """Check if the metering point ID in the message belongs to my provider."""
        for key, value in self.segments.items():
            if key.startswith("LOC+172"):
                metering_point_id = value.split("+")[2]
                return metering_point_id in self.my_meters
        return False

    def is_relevant_message_type(self):
        """Check if the message type is one that this provider processes."""
        unb_segment = self.segments.get("UNB", "")
        message_type = unb_segment.split("+")[-1]  # Extracts last element (VL, TL, EM)
        return message_type in self.allowed_types

    def is_energy_quantity_present(self):
        """Check if the energy quantity is present in the message."""
        for key, value in self.segments.items():
            if key.startswith("QTY+220"):
                return True  # QTY+220 found
        return False  # No QTY+220 found





if __name__ == "__main__":
    
    message = json.load(open("Data/Structured_parsed_messages/MSCONS_EM_9905048000007_9985046000001_20250101_CS0000000G144K.json"))
    
    header = message['header']
    body = message['body']
    footer = message['footer']

    message_type = header['UNB.1']['application_ref-0026']
    market_roles = get_market_roles(header)
    

    SG6_elements = [body[key] for key in body.keys() if 'SG6' in key]
    meters = []
    for SG6_element in SG6_elements:
        meters.append(SG6_element['location_code-3225'])
    