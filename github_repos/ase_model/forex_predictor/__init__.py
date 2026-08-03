from .data_collector import fetch_ohlc, fetch_all_majors, MAJOR_PAIRS
from .feature_engineering import add_all_features_advanced as add_all_features
from .pattern_engine import (
    compute_pattern_composite_advanced,
    compute_rsi_extreme_advanced,
    compute_cdp_advanced,
    generate_prediction_advanced,
    DEFAULT_WEIGHTS,
)
from .prediction_engine import predict_direction, accuracy_report, summary_table
from .backtester import backtest_pair, backtest_all_majors
