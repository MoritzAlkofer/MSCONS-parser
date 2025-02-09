# ⚡ MSCONS Message Parser & Structurer  

## 📌 Overview  
This project provides a **robust parser and structurer** for **MSCONS (Metered Services Consumption)** messages, which are used for exchanging energy consumption data.  

It consists of two key functionalities:  
1. **Parse Interchange** → Converts raw EDIFACT messages into structured JSON.  
2. **Structure Interchange** → Organizes parsed data into a hierarchical format for easier processing.  

---

## 🚀 Features  
✅ **Parses MSCONS EDIFACT Messages** → Extracts key segments (UNB, NAD, QTY, etc.).  
✅ **Structures Data Hierarchically** → Groups elements into SG5-SG10, maintaining logical relationships.  
✅ **Supports Time-Series (TL) & Monthly Data (EM)** → Handles detailed load profiles & aggregated values.  
✅ **Handles Market Roles** → Identifies sender/receiver for validation.  

## 📌 Additional Features (In Development)
Beyond its core functionalities, this project is being extended with several non-core features to enhance usability and analysis:

✅ Data Visualization → Generate plots and summaries of energy consumption trends.
✅ Validation & Error Handling → Detect inconsistencies in message formatting and content.
✅ Aggregation & Filtering → Extract and analyze specific periods, meters, or energy types.
✅ Export & Reporting → Convert structured data into tabular formats for further processing.

📌 Note: These features are still under development and will be refined over time. 🚀

---

## 📥 Parsing MSCONS Messages

The parse interchange function reads raw MSCONS EDIFACT messages and converts them into a structured JSON format.

🔹 Example Usage

📝 Input (Raw MSCONS Segment)
```plaintext
UNB+UNOC:3+9905048000007:500+9985046000001:500+250101:1254+CS0000000G144K++EM
```

🔄 Processing
The parse_interchange() function reads this raw EDIFACT segment and extracts key elements

```python
from reading import parse_interchange

# Load raw MSCONS message
with open("Data/Messages/sample_message.txt", "r") as f:
    raw_message = f.read()

# Parse the message
parsed_message = parse_interchange(raw_message)

# Save parsed output
with open("Data/Parsed_Messages/sample_message.json", "w") as f:
    json.dump(parsed_message, f, indent=4)
```

📤 Output (Parsed JSON Structure)
```json
{
    "segment_tag": "UNB",
    "syntax": {
        "identifier-0001": "UNOC",
        "version-0002": "3"
    },
    "sender": {
        "id-0004": "9905048000007",
        "qualifier-0007": "500"
    },
    "receiver": {
        "id-0010": "9985046000001",
        "qualifier-0007": "500"
    },
    "datetime": {
        "date-0017": "250101",
        "time-0019": "1254"
    },
    "reference-0020": "CS0000000G144K",
    "application_ref-0026": "EM"
}
```

📌 **What It Does** \
✔ Extracts segment data → Reads UNA, UNB, UNH, QTY, DTM, STS segments. \
✔ Handles delimiters → Uses EDIFACT rules to split elements.\  
✔ Stores messages as JSON → Converts EDIFACT to a structured dictionary. \

--- 

## 📂 Structuring the Parsed Message

The structure interchange function organizes the parsed flat JSON into a hierarchical format, making it easier to work with.

🔹 Example Usage

```python
from reading import parse_interchange

# Load raw MSCONS message
with open("Data/Parsed_interchanges/sample_message.json", "r") as f:
    parsed_message = json.load(f)

# Structure the message
structured_message = structure_message(parsed_message)

# Save parsed output
with open("Data/Structured_interchanges/sample_message.json", "w") as f:
    json.dump(structured_message, f, indent=4)
```

📌 **Structuring the Parsed Message** \
Each segment in the parsed MSCONS message is now assigned a unique hierarchical key, reflecting its position within the message structure.

For example, a status segment (STS) within a specific delivery party (SG5), meter (SG6), product/service (SG9), and quantity (SG10) is addressed as:

```plaintext
"SG5.1.SG6.1.SG9.1.SG10.1.STS.1"
```

Since this is the first UNB segment in the message, it is assigned the key UNB.1, indicating its position as the initial interchange header.

```json
"UNB.1": {
            "segment_tag": "UNB",
            "syntax": {
                "identifier-0001": "UNOC",
                "version-0002": "3"
            },
            "sender": {
                "id-0004": "9905048000007",
                "qualifier-0007": "500"
            },
            "receiver": {
                "id-0010": "9985046000001",
                "qualifier-0007": "500"
            },
            "datetime": {
                "date-0017": "250101",
                "time-0019": "1254"
            },
            "reference-0020": "CS0000000G144K",
            "application_ref-0026": "EM"
        }
```

This ensures a logical and easily navigable structure, preserving relationships between different elements of the message. 🚀

📌 **What It Does** \
✔ Groups segments logically → SG5 (Delivery), SG6 (Meter), SG9 (Product), SG10 (Quantity). \
✔ Attaches time references → Links DTM values to SG10 or SG6 correctly. \
✔ Supports nested parsing → Ensures hierarchical relationships are preserved. 

--- 

### 📝 Roadmap

- Implement advanced validation checks
- Improve logging & error handling
- Add Timezone-Aware Datetime Parsing → Correctly processes timestamps from `DTM` segments.  
- Gain better understanding of STS segments and their usage.

--- 

### 📚 References

- [MSCONS Documentation](https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_36/Anlagen/MSCONS_AHB_3_1d_20231024.pdf?__blob=publicationFile&v=1)