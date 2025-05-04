import os
import re
from datetime import datetime

# Configuration
TARGET_FOLDER = "data/mockups/T-Shirts"  # Changed as per user feedback

# Regex for: [Theme]-[Concept]-[Variant]-[Version]-[Date].ext
FILENAME_REGEX = re.compile(
    r"^(?P<theme>[A-Za-z0-9]+)-(?P<concept>[A-Za-z0-9]+)-(?P<variant>Dark|White|LightText|DarkText)-(?P<version>v\d+)-(?P<date>\d{8})\.(?P<ext>png|jpg|jpeg)$"
)

def parse_filename(filename):
    match = FILENAME_REGEX.match(filename)
    if not match:
        return None
    data = match.groupdict()
    # Validate date
    try:
        datetime.strptime(data["date"], "%Y%m%d")
    except ValueError:
        data["date"] = "INVALID"
    return data

def validate_folder(folder):
    print(f"Validating filenames in: {folder}")
    for root, _, files in os.walk(folder):
        for fname in files:
            result = parse_filename(fname)
            if result:
                print(f"OK: {fname} → {result}")
            else:
                print(f"INVALID: {fname}")

if __name__ == "__main__":
    validate_folder(TARGET_FOLDER)
