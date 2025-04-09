"""
Database schema definition.
"""
from typing import Any, Dict, List
import json


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