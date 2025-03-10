import gzip
import json

def extract_file(filepath):
    """
    Extracts JSON records from a gzipped file.
    Returns the list of items from the JSON (assumes an "items" key).
    """
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("items", [])
