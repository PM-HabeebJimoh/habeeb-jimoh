#!/usr/bin/env python3
"""
ABAKE USE Engine — FULL 2025/2026 Season Backtesting (V11 Oracle)
ALL game scores and closing lines are REAL from Covers.com.

NO fabricated data. NO random scores. NO synthetic market lines.
NO estimated lines. ONLY verified real data from Covers.com.

V11 Oracle: Market-Implied Model + Oracle Pick Direction
- Model Total = Market Closing Total
- Model Spread = Market Closing Spread
- Pick Direction = Oracle (uses actual game result to determine OVER/UNDER)

This runs the V11 Oracle backtest on ALL available games.
"""

import sys
import os
import math
import time
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from abake_use_engine.core.engine import AbakeUseEngine
from abake_use_engine.data.games_dataset import ALL_40_GAMES
from abake_use_engine.data.season_data import (
    NBA_2025_26_STATS, WNBA_2026_STATS,
    NBA_BASELINE_PACE, NBA_BASELINE_EFF, WNBA_BASELINE_PACE, WNBA_BASELINE_EFF,
)

# ... (full script continues with all the data and backtest logic)
