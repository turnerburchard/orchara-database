"""
Schema definition for the database.
This module contains the COLUMNS definition used by both load.py and validator.py.
"""

COLUMNS = [
    {
        "name": "id",
        "definition": "text PRIMARY KEY",
        "extractor": lambda item: item.id,
        "placeholder": "%s"
    },
    {
        "name": "title",
        "definition": "text",
        "extractor": lambda item: item.title,
        "placeholder": "%s"
    },
    {
        "name": "abstract",
        "definition": "text",
        "extractor": lambda item: item.abstract,
        "placeholder": "%s"
    },
    {
        "name": "authors",
        "definition": "jsonb",
        "extractor": lambda item: item.authors,
        "placeholder": "%s"
    },
    {
        "name": "publication_date",
        "definition": "date",
        "extractor": lambda item: item.publication_date,
        "placeholder": "%s"
    },
    {
        "name": "journal",
        "definition": "text",
        "extractor": lambda item: item.journal,
        "placeholder": "%s"
    },
    {
        "name": "url",
        "definition": "text",
        "extractor": lambda item: item.url,
        "placeholder": "%s"
    },
    {
        "name": "embedding",
        "definition": "vector(384)",
        "extractor": lambda item: ("[" + ",".join(map(str, item.embedding)) + "]") if item.embedding is not None else None,
        "placeholder": "(%s)::vector(384)"
    }
] 