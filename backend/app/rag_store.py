from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np

class TabularRAG:
    """Simple in-memory tabular RAG using sentence-transformers and NearestNeighbors."""
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.texts = []
        self.embeddings = None
        self.nn = None

    def add_texts(self, texts):
        self.texts.extend(texts)
        embeds = self.model.encode(texts)
        if self.embeddings is None:
            self.embeddings = np.array(embeds)
        else:
            self.embeddings = np.vstack([self.embeddings, embeds])
        # rebuild nn
        self.nn = NearestNeighbors(n_neighbors=min(5, len(self.embeddings)), metric="cosine")
        self.nn.fit(self.embeddings)

    def retrieve(self, query, k=3):
        if self.embeddings is None or len(self.embeddings)==0:
            return []
        q_emb = self.model.encode([query])[0].reshape(1, -1)
        dists, idxs = self.nn.kneighbors(q_emb, n_neighbors=min(k, len(self.embeddings)))
        results = [self.texts[i] for i in idxs[0]]
        return results
