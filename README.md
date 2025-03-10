# orchera-etl
ETL Pipeline for Orchera

Extract -> Transform -> Load

1. Extract:
    a. Read through Crossref papers in zip files


2. Transform:
    a. Prune non-English, empty, etc papers.
    b. Embed title with Sentence-BERT

3. Load:


4. Indexing?


TO RUN:

start database and etl:
docker-compose up -d

start just etl:
docker-compose up --no-deps --build etl



