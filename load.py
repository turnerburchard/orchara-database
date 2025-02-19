import os
import psycopg2
import json
from dotenv import load_dotenv
from util import format_date


def get_connection():
    """
    Establishes a PostgreSQL connection using credentials from the .env file.
    """
    load_dotenv()  # Ensure .env variables are loaded
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )


def safe_convert(val):
    """
    If val is a dict or list, returns its JSON string representation.
    Otherwise, returns val unchanged.
    """
    return json.dumps(val) if isinstance(val, (dict, list)) else val


COLUMNS = [
    {"name": "id", "definition": "SERIAL PRIMARY KEY"},
    {"name": "doi", "definition": "TEXT UNIQUE", "extractor": lambda item: item.doi},
    {"name": "isbn", "definition": "TEXT", "extractor": lambda item: safe_convert(item.isbn)},
    {"name": "url", "definition": "TEXT", "extractor": lambda item: item.url},
    {"name": "resource_url", "definition": "TEXT", "extractor": lambda item: item.resource_url},
    {"name": "member", "definition": "TEXT", "extractor": lambda item: item.member},
    {"name": "created_timestamp", "definition": "BIGINT", "extractor": lambda item: item.created_timestamp},
    {"name": "issn", "definition": "JSONB", "extractor": lambda item: safe_convert(item.issn)},
    {"name": "container_title", "definition": "JSONB", "extractor": lambda item: safe_convert(item.container_title)},
    {"name": "issued_date", "definition": "DATE", "extractor": lambda item: item.issued_date},
    {"name": "authors", "definition": "JSONB", "extractor": lambda item: safe_convert(item.authors)},
    {"name": "paper_references", "definition": "JSONB", "extractor": lambda item: safe_convert(item.paper_references)},
    {"name": "abstract", "definition": "TEXT", "extractor": lambda item: item.abstract},
    {"name": "title", "definition": "TEXT", "extractor": lambda item: item.title},
    {"name": "alternative_id", "definition": "JSONB", "extractor": lambda item: safe_convert(item.alternative_id)},
    {"name": "article_number", "definition": "TEXT", "extractor": lambda item: item.article_number},
    {"name": "language", "definition": "TEXT", "extractor": lambda item: item.language},
    {"name": "license", "definition": "JSONB", "extractor": lambda item: safe_convert(item.license)},
    {"name": "link", "definition": "JSONB", "extractor": lambda item: safe_convert(item.link)},
    {"name": "original_title", "definition": "TEXT", "extractor": lambda item: item.original_title},
    {"name": "page", "definition": "TEXT", "extractor": lambda item: item.page},
    {"name": "prefix", "definition": "TEXT", "extractor": lambda item: item.prefix},
    {"name": "published_date", "definition": "DATE", "extractor": lambda item: item.published_date},
    {"name": "publisher", "definition": "TEXT", "extractor": lambda item: item.publisher},
    {"name": "short_container_title", "definition": "TEXT", "extractor": lambda item: safe_convert(item.short_container_title)},
    {"name": "volume", "definition": "TEXT", "extractor": lambda item: item.volume},
    {
        "name": "embedding",
        "definition": "vector(3)",
        "extractor": lambda item: ("[" + ",".join(map(str, item.embedding)) + "]") if item.embedding is not None else None,
        "placeholder": "(%s)::vector(3)"
    }
]



def create_table_if_not_exists(cur):
    """
    Creates the pgvector extension and the papers table dynamically.
    """
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    schema = ",\n    ".join(f"{col['name']} {col['definition']}" for col in COLUMNS)
    cur.execute(f"CREATE TABLE IF NOT EXISTS public.papers (\n    {schema}\n);")
    cur.connection.commit()


def insert_item(cur, item):
    """
    Inserts a record into the papers table using dynamic query construction and UPSERT semantics.
    """
    # Exclude the auto-generated 'id'
    insert_cols = [col["name"] for col in COLUMNS if col["name"] != "id"]
    placeholders = [col.get("placeholder", "%s") for col in COLUMNS if col["name"] != "id"]

    query = f"""
        INSERT INTO public.papers (
            {", ".join(insert_cols)}
        ) VALUES (
            {", ".join(placeholders)}
        )
        ON CONFLICT (doi) DO UPDATE SET
            {", ".join(f"{col} = EXCLUDED.{col}" for col in insert_cols if col != "doi")}
    """

    values = [col["extractor"](item) for col in COLUMNS if col["name"] != "id"]
    cur.execute(query, values)
