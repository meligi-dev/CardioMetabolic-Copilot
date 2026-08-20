import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

class FastGuidelineEmbedder:
    """
    Ultra-fast, deterministic 384-dim semantic hashing embedder 
    with zero external downloads or network latency.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.vectorizer = HashingVectorizer(n_features=dim, alternate_sign=False, norm='l2')

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        sparse_vecs = self.vectorizer.transform(texts)
        dense_vecs = sparse_vecs.toarray()
        # L2 normalize
        norms = np.linalg.norm(dense_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (dense_vecs / norms).tolist()
