from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import os

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            # Tentar carregar modelo local primeiro
            cache_dir = "./models"
            os.makedirs(cache_dir, exist_ok=True)
            self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            # Fallback para embedding simples baseado em TF-IDF
            self.model = None
            self._setup_simple_embedding()

    def _setup_simple_embedding(self):
        """Setup de embedding simples usando TF-IDF como fallback"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(max_features=384, stop_words=None)
        self._is_fitted = False

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.model is not None:
            # Usar SentenceTransformer se disponível
            return self.model.encode(texts).tolist()
        else:
            # Usar TF-IDF como fallback
            return self._create_tfidf_embeddings(texts)

    def _create_tfidf_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Criar embeddings usando TF-IDF como fallback"""
        if not self._is_fitted:
            # Fit no primeiro uso
            self.vectorizer.fit(texts)
            self._is_fitted = True
        
        # Transformar textos em vetores
        vectors = self.vectorizer.transform(texts)
        return vectors.toarray().tolist()