from .segment_parser import Segment_parser

def parse_interchange(interchange):
    """
    Parse a complete EDIFACT interchange, including UNA segment and all subsequent segments.

    Args:
        interchange (str): Complete EDIFACT interchange string starting with UNA segment

    Returns:
        list: List of dictionaries containing the parsed segment data.
            Each dictionary contains the parsed fields for that segment type.
            Unknown segments return {'message': 'Unknown segment'}.

    Example:
        >>> interchange = "UNA:+.? 'UNB+UNOC:3+SENDER+RECEIVER+200505:1200+1234'"
        >>> parse_interchange(interchange)
        [
            {
                'segment_tag': 'UNA',
                'component_separator': ':',
                'element_separator': '+',
                'decimal_mark': '.',
                'release_character': '?',
                'repetition_separator': ' ',
                'segment_terminator': "'"
            },
            {
                'segment_tag': 'UNB',
                'syntax': {'identifier': 'UNOC', 'version': '3'},
                'sender': {'id': 'SENDER'},
                'receiver': {'id': 'RECEIVER'},
                'datetime': {'date': '200505', 'time': '1200'},
                'reference': '1234'
            }
        ]
    """
    segment_parser = Segment_parser()
    parsed_segments = []
    
    # First parse UNA segment to get separators
    una_segment = interchange[:9]
    segment_parser.parse_UNA_segment(una_segment)
    
    interchange = interchange[9:]
    # Split remaining interchange into segments and parse each one
    segments = interchange.split(segment_parser.separators['segment_terminator'])
    
    for segment in segments:
        if segment.strip():  # Skip empty segments
            content = segment_parser.parse_segment(segment)
            parsed_segments.append(content)
            
    return parsed_segments

def test(interchange, parsed_interchange):
    interchange = interchange.split("'")

    for i in range(len(parsed_interchange)):
        if parsed_interchange[i]['segment_tag'] == interchange[i+1][:3]:
            pass
        else:
            print(parsed_interchange[i]['segment_tag'])
            print(interchange[i+1][:3])

if __name__ == '__main__':
    with open('../Data/Messages/MSCONS_TL_9905048000007_9985046000001_20250109_CS0000000GAZ65.txt', 'r') as file:
        interchange = file.read()
    parsed_interchange = parse_interchange(interchange)
    
    test(interchange, parsed_interchange)

