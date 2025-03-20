from sentence_transformers import SentenceTransformer

from transform.types import Item


class Embedder:
    def __init__(self):
        self.model = model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_item(self, item: Item) -> Item:
        if not isinstance(item.title, str):
            print(item.title)
            raise ValueError("Item.title must be a string")
        text = item.title
        if item.abstract:
            text = text + " " + item.abstract
        embedding = self.model.encode(text)
        item.embedding = embedding
        return item