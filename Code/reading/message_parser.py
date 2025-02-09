from .segment_parsers import *

def parse_segment(segment, separators):
    """Parse a single EDIFACT segment using the appropriate parser based on the segment tag.
    
    Args:
        segment (str): The EDIFACT segment string to parse
        separators (dict): Dictionary containing separator characters used in the EDIFACT message
            with keys: element_separator, component_separator, decimal_mark, 
            release_character, repetition_separator, segment_terminator
            
    Returns:
        dict: Dictionary containing the parsed segment data. Structure varies by segment type.
            For unknown segments, returns {'message': 'Unknown segment'}
            
    Example:
        >>> segment = "UNB+UNOC:3+SENDER+RECEIVER+200505:1200+1234'"
        >>> separators = {'element_separator': '+', 'component_separator': ':'}
        >>> parse_segment(segment, separators)
        {
            'segment_tag': 'UNB',
            'syntax': {'identifier': 'UNOC', 'version': '3'},
            'sender': {'id': 'SENDER'},
            'receiver': {'id': 'RECEIVER'},
            'datetime': {'date': '200505', 'time': '1200'},
            'reference': '1234'
        }
    """
    DEI = segment[:3] # Data element identifier
    if DEI == 'UNB':
        result = parse_UNB_segment(segment, separators)
    elif DEI == 'UNH':
        result = parse_UNH_segment(segment, separators)
    elif DEI == 'BGM':
        result = parse_BGM_segment(segment, separators)
    elif DEI == 'DTM':
        result = parse_DTM_segment(segment, separators)
    elif DEI == 'RFF':
        result = parse_RFF_segment(segment, separators)
    elif DEI == 'PIA':
        result = parse_PIA_segment(segment, separators)
    elif DEI == 'QTY':
        result = parse_QTY_segment(segment, separators)
    elif DEI == 'NAD':
        result = parse_NAD_segment(segment, separators)
    elif DEI == 'UNS':
        result = parse_UNS_segment(segment, separators)
    elif DEI == 'LOC':
        result = parse_LOC_segment(segment, separators)
    elif DEI == 'LIN':
        result = parse_LIN_segment(segment, separators)
    elif DEI == 'STS':
        result = parse_STS_segment(segment, separators)
    elif DEI == 'UNT':
        result = parse_UNT_segment(segment, separators)
    elif DEI == 'UNZ':
        result = parse_UNZ_segment(segment, separators)
    else:
        result = {'message': 'Unknown segment'}
    return result

def parse_segments(segments, separators):
        """
        Parse a list of EDIFACT segments using the provided separators.

        Args:
            segments (list): List of EDIFACT segment strings to parse
            separators (dict): Dictionary containing separator characters with keys:
                - element_separator
                - component_separator
                - decimal_mark 
                - release_character
                - repetition_separator
                - segment_terminator

        Returns:
            list: List of dictionaries containing the parsed segment data.
                Each dictionary contains the parsed fields for that segment type.
                Unknown segments return {'message': 'Unknown segment'}.

        Example:
            >>> segments = ["UNB+UNOC:3+SENDER+RECEIVER+200505:1200+1234'", 
                          "UNH+1+ORDERS:D:96A:UN'"]
            >>> separators = {'element_separator': '+', 'component_separator': ':'}
            >>> parse_segments(segments, separators)
            [
                {
                    'segment_tag': 'UNB',
                    'syntax': {'identifier': 'UNOC', 'version': '3'},
                    'sender': {'id': 'SENDER'},
                    'receiver': {'id': 'RECEIVER'},
                    'datetime': {'date': '200505', 'time': '1200'},
                    'reference': '1234'
                },
                {
                    'segment_tag': 'UNH',
                    'message_reference': '1',
                    'message_type': 'ORDERS',
                    'version': 'D',
                    'release': '96A',
                    'agency': 'UN'
                }
            ]
        """
        parsed_segments = []
        for segment in segments:
            if segment.strip():  # Skip empty segments
                content = parse_segment(segment, separators)
                parsed_segments.append(content)
        return parsed_segments

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
    una_segment, interchange = interchange[:9], interchange[9:] # UNA and segments
    separators = parse_UNA_segment(una_segment) # separators
    segments = interchange.split(separators['segment_terminator']) # split interchange into segments
    parsed_interchange = parse_segments(segments, separators) # parse segments
    return parsed_interchange
