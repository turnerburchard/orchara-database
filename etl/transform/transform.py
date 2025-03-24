import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import numpy as np

from transform.types import Item
from common.util import safe_convert, format_date


def transform_item(item: Dict[str, Any]) -> Optional[Item]:
    """
    Main entry point for transforming a paper record.
    
    This function orchestrates the transformation process by:
    1. Pruning the input record to remove unnecessary fields
    2. Validating required fields and language
    3. Cleaning and formatting the data
    
    Args:
        item: Raw paper record from the source
        
    Returns:
        Transformed Item instance or None if validation fails
    """
    pruned = prune_item(item)
    if pruned is None:
        return None
    return pruned


def prune_item(item: Dict[str, Any]) -> Optional[Item]:
    """
    Prunes and validates the input record, returning a standardized Item instance.
    
    This function performs several key operations:
    1. Validates required fields (DOI, title, English language)
    2. Cleans and formats the abstract
    3. Extracts and formats dates
    4. Converts complex objects to JSON strings
    
    Args:
        item: Raw paper record from the source
        
    Returns:
        Standardized Item instance or None if validation fails
        
    Note:
        The function ensures that only English papers with valid DOIs
        and titles are processed. It also handles JATS-formatted abstracts
        by extracting only the relevant text content.
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
        url=item.get("URL"),
        resource_url=item.get("resource", {}).get("primary", {}).get("URL"),
        container_title=safe_convert(item.get("container-title")),
        issued_date=(format_date(item.get("issued", {}).get("date-parts", [[]])[0])
                     if item.get("issued", {}).get("date-parts", [[]])[0] else None),
        authors=safe_convert(item.get("author")),
        paper_references=safe_convert(item.get("reference")),
        abstract=abstract,
        title=item.get("title")[0],
        link=safe_convert(item.get("link")),
        published_date=(format_date(item.get("published", {}).get("date-parts", [[]])[0])
                        if item.get("published", {}).get("date-parts", [[]])[0] else None),
        publisher=item.get("publisher"),
        embedding=np.array([])
    )


def clean_abstract(jats_abstract: str) -> str:
    """
    Cleans and formats a JATS-formatted abstract into plain text.
    
    This function:
    1. Parses the JATS XML structure
    2. Extracts only the content from <jats:p> tags
    3. Joins paragraphs with spaces
    4. Normalizes whitespace
    
    Args:
        jats_abstract: Abstract text in JATS XML format
        
    Returns:
        Cleaned abstract text as a single line
        
    Example:
        Input: "<jats:p>First paragraph</jats:p><jats:p>Second paragraph</jats:p>"
        Output: "First paragraph Second paragraph"
    """
    soup = BeautifulSoup(jats_abstract, 'html.parser')
    paragraphs = soup.find_all('jats:p')
    # Join paragraphs with a space and collapse any extra whitespace
    cleaned_text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return " ".join(cleaned_text.split())