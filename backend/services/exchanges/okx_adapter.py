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

# OKX V5 /market/candles 返回字段索引
# [0]ts  [1]o  [2]h  [3]l  [4]c  [5]vol(张)  [6]volCcy(币)  [7]volCcyQuote(USDT)
# 对于 SWAP：index 5 = 合约张数, index 6 = 基础币种, index 7 = 计价币种(USDT)
_OKX_KLINE_VOL_CCY = 6       # 基础币种成交量
_OKX_KLINE_VOL_CCY_QUOTE = 7  # 计价币种(USDT)成交量

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

    # ==================== Price Methods ====================

    def fetch_price(self, symbol: str) -> float:
        """获取最新成交价（Bug #1 修复：补全 fetch_price 方法）。

        通过 OKX V5 /api/v5/market/ticker 获取最新成交价。
        与 BinanceAdapter.fetch_price() 返回类型一致（float）。
        """
        ticker = self.fetch_ticker(symbol)
        price = float(ticker.get("last", 0) or 0)
        if price <= 0:
            inst_id = self._to_exchange_symbol(symbol)
            raise ValueError(f"OKX returned invalid price for {inst_id}: {price}")
        return price

    # ==================== 数据获取 ====================

    def fetch_ticker(self, symbol: str) -> dict:
        """获取 24h 行情快照（最新价、24h 开盘价、24h 成交额等）。

        返回原始 dict（与 BinanceAdapter._request("/fapi/v1/ticker/24hr") 模式一致），
        供 services/market_data.py 统一字段提取，避免 dataclass/dict 不一致问题。

        OKX V5 /api/v5/market/ticker 返回字段（节选）：
          last       最新成交价
          open24h    24h 开盘价
          high24h    24h 最高价
          low24h     24h 最低价
          vol24h     24h 成交量（base currency）
          volCcy24h  24h 成交额（quote currency，USDT）
          ts         数据时间戳（毫秒）
        """
        inst_id = self._to_exchange_symbol(symbol)
        params = {"instId": inst_id}
        resp = self._get_with_retry(
            f"{self.BASE_URL}/api/v5/market/ticker",
            params=params, timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise ValueError(f"OKX 未返回 {symbol} ticker 数据")
        # 返回第一条原始 dict，字段名保持 OKX 原样
        return data[0]

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
        # Bug #2 修复：OKX V5 before/after 语义
        #   before = 返回早于此时间戳的记录（结束时间）
        #   after  = 返回晚于此时间戳的记录（开始时间）
        # 原代码将 start_time→before, end_time→after 映射反了，导致范围查询返回空集
        if start_time:
            params["after"] = str(start_time)
        if end_time:
            params["before"] = str(end_time)

        resp = self._get_with_retry(
            f"{self.BASE_URL}/api/v5/market/candles",
            params=params, timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

        klines = []
        for item in reversed(data):  # OKX 返回最新在前，需反转
            ts_ms = int(item[0])
            # Bug #3 修复：OKX V5 /market/candles 字段映射
            #   index 5 = vol (合约张数, SWAP)
            #   index 6 = volCcy (基础币种, e.g. BTC)
            #   index 7 = volCcyQuote (计价币种, e.g. USDT)
            # 原代码 volume=item[5](张数), quote_volume=item[6](币种) 语义错误
            # UnifiedKline.volume = 基础币种成交量, quote_volume = USDT 计价成交量
            klines.append(UnifiedKline(
                exchange="okx", symbol=symbol, interval=interval,
                timestamp=ts_ms // 1000,
                open_price=Decimal(str(item[1])),
                high_price=Decimal(str(item[2])),
                low_price=Decimal(str(item[3])),
                close_price=Decimal(str(item[4])),
                volume=Decimal(str(item[_OKX_KLINE_VOL_CCY])),          # volCcy: 基础币种
                quote_volume=Decimal(str(item[_OKX_KLINE_VOL_CCY_QUOTE])),  # volCcyQuote: USDT
                # OKX K-line API 不提供 taker 买卖量数据（与 Binance 不同）
                # taker_buy_volume / taker_sell_volume 保持 None
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

        # Bug #7 修复：获取 mark_price
        # OKX V5 /api/v5/public/mark-price 返回标记价格
        mark_price = None
        try:
            mp_resp = self._get_with_retry(
                f"{self.BASE_URL}/api/v5/public/mark-price",
                params={"instId": inst_id}, timeout=10
            )
            mp_resp.raise_for_status()
            mp_data = mp_resp.json().get("data", [])
            if mp_data:
                mark_price = Decimal(str(mp_data[0].get("markPx", 0)))
        except Exception as e:
            logger.warning(f"[OKX] Failed to fetch mark price for {symbol}: {e}")

        return UnifiedFunding(
            exchange="okx", symbol=symbol,
            timestamp=int(item.get("fundingTime", 0)),
            funding_rate=Decimal(str(item.get("fundingRate", 0))),
            next_funding_time=int(item.get("nextFundingTime", 0)),
            mark_price=mark_price,
        )

    def fetch_open_interest(self, symbol: str) -> UnifiedOpenInterest:
        """获取当前持仓量。

        Bug #5/#6 修复：OKX OI 字段语义
          oi    = 合约张数 (contracts)
          oiCcy = 基础币种持仓量 (e.g. BTC)

        UnifiedOpenInterest 约定（与 Binance 一致）：
          open_interest       = 基础币种持仓量
          open_interest_value = 计价币种(USD)持仓量 = oiCcy * mark_price

        原代码 open_interest=oi(张数) 导致下游 market_data.py 计算 USD 值时错误。
        """
        inst_id = self._to_exchange_symbol(symbol)
        params = {"instId": inst_id}
        resp = self._get_with_retry(f"{self.BASE_URL}/api/v5/public/open-interest", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise ValueError(f"OKX 未返回 {symbol} 持仓量")

        item = data[0]
        # 优先使用 oiCcy（基础币种），与 Binance 的 openInterest 语义一致
        oi_ccy = item.get("oiCcy")
        if oi_ccy:
            open_interest = Decimal(str(oi_ccy))  # 基础币种
        else:
            # 回退到 oi（张数），下游需注意这是张数而非币种
            open_interest = Decimal(str(item.get("oi", 0)))
            logger.warning(f"[OKX] oiCcy missing for {symbol}, falling back to oi (contracts)")

        return UnifiedOpenInterest(
            exchange="okx", symbol=symbol,
            timestamp=int(item.get("ts", int(datetime.utcnow().timestamp() * 1000))),
            open_interest=open_interest,
            open_interest_value=None,  # USD 价值由下游 (market_data.py) 用 price * open_interest 计算
        )
