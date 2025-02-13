import os
import json
import gzip
import psycopg2
from datetime import date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Establish PostgreSQL connection using credentials from .env
conn = psycopg2.connect(
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT')
)
cur = conn.cursor()

def format_date(date_parts):
    """
    Convert a list of date parts [year, month, day] into a YYYY-MM-DD string.
    If parts are missing, returns None.
    """
    if date_parts and len(date_parts) >= 3:
        try:
            # Format month and day with leading zeros if necessary.
            return date(date_parts[0], date_parts[1], date_parts[2]).isoformat()
        except Exception:
            return None
    return None

def process_file(filepath):
    print("Processing file: {}".format(filepath))
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        # Assuming the JSON object has an "items" list
        for item in data.get("items", []):
            doi = item.get("DOI")
            url = item.get("URL")
            resource_url = item.get("resource", {}).get("primary", {}).get("URL")
            member = item.get("member")
            score = item.get("score")
            created_timestamp = item.get("created", {}).get("timestamp")
            # Save ISSN and container-title as JSON strings (arrays) if present
            issn = json.dumps(item.get("ISSN")) if item.get("ISSN") else None
            container_title = json.dumps(item.get("container-title")) if item.get("container-title") else None

            # Process issued date; expected format: { "date-parts": [[2002, 6, 28]] }
            issued_parts = item.get("issued", {}).get("date-parts", [[]])
            issued_date = format_date(issued_parts[0]) if issued_parts and issued_parts[0] else None

            # Authors and references stored as JSON
            authors = json.dumps(item.get("author")) if item.get("author") else None
            paper_references = json.dumps(item.get("reference")) if item.get("reference") else None

            #print("Inserting")
            cur.execute("""
                INSERT INTO public.papers (
                    doi, url, resource_url, member, score,
                    created_timestamp, issn, container_title,
                    issued_date, authors, paper_references
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doi, url, resource_url, member, score,
                created_timestamp, issn, container_title,
                issued_date, authors, paper_references
            ))
    conn.commit()

data_folder = 'data'
for filename in os.listdir(data_folder):
    if filename.endswith('.json.gz'):
        filepath = os.path.join(data_folder, filename)
        print(f"Processing {filepath}...")
        process_file(filepath)

cur.close()
conn.close()
