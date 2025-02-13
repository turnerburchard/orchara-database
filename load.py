import os
import psycopg2
import json
from dotenv import load_dotenv


def get_connection():
    """
    Establishes a PostgreSQL connection using credentials from the .env file.
    """
    load_dotenv()  # Ensure .env variables are loaded
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )
    return conn


def create_table_if_not_exists(cur):
    """
    Creates the pgvector extension and then the papers table (with a unique constraint on DOI)
    if it doesn't already exist.
    """
    # Create pgvector extension if not exists.
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create the table. Note the embedding column is defined as vector(3)
    # and we enforce uniqueness on doi.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS public.papers (
        id SERIAL PRIMARY KEY,
        doi TEXT UNIQUE,
        url TEXT,
        resource_url TEXT,
        member TEXT,
        score REAL,
        created_timestamp BIGINT,
        issn JSONB,
        container_title JSONB,
        issued_date DATE,
        authors JSONB,
        paper_references JSONB,
        embedding vector(3)
    );
    """)
    cur.connection.commit()


def insert_item(cur, item):
    """
    Inserts a processed record into the papers table.
    Uses an UPSERT (ON CONFLICT) to update records if a DOI already exists.
    """
    doi = item.get("DOI")
    url = item.get("URL")
    resource_url = item.get("resource", {}).get("primary", {}).get("URL")
    member = item.get("member")
    score = item.get("score")
    created_timestamp = item.get("created", {}).get("timestamp")
    issn = json.dumps(item.get("ISSN")) if item.get("ISSN") else None
    container_title = json.dumps(item.get("container-title")) if item.get("container-title") else None

    from util import format_date
    issued_parts = item.get("issued", {}).get("date-parts", [[]])
    issued_date = format_date(issued_parts[0]) if issued_parts and issued_parts[0] else None

    authors = json.dumps(item.get("author")) if item.get("author") else None
    paper_references = json.dumps(item.get("reference")) if item.get("reference") else None

    # Convert embedding (a list of floats) to a vector literal string.
    embedding_list = item.get("embedding")
    if embedding_list is not None:
        # Format as '[0.0,0.0,0.0]' (no spaces) which can be cast to vector(3)
        embedding_str = "[" + ",".join(map(str, embedding_list)) + "]"
    else:
        embedding_str = None

    cur.execute("""
        INSERT INTO public.papers (
            doi, url, resource_url, member, score,
            created_timestamp, issn, container_title,
            issued_date, authors, paper_references, embedding
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector(3))
        ON CONFLICT (doi) DO UPDATE SET
            url = EXCLUDED.url,
            resource_url = EXCLUDED.resource_url,
            member = EXCLUDED.member,
            score = EXCLUDED.score,
            created_timestamp = EXCLUDED.created_timestamp,
            issn = EXCLUDED.issn,
            container_title = EXCLUDED.container_title,
            issued_date = EXCLUDED.issued_date,
            authors = EXCLUDED.authors,
            paper_references = EXCLUDED.paper_references,
            embedding = EXCLUDED.embedding;
    """, (
        doi, url, resource_url, member, score,
        created_timestamp, issn, container_title,
        issued_date, authors, paper_references, embedding_str
    ))
