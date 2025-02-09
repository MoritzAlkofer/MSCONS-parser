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
✅ **Timezone-Aware Datetime Parsing** → Correctly processes timestamps from `DTM` segments.  

---

## 📥 Parsing MSCONS Messages

The parse interchange function reads raw MSCONS EDIFACT messages and converts them into a structured JSON format.

🔹 Example Usage

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

📌 **What It Does** \
✔ Groups segments logically → SG5 (Delivery), SG6 (Meter), SG9 (Product), SG10 (Quantity). \
✔ Attaches time references → Links DTM values to SG10 or SG6 correctly. \
✔ Supports nested parsing → Ensures hierarchical relationships are preserved. \

--- 

### 📝 Roadmap

- Implement advanced validation checks
- Improve logging & error handling

--- 

### 📚 References

- [MSCONS Documentation](https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/835_mitteilungen_datenformate/Mitteilung_36/Anlagen/MSCONS_AHB_3_1d_20231024.pdf?__blob=publicationFile&v=1)