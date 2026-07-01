"""
OKX REST 数据采集器  [OKX 新增]

使用 APScheduler 定时采集 OKX 市场数据：K线、OI、资金费率、订单簿。

参考：backend/services/exchanges/binance_collector.py
"""
import logging
import threading
from typing import List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from services.exchanges.okx_adapter import OkxAdapter
from services.exchanges.data_persistence import ExchangeDataPersistence
from database.connection import SessionLocal

logger = logging.getLogger(__name__)

KLINE_INTERVAL_SECONDS = 60
OI_INTERVAL_SECONDS = 60
FUNDING_INTERVAL_SECONDS = 60
ORDERBOOK_INTERVAL_SECONDS = 15
KLINE_PERIODS = ['1m', '3m', '5m', '15m', '30m', '1h']


class OkxCollector:
    """[OKX] 单例 REST 数据采集器。"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.adapter = OkxAdapter()
        self.scheduler: Optional[BackgroundScheduler] = None
        self.running = False
        self.symbols: List[str] = []
        logger.info("[OKX] Collector initialized")

    def start(self, symbols: Optional[List[str]] = None):
        if self.running:
            return
        if symbols is None:
            from services.okx_symbol_service import get_selected_symbols
            symbols = get_selected_symbols() or ["BTC"]
        self.symbols = symbols
        self.scheduler = BackgroundScheduler()
        self._add_jobs()
        self.scheduler.start()
        self.running = True
        logger.info(f"[OKX] Collector started: symbols={symbols}")
        self._collect_all_initial()

    def stop(self):
        if not self.running:
            return
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
        self.running = False
        logger.info("[OKX] Collector stopped")

    def _add_jobs(self):
        self.scheduler.add_job(
            self._collect_klines, IntervalTrigger(seconds=KLINE_INTERVAL_SECONDS),
            id="okx_klines", max_instances=1, coalesce=True)
        self.scheduler.add_job(
            self._collect_oi, IntervalTrigger(seconds=OI_INTERVAL_SECONDS),
            id="okx_oi", max_instances=1, coalesce=True)
        self.scheduler.add_job(
            self._collect_funding, IntervalTrigger(seconds=FUNDING_INTERVAL_SECONDS),
            id="okx_funding", max_instances=1, coalesce=True)
        self.scheduler.add_job(
            self._collect_orderbook, IntervalTrigger(seconds=ORDERBOOK_INTERVAL_SECONDS),
            id="okx_orderbook", max_instances=1, coalesce=True)

    def _collect_all_initial(self):
        logger.info("[OKX] Initial data collection...")
        self._collect_klines()
        self._collect_oi()
        self._collect_funding()
        self._collect_orderbook()

    def _collect_klines(self):
        db = SessionLocal()
        try:
            persistence = ExchangeDataPersistence(db)
            for symbol in self.symbols:
                for period in KLINE_PERIODS:
                    try:
                        klines = self.adapter.fetch_klines(symbol, period, limit=5)
                        if klines:
                            persistence.save_klines(klines)
                            # Bug #10 修复：与 BinanceCollector 保持一致，
                            # 调用 save_taker_volumes_from_klines 将 taker 数据存入 MarketTradesAggregated
                            # 注意：OKX K-line API 不提供 taker 数据，此调用为 no-op，
                            # 但保留调用以确保未来添加 taker 数据源时不会遗漏
                            persistence.save_taker_volumes_from_klines(klines)
                    except Exception as e:
                        logger.error(f"[OKX] Kline {symbol}/{period}: {e}")
        finally:
            db.close()

    def _collect_oi(self):
        db = SessionLocal()
        try:
            persistence = ExchangeDataPersistence(db)
            for symbol in self.symbols:
                try:
                    oi = self.adapter.fetch_open_interest(symbol)
                    if oi:
                        persistence.save_open_interest(oi)
                except Exception as e:
                    logger.error(f"[OKX] OI {symbol}: {e}")
        finally:
            db.close()

    def _collect_funding(self):
        db = SessionLocal()
        try:
            persistence = ExchangeDataPersistence(db)
            for symbol in self.symbols:
                try:
                    funding = self.adapter.fetch_funding_rate(symbol)
                    if funding:
                        persistence.save_funding_rate(funding)
                except Exception as e:
                    logger.error(f"[OKX] Funding {symbol}: {e}")
        finally:
            db.close()

    def _collect_orderbook(self):
        db = SessionLocal()
        try:
            persistence = ExchangeDataPersistence(db)
            for symbol in self.symbols:
                try:
                    ob = self.adapter.fetch_orderbook(symbol, depth=10)
                    if ob:
                        persistence.save_orderbook(ob)
                except Exception as e:
                    logger.error(f"[OKX] Orderbook {symbol}: {e}")
        finally:
            db.close()


# 全局单例
okx_collector = OkxCollector()
