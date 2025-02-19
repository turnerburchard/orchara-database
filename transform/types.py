from typing import Optional, Any

import numpy as np
from numpy._typing import NDArray
from dataclasses import dataclass, field

# TODO: fix the "Any"

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
    embedding: NDArray[np.float64] = field(default_factory=lambda: np.array([], dtype=np.float64))
