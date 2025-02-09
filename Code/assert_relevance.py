import json

class MSCONSMessageAnalyzer:
    """Class for analyzing and extracting key information from MSCONS messages."""
    
    def __init__(self):
        pass

    def extract_my_id(self, parsed_segments):
        """Extracts provider ID from NAD segments in a parsed MSCONS message."""
        my_id = None  # Default if not found

        for segment in parsed_segments:
            if segment["segment_tag"] == "NAD" and segment["party_qualifier-3035"] in ["MS", "MR", "DP"]:
                provider_id = segment.get("party_id-3039")
                if provider_id:
                    my_id = provider_id
                    break  # Stop if found

        return my_id
        
    def extract_my_meters(self, parsed_segments):
        """Extracts metering point IDs from the parsed MSCONS message."""
        metering_points = set()

        for segment in parsed_segments:
            if segment["segment_tag"] == "LOC" and segment["location_qualifier-3227"] == "172":
                metering_points.add(segment["location_code-3225"])

        return metering_points

    def extract_allowed_types(self, parsed_segments):
        """Extracts the MSCONS message type from UNB or defaults to 'EM'."""
        return segment.get("message_type", "EM")  # Defaults to EM if missing

    def analyze_message(self, parsed_segments):
        """Extracts key information from a parsed MSCONS message to determine provider relevance."""
        return {
            "my_id": self.extract_my_id(parsed_segments),
            "my_meters": self.extract_my_meters(parsed_segments),
            "message_type": self.extract_allowed_types(parsed_segments)
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

def process_mscons_message(segments, my_id, my_meters, allowed_types):
    """
    Processes an MSCONS message and determines if it is relevant to this energy provider.

    Args:
        segments (dict): Parsed MSCONS segments.
        my_id (str): The energy provider's ID.
        my_meters (set): Set of metering points that belong to this provider.
        allowed_types (set): Set of allowed MSCONS message types (VL, TL, EM).

    Returns:
        dict: A structured dictionary containing message validation and extracted data.
    """
    return {
        "message_for_me": is_message_for_me(segments, my_id),
        "market_roles": get_market_roles(segments, my_id),
        "metering_point_relevant": is_metering_point_relevant(segments, my_meters),
        "valid_message_type": is_relevant_message_type(segments, allowed_types),
        "energy_quantity_present": is_energy_quantity_present(segments)
    }


if __name__ == "__main__":
    
    message = json.load(open("Data/Parsed_messages/MSCONS_EM_9905048000007_9985046000001_20250101_CS0000000G144K.json"))
    message_analyzer = MSCONSMessageAnalyzer()
    result = message_analyzer.analyze_message(message)
    print(message_analyzer.analyze_message())
