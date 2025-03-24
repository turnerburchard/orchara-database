from typing import Optional, Any, List, Dict

import numpy as np
from numpy._typing import NDArray
from dataclasses import dataclass, field

# TODO: fix the "Any"

@dataclass
class Item:
    """
    Represents a processed academic paper with standardized fields.
    
    This class defines the structure for papers that have been transformed
    and are ready to be loaded into the database. It includes both metadata
    fields and vector embeddings for semantic search.
    
    Attributes:
        id: Auto-incrementing primary key (set by database)
        doi: Digital Object Identifier (unique identifier)
        url: Direct URL to the paper
        resource_url: Primary resource URL
        container_title: Journal or publication title (JSONB)
        issued_date: Publication issue date (YYYY-MM-DD format)
        authors: List of paper authors (JSONB)
        paper_references: List of paper references (JSONB)
        abstract: Paper abstract text
        title: Paper title
        link: Related links (JSONB)
        published_date: Publication date (YYYY-MM-DD format)
        publisher: Publisher information
        embedding: Vector embedding for semantic search (384 dimensions)
    """
    id: Optional[int] = None  # SERIAL PRIMARY KEY
    doi: Optional[str] = None
    url: Optional[str] = None
    resource_url: Optional[str] = None
    container_title: Any = None  # JSONB
    issued_date: Optional[str] = None  # DATE
    authors: Any = None  # JSONB
    paper_references: Any = None  # JSONB
    abstract: Optional[str] = None
    title: Optional[str] = None
    link: Any = None  # JSONB
    published_date: Optional[str] = None  # DATE
    publisher: Optional[str] = None
    embedding: NDArray[np.float64] = field(default_factory=lambda: np.array([], dtype=np.float64))
