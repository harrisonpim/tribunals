from typing import Dict, List

import numpy as np


class NDCG:
    """Compute the Normalized Discounted Cumulative Gain for a set of search results."""

    def __init__(self, relevance_scores: Dict[str, int], search_result_ids: List[str]):
        self.relevance_scores = relevance_scores
        self.search_result_ids = search_result_ids

    def compute(self, k: int = 10) -> float:
        # Get the relevance scores for the top k search results
        top_k_ids = self.search_result_ids[:k]
        scores = np.array([self.relevance_scores.get(id, 0) for id in top_k_ids])

        # Calculate the Discounted Cumulative Gain (DCG)
        dcg = np.sum((2**scores - 1) / np.log2(np.arange(2, k + 2)))

        # Calculate the Ideal Discounted Cumulative Gain (IDCG)
        ideal_scores = np.array(
            sorted(self.relevance_scores.values(), reverse=True)[:k]
        )
        idcg = np.sum((2**ideal_scores - 1) / np.log2(np.arange(2, k + 2)))

        # Calculate the Normalized Discounted Cumulative Gain (NDCG)
        ndcg = dcg / idcg if idcg > 0 else 0
        return ndcg
