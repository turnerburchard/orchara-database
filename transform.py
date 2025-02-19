import re
from dataclasses import dataclass, field
from typing import Any, Optional
from util import safe_convert, format_date



@dataclass
class Item:
    id: Optional[int] = None  # SERIAL PRIMARY KEY
    doi: Optional[str] = None
    isbn: Optional[str] = None
    url: Optional[str] = None
    resource_url: Optional[str] = None
    member: Optional[str] = None
    created_timestamp: Optional[int] = None
    issn: Any = None
    container_title: Any = None
    issued_date: Optional[str] = None  # DATE
    authors: Any = None
    paper_references: Any = None
    abstract: Optional[str] = None
    title: Optional[str] = None
    alternative_id: Any = None
    article_number: Optional[str] = None
    language: Optional[str] = None
    license: Any = None
    link: Any = None
    original_title: Optional[str] = None
    page: Optional[str] = None
    prefix: Optional[str] = None
    published_date: Optional[str] = None  # DATE
    publisher: Optional[str] = None
    short_container_title: Optional[str] = None
    volume: Optional[str] = None
    embedding: Optional[list] = field(default_factory=list)


def transform_item(item):
    """
    Processes an individual record by first pruning and then computing embeddings.
    Returns the processed record or None if pruned.
    """
    pruned = prune_item(item)
    if pruned is None:
        return None
    processed = embed_item(pruned)
    return processed

def prune_item(item: dict) -> Optional[Item]:
    """
    Prunes the input record and returns an Item instance.
    Returns None if the record lacks a DOI or is not in English.
    Additionally, cleans the abstract by removing leading and trailing
    angle-bracketed text.
    """
    if not item.get("DOI"):
        return None
    if item.get("language") != "en":
        return None

    if item.get("abstract"):
        abstract = item["abstract"]
        abstract = re.sub(r'^<[^>]*>\s*', '', abstract)
        abstract = re.sub(r'\s*<[^>]*>$', '', abstract)
        item["abstract"] = abstract

    return Item(
        doi=item.get("DOI"),
        isbn=safe_convert(item.get("ISBN")),
        url=item.get("URL"),
        resource_url=item.get("resource", {}).get("primary", {}).get("URL"),
        member=item.get("member"),
        created_timestamp=item.get("created", {}).get("timestamp"),
        issn=safe_convert(item.get("ISSN")),
        container_title=safe_convert(item.get("container-title")),
        issued_date=(format_date(item.get("issued", {}).get("date-parts", [[]])[0])
                     if item.get("issued", {}).get("date-parts", [[]])[0] else None),
        authors=safe_convert(item.get("author")),
        paper_references=safe_convert(item.get("reference")),
        abstract=item.get("abstract"),
        title=item.get("title"),
        alternative_id=safe_convert(item.get("alternative-id")),
        article_number=item.get("article-number"),
        language=item.get("language"),
        license=safe_convert(item.get("license")),
        link=safe_convert(item.get("link")),
        original_title=item.get("original-title"),
        page=item.get("page"),
        prefix=item.get("prefix"),
        published_date=(format_date(item.get("published", {}).get("date-parts", [[]])[0])
                        if item.get("published", {}).get("date-parts", [[]])[0] else None),
        publisher=item.get("publisher"),
        short_container_title=safe_convert(item.get("short-container-title")),
        volume=item.get("volume"),
        embedding=[]  # Initially empty; will be populated by embed_item.
    )

def embed_item(item: Item) -> Item:
    """
    Embeds the item by first pruning it and then computing a dummy
    3-dimensional embedding (to be replaced with actual logic).
    The embedding is stored as part of the Item instance.
    """

    item.embedding = [0.0, 0.0, 0.0]  # Replace with actual embedding computation.
    return item