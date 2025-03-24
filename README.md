# Orchara Database ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for processing academic papers data into a PostgreSQL database with vector embeddings support.

## Overview

The pipeline processes academic paper metadata from various sources, transforms it into a standardized format, and loads it into a PostgreSQL database. The database uses the `pgvector` extension to store embeddings for semantic search capabilities.

## Project Structure

```
orchara-database/
├── docker-compose.yml  # Docker services configuration
├── Dockerfile         # ETL service container definition
├── etl/              # ETL pipeline components
│   ├── load.py       # Database loading logic
│   ├── extract.py    # Data extraction from source
│   ├── validate.py   # Database validation logic
│   └── transform/    # Data transformation logic
│       ├── transform.py
│       └── types.py
├── index/            # Vector indexing and search
│   └── index.py      # Index creation and management
├── data/             # Data directory for paper files
│   └── validation/   # Validation results and reports
└── common/           # Shared utilities
    └── util.py       # Common utility functions
```

Key components:
- `etl/`: Contains the core ETL pipeline logic for processing papers
- `index/`: Handles vector indexing and similarity search functionality
- `data/`: Directory for storing paper data files and validation results
- `common/`: Shared utilities used across the project

## Data Model

The pipeline processes papers with the following key fields:

- `doi`: Digital Object Identifier (unique identifier)
- `url`: Direct URL to the paper
- `resource_url`: Primary resource URL
- `container_title`: Journal or publication title
- `issued_date`: Publication issue date
- `authors`: List of paper authors
- `paper_references`: List of paper references
- `abstract`: Paper abstract
- `title`: Paper title
- `link`: Related links
- `published_date`: Publication date
- `publisher`: Publisher information
- `embedding`: Vector embedding for semantic search (384 dimensions)

## Features

- **Data Validation**: Ensures papers have required fields (DOI, title) and are in English
- **Abstract Cleaning**: Processes JATS-formatted abstracts into clean text
- **Vector Support**: Stores embeddings for semantic search capabilities
- **Upsert Logic**: Handles duplicate entries gracefully using DOI as the unique key
- **JSON Support**: Stores complex data structures (authors, references, etc.) as JSONB
- **Vector Indexing**: Efficient similarity search using HNSW index

## Database Schema

The pipeline creates a PostgreSQL table with the following structure:

```sql
CREATE TABLE public.papers (
    id SERIAL PRIMARY KEY,
    doi TEXT UNIQUE,
    url TEXT,
    resource_url TEXT,
    container_title JSONB,
    issued_date DATE,
    authors JSONB,
    paper_references JSONB,
    abstract TEXT,
    title TEXT,
    link JSONB,
    published_date DATE,
    publisher TEXT,
    embedding vector(384)
);

## Vector Indexing

The pipeline uses HNSW (Hierarchical Navigable Small World) indexing for efficient similarity search:

- **Index Type**: HNSW (Hierarchical Navigable Small World)
- **Distance Metric**: Cosine similarity
- **Parameters**:
  - `m`: 16 (number of connections per layer)
  - `ef_construction`: 64 (size of dynamic candidate list for index construction)
- **Usage**: Enables fast similarity search queries using the `vector_cosine_ops` operator


## Running with Docker

The project uses Docker Compose to manage the database and ETL services:

1. **Start the services**:
```bash
docker-compose up -d
```

2. **View logs**:
```bash
docker-compose logs -f etl
```

3. **Stop the services**:
```bash
docker-compose down
```

### Docker Configuration

- **Database Service**:
  - PostgreSQL 15 with pgvector extension
  - Persistent volume for data storage
  - Exposed on port 5432

- **ETL Service**:
  - Python-based ETL pipeline
  - Mounts local data directory
  - Waits for database to be ready before starting

### Environment Variables

Required environment variables:
- `DB_HOST`: Database host (default: db)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password

## Usage

1. Place your paper data in the `data/papers` directory
2. Start the services using Docker Compose
3. The ETL pipeline will:
   - Transform the data into the standardized format
   - Validate required fields and language
   - Clean and process abstracts
   - Generate embeddings
   - Load the data into the database with upsert logic
   - Create vector indexes for similarity search

## Dependencies

- PostgreSQL with pgvector extension
- Python 3.x
- Required Python packages:
  - numpy
  - beautifulsoup4
  - psycopg2 (or similar PostgreSQL adapter)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Data Validation

The pipeline includes comprehensive data validation that runs after the ETL process completes. Validation results are stored in `data/validation/last_run.json` and include:

- **Table Structure**: Verifies all required columns exist with correct types
- **Data Quality**:
  - Required fields (DOI, title, abstract) are present and non-empty
  - Date ranges are valid
  - No NULL embeddings
  - All embeddings have correct dimensions (384)
- **Embedding Quality**:
  - No NaN or infinite values
  - All vectors are properly normalized
  - Correct dimensionality

Example validation output:
```json
{
  "timestamp": "2025-03-24T21:46:27.639112+00:00",
  "rows_loaded": 4599,
  "validation": {
    "table_structure": {"valid": true},
    "data_quality": {
      "doi_null_count": 0,
      "title_null_count": 0,
      "abstract_null_count": 0,
      "doi_empty_count": 0,
      "title_empty_count": 0,
      "abstract_empty_count": 2713,
      "date_range": {
        "min": "1908-01-01",
        "max": "2024-07-01",
        "null_count": 1740
      },
      "null_embeddings": 0,
      "invalid_dimensions": 0
    },
    "embeddings": {
      "valid": true,
      "issues": []
    },
    "overall_valid": true
  },
  "notes": ["Found 2713 empty strings in abstract"]
}
```



