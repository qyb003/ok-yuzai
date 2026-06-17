"""
OKX 数据适配器  [OKX 新增]

继承 BaseExchangeAdapter，实现 fetch_klines / fetch_orderbook / fetch_funding_rate / fetch_open_interest。

使用 OKX 公开 REST API 获取市场数据，转换为项目内部统一格式。

参考：backend/services/exchanges/binance_adapter.py
"""
import logging
import requests
import urllib3
from decimal import Decimal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # [OKX] 抑制 verify=False 警告
from typing import List, Optional
from datetime import datetime

from .base_adapter import (
    BaseExchangeAdapter,
    UnifiedKline,
    UnifiedOrderbook,
    UnifiedFunding,
    UnifiedOpenInterest,
)
from .symbol_mapper import SymbolMapper

logger = logging.getLogger(__name__)


class OkxAdapter(BaseExchangeAdapter):
    """OKX 永续合约（USDT 本位）数据适配器。"""

    BASE_URL = "https://www.okx.com"

    def __init__(self, environment: str = "mainnet"):
        super().__init__(environment)
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.verify = False  # [OKX] 绕过 SSL 证书验证，避免 GFW 阻断 TLS

    def _get_exchange_name(self) -> str:
        return "okx"

    def _to_exchange_symbol(self, symbol: str) -> str:
        return SymbolMapper.to_exchange(symbol, "okx")

    def _to_internal_symbol(self, inst_id: str) -> str:
        return SymbolMapper.to_internal(inst_id, "okx")

    # [OKX] SSL重试辅助: GFW可能阻断TLS握手
    def _get_with_retry(self, url: str, params: dict, timeout: int = 10, max_retries: int = 3):
        import time as _time
        last_err = None
        for retry in range(max_retries):
            try:
                return self.session.get(url, params=params, timeout=timeout)
            except Exception as e:
                last_err = e
                if retry < max_retries - 1:
                    _time.sleep(1.5)
                    logger.warning(f"[OKX] HTTP retry {retry+1}/{max_retries}: {e}")
        raise last_err

    # ==================== 数据获取 ====================

    def fetch_klines(
        self, symbol: str, interval: str, limit: int = 100,
        start_time: Optional[int] = None, end_time: Optional[int] = None,
    ) -> List[UnifiedKline]:
        """获取 K 线数据。"""
        inst_id = self._to_exchange_symbol(symbol)
        # OKX bar 参数格式规范化
        bar_map = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m",
                   "30m": "30m", "1h": "1H", "4h": "4H", "1d": "1D"}
        bar = bar_map.get(interval, interval)

        params = {"instId": inst_id, "bar": bar, "limit": str(min(limit, 300))}
        if start_time:
            params["before"] = str(start_time)
        if end_time:
            params["after"] = str(end_time)

        resp = self._get_with_retry(
            f"{self.BASE_URL}/api/v5/market/candles",
            params=params, timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

        klines = []
        for item in reversed(data):  # OKX 返回最新在前，需反转
            ts_ms = int(item[0])
            klines.append(UnifiedKline(
                exchange="okx", symbol=symbol, interval=interval,
                timestamp=ts_ms // 1000,
                open_price=Decimal(str(item[1])),
                high_price=Decimal(str(item[2])),
                low_price=Decimal(str(item[3])),
                close_price=Decimal(str(item[4])),
                volume=Decimal(str(item[5])),
                quote_volume=Decimal(str(item[6])),
            ))
        return klines

    def fetch_orderbook(self, symbol: str, depth: int = 10) -> UnifiedOrderbook:
        """获取订单簿快照。"""
        inst_id = self._to_exchange_symbol(symbol)
        params = {"instId": inst_id, "sz": str(min(depth, 400))}
        resp = self._get_with_retry(f"{self.BASE_URL}/api/v5/market/books", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise ValueError(f"OKX 未返回 {symbol} 订单簿数据")

        snapshot = data[0]
        bids = snapshot.get("bids", [])
        asks = snapshot.get("asks", [])
        ts = int(snapshot.get("ts", int(datetime.utcnow().timestamp() * 1000)))

        best_bid = Decimal(str(bids[0][0])) if bids else Decimal("0")
        best_ask = Decimal(str(asks[0][0])) if asks else Decimal("0")
        bid_depth = sum(Decimal(str(b[1])) for b in bids[:10])
        ask_depth = sum(Decimal(str(a[1])) for a in asks[:10])
        spread = best_ask - best_bid
        mid = (best_ask + best_bid) / 2
        spread_bps = (spread / mid * 10000) if mid > 0 else Decimal("0")

        return UnifiedOrderbook(
            exchange="okx", symbol=symbol, timestamp=ts,
            best_bid=best_bid, best_ask=best_ask,
            bid_depth_sum=bid_depth, ask_depth_sum=ask_depth,
            spread=spread, spread_bps=spread_bps,
        )

    def fetch_funding_rate(self, symbol: str) -> UnifiedFunding:
        """获取当前资金费率。"""
        inst_id = self._to_exchange_symbol(symbol)
        params = {"instId": inst_id}
        resp = self._get_with_retry(f"{self.BASE_URL}/api/v5/public/funding-rate", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise ValueError(f"OKX 未返回 {symbol} 资金费率")

        item = data[0]
        return UnifiedFunding(
            exchange="okx", symbol=symbol,
            timestamp=int(item.get("fundingTime", 0)),
            funding_rate=Decimal(str(item.get("fundingRate", 0))),
            next_funding_time=int(item.get("nextFundingTime", 0)),
        )

    def fetch_open_interest(self, symbol: str) -> UnifiedOpenInterest:
        """获取当前持仓量。"""
        inst_id = self._to_exchange_symbol(symbol)
        params = {"instId": inst_id}
        resp = self._get_with_retry(f"{self.BASE_URL}/api/v5/public/open-interest", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise ValueError(f"OKX 未返回 {symbol} 持仓量")

        item = data[0]
        oi = Decimal(str(item.get("oi", 0)))
        oi_value = Decimal(str(item.get("oiCcy", 0))) if item.get("oiCcy") else None
        return UnifiedOpenInterest(
            exchange="okx", symbol=symbol,
            timestamp=int(item.get("ts", int(datetime.utcnow().timestamp() * 1000))),
            open_interest=oi, open_interest_value=oi_value,
        )
