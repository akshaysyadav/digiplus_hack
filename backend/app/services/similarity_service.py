"""
Similarity Service

Responsible for:
- Fitting TF-IDF Vectorizer on 300 historical resolved tickets
- Executing Cosine Similarity search against incoming tickets
- Returning Top K historical precedent matches with similarity scores
"""

import numpy as np
import pandas as pd
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.schemas import PrecedentMatch
from app.services.data_service import data_service
from app.core.config import TOP_K_PRECEDENTS


class SimilarityService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english"
        )
        self.resolved_matrix = None
        self._fit_vectorizer()

    def _fit_vectorizer(self) -> None:
        """Fits the TF-IDF vectorizer on all historical resolved ticket descriptions."""
        df = data_service.resolved_tickets_df
        descriptions = df["description"].fillna("").astype(str)
        self.resolved_matrix = self.vectorizer.fit_transform(descriptions)

    def get_top_k_precedents(self, description: str, k: int = TOP_K_PRECEDENTS) -> List[PrecedentMatch]:
        """
        Calculates cosine similarity of input text against historical resolved tickets
        and returns the top-k precedent matches.
        """
        if self.resolved_matrix is None:
            self._fit_vectorizer()

        query_vector = self.vectorizer.transform([description])
        sim_scores = cosine_similarity(query_vector, self.resolved_matrix)[0]

        # Get top k indices in descending order
        top_indices = np.argsort(sim_scores)[::-1][:k]
        df = data_service.resolved_tickets_df

        precedents = []
        for idx in top_indices:
            row = df.iloc[idx]
            precedents.append(
                PrecedentMatch(
                    precedent_id=str(row["ticket_id"]),
                    category=str(row["category"]),
                    description=str(row["description"]),
                    resolution_action=str(row["resolution_action"]),
                    resolution_note=str(row["resolution_note"]),
                    similarity_score=round(float(sim_scores[idx]), 4),
                    csat=int(row["csat"])
                )
            )

        return precedents


# Global singleton instance
similarity_service = SimilarityService()
