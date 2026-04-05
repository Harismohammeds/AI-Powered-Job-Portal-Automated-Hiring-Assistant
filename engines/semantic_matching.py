import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticMatcher:
    """
    Engine to compute semantic similarity between resumes and job descriptions.
    Uses Hugging Face sentence transformers for creating embeddings.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def get_embedding(self, text):
        if not text:
            return np.zeros((self.model.get_sentence_embedding_dimension(),))
        return self.model.encode([text])[0]

    def compute_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
            
        emb1 = self.get_embedding(text1).reshape(1, -1)
        emb2 = self.get_embedding(text2).reshape(1, -1)
        return float(cosine_similarity(emb1, emb2)[0][0])
