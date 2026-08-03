"""CSS-X v1.0 — Crypto Solvency Shadow protocol.

Crypto-market analogue of CSS v10.0: mandatory-emission absence detection for
chains, rollups, DeFi protocols, exchanges and stablecoins.
"""

from .core import AssetClass, Observation, SignalScore, Tier
from .convergence import Verdict, rank, score_entity

__version__ = "1.0.0"
__all__ = ["AssetClass", "Observation", "SignalScore", "Tier",
           "Verdict", "rank", "score_entity", "__version__"]
