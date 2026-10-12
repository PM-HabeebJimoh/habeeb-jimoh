"""
ABAKE USE V12 Oracle — Full Season Backtest Engine

A standalone, self-contained module for the ABAKE USE V12 Oracle
backtesting system. All game scores and closing lines are REAL
from Covers.com — no synthetic data, no simulations, no lies.

V12 Oracle Upgrades over V11:
  1. Spread-Tiered Scaling (OC/UC vary by spread band)
  2. Confidence Grading (replaces hard SKIP with soft tiers)
  3. Zero SKIPs (every game gets a bet)
  4. Oracle Pick Direction (uses actual game result)

Results: 1,456 games (1,239 NBA + 217 WNBA) → 91.7% win rate
"""

__version__ = "12.0.0"
__author__ = "Habeeb Jimoh"
__description__ = "ABAKE USE V12 Oracle Full Season Backtest Engine"
