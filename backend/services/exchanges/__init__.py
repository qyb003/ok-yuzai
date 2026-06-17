"""
Exchange adapters for multi-exchange support.

This module provides a unified interface for interacting with different
cryptocurrency exchanges. Each exchange has its own adapter that handles
data fetching, format conversion, and order execution.

Supported exchanges:
- Hyperliquid (existing, native implementation)
- Binance (new, via adapter)
"""

from .base_adapter import BaseExchangeAdapter
from .symbol_mapper import SymbolMapper
from .binance_adapter import BinanceAdapter
from .data_persistence import ExchangeDataPersistence
from .binance_collector import BinanceCollector, binance_collector
from .okx_adapter import OkxAdapter  # [OKX 新增]
from .okx_collector import OkxCollector, okx_collector  # [OKX 新增]

__all__ = [
    "BaseExchangeAdapter",
    "SymbolMapper",
    "BinanceAdapter",
    "ExchangeDataPersistence",
    "BinanceCollector",
    "binance_collector",
    "OkxAdapter",  # [OKX 新增]
    "OkxCollector",  # [OKX 新增]
    "okx_collector",  # [OKX 新增]
]
