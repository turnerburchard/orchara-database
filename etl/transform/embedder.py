from sentence_transformers import SentenceTransformer

from transform.types import Item


class Embedder:
    def __init__(self):
        self.model = model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_item(self, item: Item) -> Item:
        """
        Embeds the item using Sentence-BERT to compute a semantic embedding
        from its title. The embedding is stored as a list of floats in item.embedding.
        """
        if not isinstance(item.title, str):
            print(item.title)
            raise ValueError("Item.title must be a string")

        embedding = self.model.encode(item.title)
        item.embedding = embedding

        return item