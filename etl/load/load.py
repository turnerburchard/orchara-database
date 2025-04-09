import json
from typing import Any, Dict, List
from psycopg2.extensions import cursor
from .schema import COLUMNS, safe_convert


def safe_convert(val: Any) -> Any:
    """
    Safely converts complex Python objects to JSON strings for database storage.
    
    This function handles the conversion of Python dictionaries and lists
    to JSON strings, while leaving other types unchanged. This is necessary
    for storing complex data structures in PostgreSQL JSONB columns.
    
    Args:
        val: Value to convert
        
    Returns:
        JSON string if input is dict or list, otherwise the original value
    """
    return json.dumps(val) if isinstance(val, (dict, list)) else val


# Define the database schema and extraction logic
COLUMNS: List[Dict[str, Any]] = [
    {"name": "id", "definition": "SERIAL PRIMARY KEY"},
    {"name": "doi", "definition": "TEXT UNIQUE", "extractor": lambda item: item.doi},
    {"name": "url", "definition": "TEXT", "extractor": lambda item: item.url},
    {"name": "resource_url", "definition": "TEXT", "extractor": lambda item: item.resource_url},
    {"name": "container_title", "definition": "JSONB", "extractor": lambda item: safe_convert(item.container_title)},
    {"name": "issued_date", "definition": "DATE", "extractor": lambda item: item.issued_date},
    {"name": "authors", "definition": "JSONB", "extractor": lambda item: safe_convert(item.authors)},
    {"name": "paper_references", "definition": "JSONB", "extractor": lambda item: safe_convert(item.paper_references)},
    {"name": "abstract", "definition": "TEXT", "extractor": lambda item: item.abstract},
    {"name": "title", "definition": "TEXT", "extractor": lambda item: item.title},
    {"name": "link", "definition": "JSONB", "extractor": lambda item: safe_convert(item.link)},
    {"name": "published_date", "definition": "DATE", "extractor": lambda item: item.published_date},
    {"name": "publisher", "definition": "TEXT", "extractor": lambda item: item.publisher},
    {
        "name": "embedding",
        "definition": "vector(384)",
        "extractor": lambda item: ("[" + ",".join(map(str, item.embedding)) + "]") if item.embedding is not None else None,
        "placeholder": "(%s)::vector(384)"
    }
]


def create_table_if_not_exists(cur: cursor) -> None:
    """
    Creates the database table and required extensions if they don't exist.
    
    This function:
    1. Creates the pgvector extension for vector operations
    2. Creates the papers table with all required columns
    3. Uses the COLUMNS definition to dynamically generate the schema
    
    Args:
        cur: Database cursor
        
    Note:
        The function uses IF NOT EXISTS to ensure idempotency.
        The table schema is defined by the COLUMNS list above.
    """
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    schema = ",\n    ".join(f"{col['name']} {col['definition']}" for col in COLUMNS)
    cur.execute(f"CREATE TABLE IF NOT EXISTS public.papers (\n    {schema}\n);")
    cur.connection.commit()


def insert_item(cur: cursor, item: Any) -> None:
    """
    Inserts or updates a paper record in the database using UPSERT logic.
    
    This function:
    1. Constructs a dynamic INSERT query based on the COLUMNS definition
    2. Uses ON CONFLICT (doi) to handle duplicates
    3. Updates all fields except doi when a duplicate is found
    4. Handles special cases like vector embeddings
    
    Args:
        cur: Database cursor
        item: Item instance to insert/update
        
    Note:
        The function uses the DOI as the unique key for upsert operations.
        All complex objects (dicts, lists) are automatically converted to JSON strings.
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
