import re


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

def prune_item(item):
    """
    Manual pruning of records.
    """
    if not item.get("DOI"):
        return None
    if not item.get("language") == "en":
        return None
    if item.get("abstract"):
        abstract = item["abstract"]
        # Remove leading angle-bracketed text (e.g., "<...> ") if present.
        abstract = re.sub(r'^<[^>]*>\s*', '', abstract)
        # Remove trailing angle-bracketed text (e.g., " <...>") if present.
        abstract = re.sub(r'\s*<[^>]*>$', '', abstract)
        item["abstract"] = abstract

    return item

def embed_item(item):
    """
    Placeholder embedding function.
    Replace this with your actual embedding logic.
    Here, we return a dummy 3-dimensional embedding.
    """
    # For example, compute an embedding from title/abstract.
    item["embedding"] = [0.0, 0.0, 0.0]
    return item