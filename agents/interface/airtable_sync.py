import os
import json
from airtable import Airtable
from optimize_listings import optimize_listing

# Airtable settings
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appF5TYNhZ71SCjco")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Table 1")
AIRTABLE_API_KEY = "patDOB4P58JpLJZV2.e6b6fcffb411881a4152f61b83c166ee84de4de3eb4622e192def0f4e3e61857"
if not AIRTABLE_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

if not AIRTABLE_API_KEY:
    raise RuntimeError("Airtable API key not provided. Set AIRTABLE_API_KEY in environment or .env file.")

airtable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)

# Define the allowed tags based on your Airtable multiple-select field (do NOT include "cat lover" if it's not allowed).
ALLOWED_OPTIMIZED_TAGS = [
    "cat t-shirt", "cat dad gift", "cat mom gift", 
    "funny cat", "cute cat", "cat lover",
    "cat gifts", "cat lover gifts", "cat lover shirt",
    # Include other permitted tags as they appear in your Airtable configuration.
]

def filter_allowed_tags(tags):
    """Filter AI-generated tags so only allowed options are submitted."""
    return [tag for tag in tags if tag in ALLOWED_OPTIMIZED_TAGS]

def run_airtable_optimizer():
    print("Attempting to connect to Airtable and fetch 1 record...")
    try:
        records = airtable.get_all(view="Grid view", max_records=1)
        print(f"✅ Successfully fetched {len(records)} record(s). Connection test PASSED.")
    except Exception as e:
        print(f"❌ Failed to fetch records from Airtable: {e}")
        return

    print("\nProcessing fetched record(s)...")
    for record in records:
        fields = record.get("fields", {})
        record_id = record.get("id")

        # Skip records already processed.
        if fields.get("Status", "").lower() == "optimized":
            continue

        try:
            print(f"Processing: {fields.get('Title', 'No Title')}")
            input_data = {
                "title": fields.get("Title", ""),
                "description": fields.get("Description", ""),
                "tags": fields.get("Tags", ""),
                "product_type": fields.get("Product Type", "")
            }

            optimized = optimize_listing(input_data)
            # Save all raw AI-generated tags in "Suggested Tags"
            suggested_tags = optimized["tags"]
            # Filter the optimized tags based on allowed options (which now excludes "cat lover")
            allowed_tags = filter_allowed_tags(optimized["tags"])
            
            update_data = {
                "Suggested Tags": ", ".join(suggested_tags),  # Free-text field: store raw suggestions
                "Optimized Tags": allowed_tags,               # Multiple-select field: only allowed options
                "Listing Description": optimized["description"],
                "Status": "optimized"
            }

            airtable.update(record_id, update_data)
            print(f"✔ Optimized and updated record {record_id}")

        except Exception as e:
            print(f"✖ Error on record {record_id}: {e}")
            # Update the record with an error status; adjust the status value to an allowed option (e.g., "Error")
            airtable.update(record_id, {
                "Error Logs": str(e),
                "Status": "Error"
            })

if __name__ == "__main__":
    run_airtable_optimizer()