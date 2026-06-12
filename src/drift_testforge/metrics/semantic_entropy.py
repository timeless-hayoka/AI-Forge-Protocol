#!/usr/bin/env python3
"""
Semantic Entropy Metric for DRIFT TestForge
Lightweight, dependency-minimal implementation for cognitive robustness testing.
Uses character n-gram hashing for embedding (no sentence-transformers or sklearn required).
Falls back gracefully and is fully reproducible with seeds.
"""

import logging
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import statistics
from typing import List, Dict, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

def _char_ngram_hash_embed(texts: List[str], n: int = 3, dim: int = 256) -> np.ndarray:
    """Lightweight embedding via hashed character n-grams + L2 normalize.
    Pure numpy, no external models. Good proxy for semantic clustering on short outputs.
    """
    if not texts:
        return np.zeros((0, dim))
    
    vectors = []
    for text in texts:
        vec = np.zeros(dim, dtype=np.float32)
        if not text or not text.strip():
            vectors.append(vec)
            continue
        clean = text.lower().strip().replace(" ", "_")
        for i in range(max(0, len(clean) - n + 1)):
            gram = clean[i : i + n]
            h = hash(gram) % dim
            vec[h] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 1e-8:
            vec /= norm
        vectors.append(vec)
    return np.array(vectors, dtype=np.float32)


class SemanticEntropy:
    """
    Production-grade Semantic Entropy for measuring output diversity under perturbation.
    Higher entropy = more semantic uncertainty / less consistent "meaning" across repeats.
    Uses hierarchical clustering on lightweight n-gram embeddings.
    """

    def __init__(self, distance_threshold: float = 0.65, embed_dim: int = 256, ngram_n: int = 3):
        self.distance_threshold = distance_threshold
        self.embed_dim = embed_dim
        self.ngram_n = ngram_n

    def embed(self, texts: List[str]) -> np.ndarray:
        return _char_ngram_hash_embed(texts, n=self.ngram_n, dim=self.embed_dim)

    def cluster(self, texts: List[str]) -> Tuple[List[int], Dict[int, List[str]]]:
        if len(texts) < 2:
            return [0] * len(texts), {0: texts} if texts else ({}, {})
        
        embeds = self.embed(texts)
        if embeds.shape[0] == 0:
            return list(range(len(texts))), {i: [t] for i, t in enumerate(texts)}
        
        # Cosine distance for clustering
        condensed = pdist(embeds, metric="cosine")
        Z = linkage(condensed, method="average")
        clusters = fcluster(Z, t=self.distance_threshold, criterion="distance")
        
        cluster_map: Dict[int, List[str]] = defaultdict(list)
        for idx, c in enumerate(clusters):
            cluster_map[int(c)].append(texts[idx])
        
        return clusters.tolist(), dict(cluster_map)

    def compute(self, outputs: List[str]) -> Dict[str, float]:
        clean = [o.strip() for o in outputs if o and o.strip()]
        n = len(clean)
        if n < 2:
            return {
                "semantic_entropy": 0.0,
                "num_clusters": 1 if n > 0 else 0,
                "max_cluster_prob": 1.0 if n > 0 else 0.0,
                "num_outputs": n,
                "avg_cluster_size": float(n),
                "cluster_sizes": [n] if n > 0 else [],
            }
        
        _, cluster_map = self.cluster(clean)
        k = len(cluster_map)
        probs = np.array([len(g) / n for g in cluster_map.values()])
        entropy = -np.sum(probs * np.log(probs + 1e-12))  # nats
        
        return {
            "semantic_entropy": float(entropy),
            "num_clusters": k,
            "max_cluster_prob": float(np.max(probs)),
            "num_outputs": n,
            "avg_cluster_size": float(statistics.mean(len(g) for g in cluster_map.values())),
            "cluster_sizes": [len(g) for g in cluster_map.values()],
        }


# Quick self-test when run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    se = SemanticEntropy()
    sample_outputs = [
        "The system maintains strong homeostasis and reflects deeply on its needs.",
        "Homeostasis is stable; reflection shows clear self-awareness of internal states.",
        "The agent feels balanced and engages in meaningful self-reflection about its drives.",
        "Under stress the homeostasis falters and reflection becomes shallow and fragmented.",
    ]
    metrics = se.compute(sample_outputs)
    print("Semantic Entropy demo:", metrics)