import os
from pyairtable import Api

# Airtable credentials
API_TOKEN = "patDOB4P58JpLJZV2.e6b6fcffb411881a4152f61b83c166ee84de4de3eb4622e192def0f4e3e61857"
BASE_ID = "appF5TYNhZ71SCjco"
TABLE_NAME = "Table 1"

def main():
    api = Api(API_TOKEN)
    print("=== Listing tables in base to verify access ===")
    try:
        base = api.base(BASE_ID)
        tables = base.tables()
        print("Tables found in base:")
        for t in tables:
            print("-", t.name)
    except Exception as e:
        print("Error listing tables:", e)
        return

    print(f"\n=== Attempting to access table '{TABLE_NAME}' ===")
    try:
        table = api.table(BASE_ID, TABLE_NAME)
        print("Table object created successfully.")
    except Exception as e:
        print("Error creating table object:", e)
        return

    print("\n=== Reading first 3 records in table and listing field names ===")
    try:
        records = table.all(max_records=3)
        if records:
            for idx, rec in enumerate(records, 1):
                print(f"Record {idx} fields: {list(rec.get('fields', {}).keys())}")
        else:
            print("No records found in table.")
    except Exception as e:
        print("Error reading records:", e)
        return

    print("\n=== Creating a test record using 'Design Name' field ===")
    test_data = {"Design Name": "Hello from pyairtable!"}
    try:
        created_record = table.create(test_data)
        print("Created record:", created_record)
        record_id = created_record["id"]
    except Exception as e:
        print("Error creating record:", e)
        return

    print("\n=== Deleting the test record ===")
    try:
        table.delete(record_id)
        print("Test record deleted successfully.")
    except Exception as e:
        print("Error deleting test record:", e)

if __name__ == "__main__":
    main()
