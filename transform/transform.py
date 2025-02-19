import re
from typing import Optional
from bs4 import BeautifulSoup
import numpy as np

from transform.types import Item

from util import safe_convert, format_date


def transform_item(item):
    pruned = prune_item(item)
    if pruned is None:
        return None
    return pruned

def prune_item(item: dict) -> Optional[Item]:
    """
    Prunes the input record and returns an Item instance.
    Returns None if the record lacks a DOI or is not in English.
    Additionally, cleans the abstract by removing leading and trailing
    angle-bracketed text.
    """
    if not item.get("DOI"):
        return None
    if not item.get("title"):
        return None
    if item.get("language") != "en":
        return None


    if item.get("abstract"):
        abstract = clean_abstract(item.get("abstract"))
    else:
        abstract = ""

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
        abstract=abstract,
        title=item.get("title")[0],
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
        embedding= np.array([])
    )

def clean_abstract(jats_abstract: str) -> str:
    """
    Extracts text only from <jats:p> tags, concatenating them into a single line.
    This omits any text from tags like <jats:title> and ensures the result is a single line.
    """
    soup = BeautifulSoup(jats_abstract, 'html.parser')
    paragraphs = soup.find_all('jats:p')
    # Join paragraphs with a space and collapse any extra whitespace
    cleaned_text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return " ".join(cleaned_text.split())