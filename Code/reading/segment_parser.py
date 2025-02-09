from utils import split_with_release

class Segment_parser():
    def __init__(self):
        self.separators = {
            'element_separator': '+',
            'component_separator': ':',
            'decimal_mark': '.',
            'release_character': '?',
            'repetition_separator': '*',
            'segment_terminator': ''
        }

    def parse_UNA_segment(self, segment):
        """
        Parse and validate UNA segment according to EDIFACT specifications.
    
        Args:
            UNA_segment (str): The UNA segment string starting with 'UNA' followed by 6 characters
            
        Returns:
            dict: Dictionary containing the parsed self.separators and their meanings
            
        Raises:
            ValueError: If UNA segment is invalid
        """
        # Extract the 6 service characters
        chars = segment[3:9]
        
        set(chars)
        # Check for duplicate characters
        if len(set(chars)) != 6:
            raise ValueError("Each UNA position must use a unique character")
        
        self.separators = {
            'segment_tag': 'UNA', # for debugging
            'element_separator': chars[1], # Default '+' swapped order with component, as elements are higher in hierarchy
            'component_separator': chars[0],    # Default ':'
            'decimal_mark': chars[2],           # Default '.'
            'release_character': chars[3],      # Must be '?'
            'repetition_separator': chars[4],   # Must be '*'
            'segment_terminator': chars[5]      # Default '''
        }
        return self.separators 

    def parse_UNB_segment(self, segment):
        """
        Parse UNB (Nutzdaten-Kopfsegment) segment according to EDIFACT specifications.
        
        Args:
            unb_segment (str): The UNB segment string
            
        Returns:
            dict: Dictionary containing the parsed UNB elements
            
        Raises:
            ValueError: If UNB segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'UNB':
            raise ValueError("Segment must start with 'UNB'")
        

        # Parse the elements according to specification
        result = {
            'segment_tag': 'UNB',
            'syntax': {
                'identifier-0001': None,  # S001
                'version-0002': None      # S001
            },
            'sender': {             # S002
                'id-0004': None,         
                'qualifier-0007': None    
            },
            'receiver': {           # S003
                'id-0010': None,         
                'qualifier-0007': None    
            },
            'datetime': {           # S004
                'date-0017': None,       
                'time-0019': None        
            },
            'reference-0020': None,      
            'application_ref-0026': None 
        }
        
        if len(elements) >= 7:  # Check for all required elements
            # S001 Syntax
            syntax_parts = split_with_release(elements[0], self.separators, self.separators['component_separator'])
            if len(syntax_parts) >= 2:
                result['syntax']['identifier-0001'] = syntax_parts[0]  # 0001 UNOC (mandatory)
                result['syntax']['version-0002'] = syntax_parts[1]     # 0002 3 (mandatory)
            
            # S002 Sender
            sender_parts = split_with_release(elements[1], self.separators, self.separators['component_separator'])
            result['sender']['id-0004'] = sender_parts[0]         # 0004 (mandatory)
            if len(sender_parts) >= 2:
                result['sender']['qualifier-0007'] = sender_parts[1]  # 0007 (required)
            
            # S003 Receiver
            receiver_parts = split_with_release(elements[2], self.separators, self.separators['component_separator'])
            result['receiver']['id-0010'] = receiver_parts[0]         # 0010 (mandatory)
            if len(receiver_parts) >= 2:
                result['receiver']['qualifier-0007'] = receiver_parts[1]  # 0007 (required)
            
            # S004 DateTime
            datetime_parts = split_with_release(elements[3], self.separators, self.separators['component_separator'])
            if len(datetime_parts) >= 2:
                result['datetime']['date-0017'] = datetime_parts[0]  # 0017 YYMMDD (mandatory)
                result['datetime']['time-0019'] = datetime_parts[1]  # 0019 HHMM (mandatory)
            
            # 0020 Reference (mandatory)
            result['reference-0020'] = elements[4]
            
            # S005 (not used) would be elements[5]
            
            # 0026 Application Reference
            result['application_ref-0026'] = elements[6] # 0026 (required)
        
        return result

    def parse_UNH_segment(self, segment):
            """Parse UNH (Message Header) segment from EDIFACT message.
            
            The UNH segment contains the message reference number and message type identification.
            
            Args:
                segment (str): The UNH segment string to parse
                
            Returns:
                dict: Parsed UNH data with the following structure:
                    - message_reference-0062: Reference number that uniquely identifies the message
                    - message_type (S009):
                        - message_type_id-0065: Type of message (e.g. MSCONS)
                        - message_version-0052: Version number (e.g. D)
                        - message_release-0054: Release number (e.g. 04B) 
                        - controlling_agency-0051: Agency controlling the message (e.g. UN)
                        - association_code-0057: Association assigned code (e.g. 2.4b)
                        - common_access_ref-0068: Common access reference (optional)
                    - transmission (S010, optional):
                        - sequence_number-0070: Message sequence number
                        - sequence_status-0073: First/last message indicator
            """
            elements = split_with_release(segment, self.separators, self.separators['element_separator'])
            
            result = {
                'segment_tag': 'UNH',
                'message_reference-0062': None,
                'message_type': {  # S009
                    'message_type_id-0065': None,        # MSCONS
                    'message_version-0052': None,        # D
                    'message_release-0054': None,        # 04B
                    'controlling_agency-0051': None,     # UN
                    'association_code-0057': None,       # 2.4b
                    'common_access_ref-0068': None       # Optional
                },
                'transmission': {  # S010 Optional
                    'sequence_number-0070': None,
                    'sequence_status-0073': None
                }
            }
            
            # Parse message reference
            result['message_reference-0062'] = elements[1]
            
            # Parse message type components
            message_type = elements[2].split(self.separators['component_separator'])
            result['message_type']['message_type_id-0065'] = message_type[0]
            result['message_type']['message_version-0052'] = message_type[1]
            result['message_type']['message_release-0054'] = message_type[2]
            result['message_type']['controlling_agency-0051'] = message_type[3]
            result['message_type']['association_code-0057'] = message_type[4]
            
            # Optional common access reference
            if len(message_type) > 5:
                result['message_type']['common_access_ref-0068'] = message_type[5]
                
            # Optional transmission info
            if len(elements) > 3:
                transmission = elements[3].split(self.separators['component_separator'])
                result['transmission']['sequence_number-0070'] = transmission[0]
                if len(transmission) > 1:
                    result['transmission']['sequence_status-0073'] = transmission[1]
                
            return result

    def parse_BGM_segment(self, segment):
        # parse segment
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        # ensure its a BGM
        if segment_tag != 'BGM':
            raise ValueError("Segment is not a BGM")
        
        # parse BGM elements
        bgm_result = {
            'segment_tag': 'BGM',
            'document_code-1001': None,
            'document_name-1001': None,
            'document_number-1004': None,
            'message_function_code-1225': None
        }

        # interpretation of BGM elements
        bgm_document_code_interpretation = {
            '7': 'Prozessdatenbericht',
            '270': 'Lieferschein',
            'BK': 'Zeitreihen im Rahmen der Bilanzkreisabrechnung',
            'Z06': 'normiertes Profil',
            'Z15': 'EEG-Überführungszeitreihe',
            'Z16': 'Profilschar',
            'Z20': 'Vergangenheitswerte für TEP mit Referenzmessung',
            'Z21': 'Gasbeschaffenheitsdaten',
            'Z23': 'Bilanzierte Menge (MMMA)',
            'Z24': 'Allokationsliste (MMMA)',
            'Z27': 'Bewegungsdaten im Kalenderjahr vor Lieferbeginn',
            'Z28': 'Energiemenge und Leistungsmaximum',
            'Z39': 'Tägliche Summenzeitreihe',
            'Z41': 'Lieferschein Grund- / Arbeitspreis',
            'Z42': 'Lieferschein Arbeits- / Leistungspreis',
            'Z43': 'Redispatch Ausfallarbeitsüberführungszeitreihe',
            'Z44': 'Redispatch Übermittlung von meteorologischen Daten',
            'Z45': 'Redispatch Einzelzeitreihe Ausfallarbeit',
            'Z46': 'Redispatch Ausfallarbeitssummenzeitreihe',
            'Z48': 'Lastgang Marktlokation, Tranche',
            'Z50': 'Redispatch EEG-Überführungszeitreihe aufgrund Ausfallarbeit',
            'Z69': 'Redispatch tägliche Ausfallarbeitsüberführungszeitreihe',
            'Z83': 'Werte nach Typ 2'
        }
        if len(elements) >= 3:  # Changed to >= since we need exactly 3 elements
            bgm_result['document_code-1001'] = elements[0]
            if elements[0] in bgm_document_code_interpretation:  # Add check to avoid KeyError
                bgm_result['document_name-1001'] = bgm_document_code_interpretation[elements[0]]
            bgm_result['document_number-1004'] = elements[1]
            bgm_result['message_function_code-1225'] = elements[2]

        return bgm_result

    def parse_DTM_segment(self, segment):
            """
            Parse DTM (Datum/Uhrzeit/Zeitspanne) segment according to EDIFACT specifications.
            
            Args:
                dtm_segment (str): The DTM segment string
                
            Returns:
                dict: Dictionary containing the parsed DTM elements
                
            Raises:
                ValueError: If DTM segment is invalid
            """

            segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
            datetime_element = elements[0]
            if not segment_tag == 'DTM':
                raise ValueError("Segment must start with 'DTM'")
            
            result = {
                'segment_tag': 'DTM',
                'function_code-2005': None,    # 2005
                'value-2380': None,            # 2380
                'format_code-2379': None       # 2379
            }
            if len(elements) >= 1:
                datetime_components = split_with_release(datetime_element, self.separators, self.separators['component_separator'])

                if len(datetime_components) >= 2:
                    result['function_code-2005'] = datetime_components[0]  # e.g., 137
                    result['value-2380'] = datetime_components[1]         # actual date/time value
                    result['format_code-2379'] = datetime_components[2]   # e.g., 303
            
            return result
    
    def parse_NAD_segment(self, segment):
        """
        Parse NAD (Name and Address) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The NAD segment string
            
        Returns:
            dict: Dictionary containing the parsed NAD elements
            
        Raises:
            ValueError: If NAD segment is invalid
        """
        result = {
            'segment_tag': 'NAD',
            'party_qualifier-3035': None,
            'party_id-3039': None,
            'code_list-1131': None,
            'resp_agency-3055': None
        }
        
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'NAD':
            raise ValueError("Segment must start with 'NAD'")
            
        # First element is the party qualifier (3035)
        result['party_qualifier-3035'] = elements[0]
        
        # Second element contains party identification (C082)
        if len(elements) > 1:
            party_id_components = elements[1].split(self.separators['component_separator'])
            result['party_id-3039'] = party_id_components[0]  # party_id
            if len(party_id_components) > 1:
                result['code_list-1131'] = party_id_components[1]  # code_list
            if len(party_id_components) > 2:
                result['resp_agency-3055'] = party_id_components[2]  # resp_agency
            
        return result

    def parse_RFF_segment(self, segment):
        """
        Parse RFF (Reference) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The RFF segment string
       
                
        Returns:
            dict: Dictionary containing the parsed RFF elements with reference qualifier and identifier
                
        Raises:
            ValueError: If RFF segment is invalid
        """

        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        if segment_tag != 'RFF':
            raise ValueError("Segment must start with 'RFF'")
        
        rff_result = {
            'segment_tag': 'RFF',
            'qualifier-1153': None,  # AGI or ACW
            'identifier-1154': None  # Reference number
        }

        # parse RFF elements
        components = split_with_release(elements[0], self.separators, self.separators['component_separator'])
        if len(components) >= 2:
            rff_result['qualifier-1153'] = components[0]
            rff_result['identifier-1154'] = components[1]
                
        return rff_result

    def parse_PIA_segment(self, segment):
        """
        Parse PIA (Product Identification) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The PIA segment string
            
        Returns:
            dict: Dictionary containing the parsed PIA elements
            
        Raises:
            ValueError: If PIA segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if segment_tag != 'PIA':
            raise ValueError("Segment must start with 'PIA'")
            
        result = {
            'segment_tag': 'PIA',
            'qualifier-4347': None,  # Product qualifier (5 = Product identification)
            'product_number-7140': None,  # Product/service number (OBIS code)
            'product_type-7143': None     # Code type (SRW, Z02, Z08)
        }
        
        if len(elements) >= 2:
            result['qualifier-4347'] = elements[0]
            product_components = split_with_release(elements[1], self.separators, self.separators['component_separator'])
            if len(product_components) >= 2:
                result['product_number-7140'] = product_components[0]
                result['product_type-7143'] = product_components[1]
                
        return result

    def parse_QTY_segment(self, segment):
        """
        Parse QTY (Quantity) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The QTY segment string
            
        Returns:
            dict: Dictionary containing the parsed QTY elements
            
        Raises:
            ValueError: If QTY segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if segment_tag != 'QTY':
            raise ValueError("Segment must start with 'QTY'")
            
        result = {
            'segment_tag': 'QTY',
            'quantity_qualifier-6063': None,  # Quantity qualifier (220, 67, 201, etc.)
            'quantity_value-6060': None,      # Actual quantity value
            'quantity_unit-6411': None        # Unit of measurement (KWH, KWT, etc.)
        }
        
        if len(elements) >= 1:
            quantity_components = split_with_release(elements[0], self.separators, self.separators['component_separator'])
            if len(quantity_components) >= 2:
                result['quantity_qualifier-6063'] = quantity_components[0]
                result['quantity_value-6060'] = quantity_components[1]
                if len(quantity_components) >= 3:
                    result['quantity_unit-6411'] = quantity_components[2]
                
        return result

    def parse_UNS_segment(self, segment):
        """
        Parse UNS (Section Control) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The UNS segment string
            
        Returns:
            dict: Dictionary containing the parsed UNS elements
            
        Raises:
            ValueError: If UNS segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if segment_tag != 'UNS':
            raise ValueError("Segment must start with 'UNS'")
            
        result = {
            'segment_tag': 'UNS',
            'section_id-0081': None  # Section identifier (D)
        }
        
        if len(elements) >= 1:
            result['section_id-0081'] = elements[0]
                
        return result

    def parse_LOC_segment(self, segment):
        """Parse LOC (Location) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The LOC segment string
            
        Returns:
            dict: Dictionary containing the parsed LOC elements with structure:
                - location_qualifier-3227: Location qualifier (e.g. 237 for balancing group)
                - location_code-3225: Location code (balancing group to)
                - first_related_code-3223: First related location code (balancing group from)
                    
        Raises:
            ValueError: If LOC segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'LOC':
            raise ValueError("Segment must start with 'LOC'")
            
        result = {
            'segment_tag': 'LOC',
            'location_qualifier-3227': None,
            'location_code-3225': None,
            'first_related_code-3223': None
        }
        
        # Location qualifier (3227)
        if len(elements) >= 1:
            result['location_qualifier-3227'] = elements[0]
            
        # Location identification (C517)
        if len(elements) >= 2:
            location_id = elements[1].split(self.separators['component_separator'])
            if len(location_id) >= 1:
                result['location_code-3225'] = location_id[0]
                
        # Related location 1 (C519)
        if len(elements) >= 3:
            related_loc = elements[2].split(self.separators['component_separator'])
            if len(related_loc) >= 1:
                result['first_related_code-3223'] = related_loc[0]
                
        return result

    def parse_LIN_segment(self, segment):
        """Parse LIN (Line Item) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The LIN segment string
            
        Returns:
            dict: Dictionary containing the parsed LIN elements with structure:
                - line_item_number-1082: Line item number (natural number including 0)
                    
        Raises:
            ValueError: If LIN segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'LIN':
            raise ValueError("Segment must start with 'LIN'")
            
        result = {
            'segment_tag': 'LIN',
            'line_item_number-1082': None
        }
        
        # Line item number (1082)
        if len(elements) >= 1:
            result['line_item_number-1082'] = elements[0]
                
        return result

    def parse_STS_segment(self, segment):
        """Parse STS (Status) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The STS segment string
            
        Returns:
            dict: Dictionary containing the parsed STS elements with structure:
                - status_category_code-9015: Status category code (Z33 for plausibility note)
                - status_reason_code-9013: Status reason code (Z83-Z87, ZC3, ZR5, ZS2)
                    
        Raises:
            ValueError: If STS segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'STS':
            raise ValueError("Segment must start with 'STS'")
            
        result = {
            'segment_tag': 'STS',
            'status_category_code-9015': None,
            'status_reason_code-9013': None
        }
        
        # Status category (C601)
        if len(elements) >= 1:
            status_category = elements[0].split(self.separators['component_separator'])
            if len(status_category) >= 1:
                result['status_category_code-9015'] = status_category[0]
                
        # Status reason (C556)
        if len(elements) >= 3:
            status_reason = elements[2].split(self.separators['component_separator'])
            if len(status_reason) >= 1:
                result['status_reason_code-9013'] = status_reason[0]
                
        return result

    def parse_UNT_segment(self, segment):
        """Parse UNT (Message Trailer) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The UNT segment string
            
        Returns:
            dict: Dictionary containing the parsed UNT elements with structure:
                - number_of_segments-0074: Number of segments in the message
                - message_reference_number-0062: Message reference number from UNH
                    
        Raises:
            ValueError: If UNT segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'UNT':
            raise ValueError("Segment must start with 'UNT'")
            
        result = {
            'segment_tag': 'UNT',
            'number_of_segments-0074': None,
            'message_reference_number-0062': None
        }
        
        # Number of segments (0074)
        if len(elements) >= 1:
            result['number_of_segments-0074'] = elements[0]
                
        # Message reference number (0062)
        if len(elements) >= 2:
            result['message_reference_number-0062'] = elements[1]
                
        return result

    def parse_UNZ_segment(self, segment):
        """Parse UNZ (Interchange Trailer) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The UNZ segment string
            
        Returns:
            dict: Dictionary containing the parsed UNZ elements with structure:
                - interchange_control_count-0036: Number of messages/groups in interchange
                - interchange_control_reference-0020: Reference matching UNB
                    
        Raises:
            ValueError: If UNZ segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if not segment_tag == 'UNZ':
            raise ValueError("Segment must start with 'UNZ'")
            
        result = {
            'segment_tag': 'UNZ',
            'interchange_control_count-0036': None,
            'interchange_control_reference-0020': None
        }
        
        # Interchange control count (0036)
        if len(elements) >= 1:
            result['interchange_control_count-0036'] = elements[0]
                
        # Interchange control reference (0020)
        if len(elements) >= 2:
            result['interchange_control_reference-0020'] = elements[1]
                
        return result

    def parse_CTA_segment(self, segment):
        """Parse CTA (Contact Information) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The CTA segment string
            
        Returns:
            dict: Dictionary containing the parsed CTA elements with structure:
                - contact_function_code-3139: Function of the contact (e.g., "IC" for Information Center)
                - department_code-3413: Not used (as per specification)
                - department_name-3412: Department or responsible person name
                
        Raises:
            ValueError: If CTA segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if segment_tag != 'CTA':
            raise ValueError("Segment must start with 'CTA'")
        
        result = {
            'segment_tag': 'CTA',
            'contact_function_code-3139': None,
            'department_name-3412': None
        }
        
        # Function of the contact (3139) - Required
        if len(elements) >= 1:
            result['contact_function_code-3139'] = elements[0]
        
        # elements[1] - Department code (3413) - Not used (spec says it's not used)  
        
        # Department or responsible person name (3412) - Required
        if len(elements) >= 3:
            result['department_name-3412'] = elements[2]
        
        return result
    
    def parse_COM_segment(self, segment):
        """Parse COM (Communication Contact) segment according to EDIFACT specifications.
        
        Args:
            segment (str): The COM segment string
            
        Returns:
            dict: Dictionary containing the parsed COM elements with structure:
                - communication_number-3148: Contact number or address
                - communication_qualifier-3155: Type of communication (TE, EM, AJ, AL, FX)
                    
        Raises:
            ValueError: If COM segment is invalid
        """
        segment_tag, *elements = split_with_release(segment, self.separators, self.separators['element_separator'])
        
        if segment_tag != 'COM':
            raise ValueError("Segment must start with 'COM'")
        
        result = {
            'segment_tag': 'COM',
            'communication_number-3148': None,  # Contact number (phone, email, etc.)
            'communication_qualifier-3155': None  # Type (TE, EM, AJ, AL, FX)
        }
        
        # Communication details (C076 composite)
        if len(elements) >= 1:
            communication_details = elements[0].split(self.separators['component_separator'])
            
            if len(communication_details) >= 1:
                result['communication_number-3148'] = communication_details[0]  # e.g., "003222271020"
            
            if len(communication_details) >= 2:
                result['communication_qualifier-3155'] = communication_details[1]  # e.g., "TE" (Telephone)
        
        return result

    def parse_segment(self, segment):
        """Parse a single EDIFACT segment using the appropriate parser based on the segment tag.
        
        Args:
            segment (str): The EDIFACT segment string to parse
                
        Returns:
            dict: Dictionary containing the parsed segment data. Structure varies by segment type.
                For unknown segments, returns {'message': 'Unknown segment'}
                
        Example:
            >>> segment = "UNB+UNOC:3+SENDER+RECEIVER+200505:1200+1234'"
            >>> parse_segment(segment)
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
        if DEI == 'UNA':
            result = self.parse_UNA_segment(segment) # also sets self.separators if UNA
        elif DEI == 'UNB':
            result = self.parse_UNB_segment(segment)
        elif DEI == 'UNH':
            result = self.parse_UNH_segment(segment)
        elif DEI == 'BGM':
            result = self.parse_BGM_segment(segment)
        elif DEI == 'DTM':
            result = self.parse_DTM_segment(segment)
        elif DEI == 'RFF':
            result = self.parse_RFF_segment(segment)
        elif DEI == 'PIA':
            result = self.parse_PIA_segment(segment)
        elif DEI == 'QTY':
            result = self.parse_QTY_segment(segment)
        elif DEI == 'NAD':
            result = self.parse_NAD_segment(segment)
        elif DEI == 'UNS':
            result = self.parse_UNS_segment(segment)
        elif DEI == 'LOC':
            result = self.parse_LOC_segment(segment)
        elif DEI == 'LIN':
            result = self.parse_LIN_segment(segment)
        elif DEI == 'STS':
            result = self.parse_STS_segment(segment)
        elif DEI == 'UNT':
            result = self.parse_UNT_segment(segment)
        elif DEI == 'UNZ':
            result = self.parse_UNZ_segment(segment)
        elif DEI == 'CTA':
            result = self.parse_CTA_segment(segment)
        elif DEI == 'COM':
            result = self.parse_COM_segment(segment)
        
        
        else:
            result = {'message': 'Unknown segment'}
        return result