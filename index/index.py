import json
import hnswlib
import numpy as np
from etl.util import get_connection


def get_total_count():
    """
    Returns the total number of papers in the database.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM public.papers")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def fetch_embeddings_in_batches(batch_size=10000):
    """
    Generator that yields batches of (id, embedding) rows from the papers table.
    Uses a server-side cursor to avoid loading all data into memory.
    """
    conn = get_connection()
    # Using a named cursor so that the data is streamed from the server.
    cur = conn.cursor(name="embedding_cursor")
    cur.itersize = batch_size
    cur.execute("SELECT id, embedding FROM public.papers")
    while True:
        batch = cur.fetchmany(batch_size)
        if not batch:
            break
        yield batch
    cur.close()
    conn.close()


def build_and_save_index(index_path="hnsw_index.bin", mapping_path="id_mapping.json", batch_size=10000):
    """
    Builds an HNSWlib index using cosine similarity in batches and saves the index and
    ID mapping to disk. This method avoids loading the entire dataset into memory.
    """
    total_count = get_total_count()
    print(f"Total number of papers: {total_count}")

    dim = 384  # Dimensionality of your embeddings
    # Initialize the index with the expected maximum number of elements.
    index = hnswlib.Index(space='cosine', dim=dim)
    index.init_index(max_elements=total_count, ef_construction=200, M=16)
    index.set_ef(50)  # Set query-time parameter

    id_map = {}  # Mapping from internal index (as string) to paper ID
    current_offset = 0

    for batch in fetch_embeddings_in_batches(batch_size):
        batch_ids = []
        batch_embeddings = []
        for row in batch:
            paper_id = row[0]
            embedding = row[1]
            # Convert the embedding string to a list of floats if needed
            if isinstance(embedding, str):
                embedding = json.loads(embedding)
            batch_ids.append(paper_id)
            batch_embeddings.append(embedding)

        # Convert list of embeddings to a NumPy array with explicit float type.
        batch_embeddings = np.array(batch_embeddings, dtype=np.float32)
        # Normalize embeddings for cosine similarity.
        norms = np.linalg.norm(batch_embeddings, axis=1, keepdims=True)
        batch_embeddings_norm = batch_embeddings / norms

        num_batch = batch_embeddings_norm.shape[0]
        # Add this batch of normalized embeddings to the index.
        index.add_items(batch_embeddings_norm, np.arange(current_offset, current_offset + num_batch))

        # Update the ID mapping for this batch.
        for i, paper_id in enumerate(batch_ids):
            id_map[str(current_offset + i)] = paper_id

        current_offset += num_batch
        print(f"Processed {current_offset} / {total_count} papers.")

    # Save the index to disk.
    index.save_index(index_path)
    print(f"HNSW index saved to {index_path}")

    # Save the mapping from internal index to paper ID.
    with open(mapping_path, "w") as f:
        json.dump(id_map, f)
    print(f"ID mapping saved to {mapping_path}")


def main():
    print("Building and saving HNSWlib index in batches...")
    build_and_save_index()
    print("ETL indexing complete.")


if __name__ == "__main__":
    main()
