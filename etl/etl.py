import os
from extract import extract_file
from transform.transform import transform_item
from transform.embedder import Embedder
from load import create_table_if_not_exists, insert_item
from util import get_connection
from dotenv import load_dotenv
from validate_db import validate_database
import json
import sys


load_dotenv()
if os.environ.get('SAMPLE_DATA') == 'true':
    DATA_DIR = '/app/data/sample'
else:
    DATA_DIR = '/app/data'


def process_file(filepath, cur):
    print(f"Processing file: {filepath}")
    items = extract_file(filepath)

    embedder = Embedder()

    for item in items:
        processed = transform_item(item)
        if processed is None:
            continue
        processed = embedder.embed_item(processed)
        insert_item(cur, processed)
    cur.connection.commit()
    print(f"Finished processing {filepath}")


def main():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Create table if it doesn't exist
        create_table_if_not_exists(cur)
        
        # Process all files
        data_folder = DATA_DIR
        for filename in os.listdir(data_folder):
            if filename.endswith('.json.gz'):
                filepath = os.path.join(data_folder, filename)
                process_file(filepath, cur)
        
        # Run validation after all files are processed
        print("\nRunning database validation...")
        validation_result = validate_database(conn)
        
        # Write validation results to file
        with open("etl/last_run.json", "w") as f:
            json.dump(validation_result, f, indent=2)
            
        # Exit with error if validation failed
        if not validation_result["validation"]["overall_valid"]:
            print("Validation failed:", validation_result["notes"])
            return 1
            
        print("Validation successful:", validation_result)
        return 0
        
    except Exception as e:
        print(f"Error during ETL process: {str(e)}")
        return 1
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
