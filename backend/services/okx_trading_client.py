"""
OKX 永续合约交易客户端

基于 OKX V5 REST API 实现，支持：
- 模拟盘/实盘环境隔离（通过 x-simulated-trading 请求头切换）
- HMAC SHA256 签名认证（api_key + secret_key + passphrase）
- USDT 本位永续合约（线性合约）
- 下单 + 附加止盈止损单（attachAlgoOrds）
- 频率限制与 429 自动重试

接口签名与 BinanceTradingClient / HyperliquidTradingClient 保持一致，
确保上层调用者（AI Trader、Program Trader、API Routes）无需修改。

参考文档：https://www.okx.com/docs-v5/
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import threading
import time
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ============================================================================
# 常量定义
# ============================================================================

# OKX API 基础域名（主网和模拟盘共用同一个域名，通过请求头区分）
REST_URL = "https://www.okx.com"

# 模拟盘专用请求头
SIMULATED_TRADING_HEADER = "x-simulated-trading"

# 默认接收窗口（秒）
DEFAULT_RECV_WINDOW = 10

# 频率限制配置（各接口权重不同，此处设置保守默认值）
# OKX 默认每个 API Key 每秒最多 10 次请求（可申请提额）
DEFAULT_RATE_LIMIT_PER_SECOND = 8  # 留 20% 余量
RETRY_AFTER_DEFAULT_SECONDS = 2  # 429 无 Retry-After 时的默认等待秒数
MAX_RETRY_COUNT = 3  # 最大重试次数

# 内部符号到 OKX instId 的映射表
# 格式：内部符号 -> OKX 永续合约产品 ID
SYMBOL_TO_INST_ID: Dict[str, str] = {
    "BTC": "BTC-USDT-SWAP",
    "BTCUSDT": "BTC-USDT-SWAP",
    "ETH": "ETH-USDT-SWAP",
    "ETHUSDT": "ETH-USDT-SWAP",
    "SOL": "SOL-USDT-SWAP",
    "SOLUSDT": "SOL-USDT-SWAP",
    "DOGE": "DOGE-USDT-SWAP",
    "DOGEUSDT": "DOGE-USDT-SWAP",
    "XRP": "XRP-USDT-SWAP",
    "XRPUSDT": "XRP-USDT-SWAP",
    "ADA": "ADA-USDT-SWAP",
    "ADAUSDT": "ADA-USDT-SWAP",
    "AVAX": "AVAX-USDT-SWAP",
    "AVAXUSDT": "AVAX-USDT-SWAP",
    "LINK": "LINK-USDT-SWAP",
    "LINKUSDT": "LINK-USDT-SWAP",
    "DOT": "DOT-USDT-SWAP",
    "DOTUSDT": "DOT-USDT-SWAP",
    "LTC": "LTC-USDT-SWAP",
    "LTCUSDT": "LTC-USDT-SWAP",
    "BCH": "BCH-USDT-SWAP",
    "BCHUSDT": "BCH-USDT-SWAP",
    "SUI": "SUI-USDT-SWAP",
    "SUIUSDT": "SUI-USDT-SWAP",
    "TRX": "TRX-USDT-SWAP",
    "TRXUSDT": "TRX-USDT-SWAP",
    "APT": "APT-USDT-SWAP",
    "APTUSDT": "APT-USDT-SWAP",
    "ARB": "ARB-USDT-SWAP",
    "ARBUSDT": "ARB-USDT-SWAP",
    "OP": "OP-USDT-SWAP",
    "OPUSDT": "OP-USDT-SWAP",
    "NEAR": "NEAR-USDT-SWAP",
    "NEARUSDT": "NEAR-USDT-SWAP",
    "ATOM": "ATOM-USDT-SWAP",
    "ATOMUSDT": "ATOM-USDT-SWAP",
    "FIL": "FIL-USDT-SWAP",
    "FILUSDT": "FIL-USDT-SWAP",
    "UNI": "UNI-USDT-SWAP",
    "UNIUSDT": "UNI-USDT-SWAP",

}

# OKX instId 到内部符号的反向映射（运行时自动构建）
INST_ID_TO_SYMBOL: Dict[str, str] = {}

# ============================================================================
# 符号映射工具函数
# ============================================================================


def _to_inst_id(symbol: str) -> str:
    """
    将内部符号转换为 OKX 永续合约 instId。

    转换规则（优先级从高到低）：
    1. 精确匹配映射表（如 "BTC" -> "BTC-USDT-SWAP"）
    2. 已知 USDT 后缀格式（如 "BTCUSDT" -> "BTC-USDT-SWAP"）
    3. 动态生成：添加 -USDT-SWAP 后缀

    Args:
        symbol: 内部符号，如 "BTC" 或 "BTCUSDT"

    Returns:
        OKX instId，如 "BTC-USDT-SWAP"
    """
    upper = str(symbol).upper().strip()
    if not upper:
        raise ValueError(f"无效的 symbol: {symbol!r}")

    # 1. 精确匹配映射表
    if upper in SYMBOL_TO_INST_ID:
        return SYMBOL_TO_INST_ID[upper]

    # 2. 去除 USDT 后缀后再尝试
    if upper.endswith("USDT"):
        base = upper[:-4]
        if base in SYMBOL_TO_INST_ID:
            return SYMBOL_TO_INST_ID[base]

    # 3. 动态生成 instId
    base = upper[:-4] if upper.endswith("USDT") else upper
    inst_id = f"{base}-USDT-SWAP"
    # 缓存到映射表以便后续快速查找
    SYMBOL_TO_INST_ID[upper] = inst_id
    SYMBOL_TO_INST_ID[base] = inst_id
    logger.debug(f"[OKX] 动态生成 instId: {upper} -> {inst_id}")
    return inst_id


def _to_internal_symbol(inst_id: str) -> str:
    """
    将 OKX instId 转换为内部符号。

    Args:
        inst_id: OKX 产品 ID，如 "BTC-USDT-SWAP"

    Returns:
        内部符号，如 "BTC"
    """
    upper = str(inst_id).upper().strip()
    # 检查反向映射缓存
    if upper in INST_ID_TO_SYMBOL:
        return INST_ID_TO_SYMBOL[upper]

    # 解析 instId 格式: BASE-QUOTE-SWAP
    if "-" in upper:
        base = upper.split("-")[0]
        INST_ID_TO_SYMBOL[upper] = base
        return base

    return upper


# ============================================================================
# 频率限制器（基于时间窗口的简单计数器）
# ============================================================================


class RateLimiter:
    """
    基于滑动时间窗口的频率限制器。

    用于控制对 OKX API 的请求速率，防止触发 HTTP 429。
    每个 API Key 默认每秒最多 10 次请求，此处使用保守值 8 次/秒。
    """

    def __init__(self, max_requests_per_second: int = DEFAULT_RATE_LIMIT_PER_SECOND):
        """
        Args:
            max_requests_per_second: 每秒最大请求数
        """
        self._max_requests = max_requests_per_second
        self._window_start = time.monotonic()
        self._count = 0
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """
        获取请求许可（必要时阻塞等待）。

        如果当前时间窗口内已达上限，则等待下一个窗口。
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._window_start

            if elapsed >= 1.0:
                # 新窗口开始，重置计数器
                self._window_start = now
                self._count = 1
                return

            if self._count < self._max_requests:
                # 窗口内还有余量
                self._count += 1
                return

            # 已达上限，等待到下一个窗口
            sleep_seconds = 1.0 - elapsed + 0.05  # 加 50ms 缓冲
            logger.debug(f"[OKX RateLimiter] 限流等待 {sleep_seconds:.2f}s")
            time.sleep(sleep_seconds)
            self._window_start = time.monotonic()
            self._count = 1


# ============================================================================
# OKX 交易客户端
# ============================================================================


class OkxTradingClient:
    """
    OKX 永续合约（USDT 本位）交易客户端。

    使用 OKX V5 REST API，支持：
    - HMAC SHA256 + Base64 签名认证
    - 模拟盘/实盘环境切换
    - 下单并附加止盈止损单
    - 频率限制与自动重试

    接口签名与 BinanceTradingClient 保持一致。
    """

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        passphrase: str,
        environment: str = "testnet",
    ):
        """
        初始化 OKX 交易客户端。

        Args:
            api_key: OKX API Key
            secret_key: OKX Secret Key（用于 HMAC 签名）
            passphrase: OKX Passphrase（创建 API Key 时设置的密码短语）
            environment: "testnet"（模拟盘）或 "mainnet"（实盘）
        """
        if environment not in ("testnet", "mainnet"):
            raise ValueError(f"无效的 environment: {environment!r}，必须是 'testnet' 或 'mainnet'")

        self.api_key = api_key.strip()
        self.secret_key = secret_key.strip()
        self.passphrase = passphrase.strip()
        self.environment = environment
        self._is_simulated = (environment == "testnet")

        # HTTP 会话（复用连接池）
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        # 频率限制器
        self._rate_limiter = RateLimiter()

        # 用于记录最后一次请求的限流信息（与 Binance 兼容）
        self._last_rate_limit_info: Dict[str, Any] = {}

        logger.info(
            f"[OKX] 客户端初始化完成: environment={environment}, "
            f"simulated={self._is_simulated}"
        )

    # ========================================================================
    # 签名与认证
    # ========================================================================

    def _get_timestamp(self) -> str:
        """
        生成 OKX 要求的 ISO 8601 UTC 时间戳（精确到毫秒）。

        格式示例：2024-06-13T04:42:47.890Z
        """
        now = datetime.now(timezone.utc)
        # strftime 不支持毫秒，手动拼接
        base = now.strftime("%Y-%m-%dT%H:%M:%S")
        millis = f"{now.microsecond // 1000:03d}"
        return f"{base}.{millis}Z"

    def _sign(
        self,
        timestamp: str,
        method: str,
        request_path: str,
        body: str = "",
    ) -> str:
        """生成 OKX API 签名。

        签名字符串 = timestamp + method + requestPath + body (body 可为空串)
        HMAC-SHA256(key_bytes, sign_string) → Base64 输出
        """
        sign_str = timestamp + method.upper() + request_path + (body or "")

        # === 密钥处理（两种模式） ===
        # 模式 A: UTF-8 编码（99% 的 OKX API Key 用这个）
        secret_utf8 = self.secret_key.encode("utf-8")
        # 模式 B: Base64 解码（部分特殊密钥格式）
        secret_b64 = None
        try:
            secret_b64 = base64.b64decode(self.secret_key)
        except Exception:
            pass

        # 两种模式都计算签名，如果密钥本身就是 base64 且需要 decode，
        # 两种签名会不同，异常日志会提示用户切换模式。
        sig_a = base64.b64encode(
            hmac.new(secret_utf8, sign_str.encode("utf-8"), hashlib.sha256).digest()
        ).decode("utf-8")

        sig_b = None
        if secret_b64 and secret_b64 != secret_utf8:
            sig_b = base64.b64encode(
                hmac.new(secret_b64, sign_str.encode("utf-8"), hashlib.sha256).digest()
            ).decode("utf-8")

        # 默认使用模式 A (UTF-8)
        # 如果收到 50113，日志会显示两种签名，可切换为 sig_b
        signature = sig_a  # default UTF-8

        # 调试：打印签名关键信息
        logger.info(
            f"[OKX SIGN DEBUG] method={method.upper()} path={request_path} "
            f"secret[0:4]={self.secret_key[:4] if len(self.secret_key)>=4 else '?'} "
            f"secret[-4:]={self.secret_key[-4:] if len(self.secret_key)>=4 else '?'} "
            f"sign_str={sign_str[:120]} "
            f"sig_a(utf8)={sig_a[:20]}..."
            + (f" sig_b(b64)={sig_b[:20]}..." if sig_b else "")
        )

        return signature

    def _build_signed_headers(
        self,
        method: str,
        request_path: str,
        body: str = "",
    ) -> Dict[str, str]:
        """
        构建带签名的请求头。

        包含 4 个必须的认证头 + 可选的模拟盘切换头。

        Args:
            method: HTTP 方法（GET/POST）
            request_path: 请求路径（不含 query string）
            body: 请求体字符串

        Returns:
            完整的请求头字典
        """
        timestamp = self._get_timestamp()
        signature = self._sign(timestamp, method, request_path, body)

        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
        }

        # 模拟盘需要附加 x-simulated-trading 请求头
        if self._is_simulated:
            headers[SIMULATED_TRADING_HEADER] = "1"

        return headers

    # ========================================================================
    # HTTP 请求
    # ========================================================================

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求到 OKX API。

        Args:
            method: HTTP 方法（"GET" 或 "POST"）
            endpoint: API 端点路径（如 /api/v5/account/balance）
            params: URL 查询参数
            body: 请求体字典（用于 POST 请求）
            signed: 是否需要签名认证（私有接口需要）

        Returns:
            API 响应的 JSON 数据（已从 {"code":"0","data":[...],"msg":""} 中提取）

        Raises:
            Exception: API 调用失败或返回错误码
        """
        method_upper = method.upper()
        url = f"{REST_URL}{endpoint}"
        body_str = json.dumps(body) if body else ""

        # 频率限制
        self._rate_limiter.acquire()

        for attempt in range(MAX_RETRY_COUNT):
            headers: Dict[str, str] = {}
            if signed:
                # 计算签名时的 request_path 不含查询参数
                headers = self._build_signed_headers(method_upper, endpoint, body_str)
                # [DEBUG] 打印完整请求信息
                logger.warning(
                    f"[OKX REQUEST DEBUG] attempt={attempt+1}/{MAX_RETRY_COUNT}\n"
                    f"  URL: {url}\n"
                    f"  params: {params}\n"
                    f"  body_str: {body_str[:200] if body_str else '(empty)'}\n"
                    f"  OK-ACCESS-KEY: {headers.get('OK-ACCESS-KEY','?')[:12]}...\n"
                    f"  OK-ACCESS-TIMESTAMP: {headers.get('OK-ACCESS-TIMESTAMP','?')}\n"
                    f"  OK-ACCESS-SIGN: {headers.get('OK-ACCESS-SIGN','?')[:30]}...\n"
                    f"  OK-ACCESS-PASSPHRASE: {headers.get('OK-ACCESS-PASSPHRASE','?')[:6]}...\n"
                    f"  x-simulated-trading: {headers.get('x-simulated-trading','NOT SET')}\n"
                    f"  session headers: {dict(self.session.headers)}"
                )

            try:
                if method_upper == "GET":
                    response = self.session.get(
                        url, params=params, headers=headers, timeout=15
                    )
                elif method_upper == "POST":
                    response = self.session.post(
                        url, params=params, data=body_str, headers=headers, timeout=15
                    )
                else:
                    raise ValueError(f"不支持的 HTTP 方法: {method_upper}")

                # 记录限流信息（OKX 使用 X-Ratelimit-* 系列响应头）
                self._last_rate_limit_info = {
                    "remaining": response.headers.get("x-ratelimit-remaining", "N/A"),
                    "limit": response.headers.get("x-ratelimit-limit", "N/A"),
                    "reset": response.headers.get("x-ratelimit-reset", "N/A"),
                }

                # HTTP 429 处理：频率限制，读取 Retry-After 并等待重试
                if response.status_code == 429:
                    retry_after = RETRY_AFTER_DEFAULT_SECONDS
                    retry_after_header = response.headers.get("Retry-After")
                    if retry_after_header:
                        try:
                            retry_after = int(retry_after_header)
                        except ValueError:
                            pass
                    logger.warning(
                        f"[OKX] HTTP 429 (频率限制): {method_upper} {endpoint}, "
                        f"等待 {retry_after}s 后重试 (attempt {attempt + 1}/{MAX_RETRY_COUNT})"
                    )
                    if attempt < MAX_RETRY_COUNT - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise Exception(
                            f"OKX API 频率限制已达最大重试次数: {method_upper} {endpoint}"
                        )

                if not response.ok:
                    try:
                        error_data = response.json() if response.text else {}
                    except ValueError:
                        error_data = {}
                    # [DEBUG] 打印完整错误响应
                    logger.error(
                        f"[OKX RESPONSE ERROR] HTTP {response.status_code}: {response.text[:500]}"
                    )

                    error_code = error_data.get("code", str(response.status_code))
                    error_msg = error_data.get("msg", response.text or "未知错误")

                    # HTTP 5xx 服务端错误，重试
                    if 500 <= response.status_code < 600 and attempt < MAX_RETRY_COUNT - 1:
                        wait = (attempt + 1) * 2
                        logger.warning(
                            f"[OKX] HTTP {response.status_code} 服务端错误: "
                            f"{method_upper} {endpoint}, {wait}s 后重试"
                        )
                        time.sleep(wait)
                        continue

                    logger.error(f"[OKX] API 错误: code={error_code} - {error_msg}")
                    raise Exception(f"OKX API 错误 {error_code}: {error_msg}")

                # 解析响应
                result = response.json()
                okx_code = result.get("code", "")

                # OKX 业务错误码（非 "0" 表示失败）
                if okx_code != "0":
                    okx_msg = result.get("msg", "未知错误")

                    # 部分错误可重试（如频率限制的 JSON 返回）
                    if okx_code == "50011" and attempt < MAX_RETRY_COUNT - 1:
                        # 50011: Too many requests
                        wait = (attempt + 1) * 2
                        logger.warning(
                            f"[OKX] 请求过于频繁 (code={okx_code}), "
                            f"{wait}s 后重试 (attempt {attempt + 1}/{MAX_RETRY_COUNT})"
                        )
                        time.sleep(wait)
                        continue

                    logger.error(f"[OKX] API 业务错误: code={okx_code}, msg={okx_msg}")
                    raise Exception(f"OKX API 错误 {okx_code}: {okx_msg}")

                # 成功返回 data 字段
                return result

            except requests.exceptions.Timeout:
                if attempt < MAX_RETRY_COUNT - 1:
                    logger.warning(
                        f"[OKX] 请求超时: {method_upper} {endpoint}, 重试中 "
                        f"(attempt {attempt + 1}/{MAX_RETRY_COUNT})"
                    )
                    continue
                raise Exception(f"OKX API 请求超时: {method_upper} {endpoint}")

            except requests.exceptions.ConnectionError as e:
                if attempt < MAX_RETRY_COUNT - 1:
                    wait = (attempt + 1) * 2
                    logger.warning(
                        f"[OKX] 连接错误: {e}, {wait}s 后重试"
                    )
                    time.sleep(wait)
                    continue
                raise Exception(f"OKX API 连接失败: {method_upper} {endpoint} - {e}")

            except Exception:
                # 非 requests 异常直接抛出，不重试
                raise

        raise RuntimeError(
            f"OKX 请求重试循环异常退出: {method_upper} {endpoint}"
        )

    def _get_signed(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送带签名的 GET 请求。"""
        return self._request("GET", endpoint, params=params, signed=True)

    def _post_signed(self, endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """发送带签名的 POST 请求。"""
        return self._request("POST", endpoint, body=body, signed=True)

    def _get_public(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送无需签名的 GET 请求。"""
        return self._request("GET", endpoint, params=params, signed=False)

    # ========================================================================
    # 符号转换辅助方法
    # ========================================================================

    def _to_okx_symbol(self, symbol: str) -> str:
        """
        将内部符号转换为 OKX instId。

        Args:
            symbol: 内部符号（如 "BTC" 或 "BTCUSDT"）

        Returns:
            OKX instId（如 "BTC-USDT-SWAP"）
        """
        return _to_inst_id(symbol)

    @staticmethod
    def _from_okx_symbol(inst_id: str) -> str:
        """
        将 OKX instId 转换为内部符号。

        Args:
            inst_id: OKX 产品 ID（如 "BTC-USDT-SWAP"）

        Returns:
            内部符号（如 "BTC"）
        """
        return _to_internal_symbol(inst_id)

    # ========================================================================
    # 行情数据方法
    # ========================================================================

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取指定交易对的最新行情。

        Args:
            symbol: 内部符号（如 "BTC"）

        Returns:
            {"symbol": "BTC", "price": 65000.5}
        """
        inst_id = self._to_okx_symbol(symbol)
        result = self._get_public("/api/v5/market/ticker", {"instId": inst_id})

        data_list = result.get("data", [])
        if not data_list:
            raise ValueError(f"OKX 未返回 {symbol} 的行情数据")

        ticker = data_list[0]
        price = float(ticker.get("last", 0))
        if price <= 0:
            raise ValueError(f"OKX 返回 {symbol} 价格无效: {price}")

        return {
            "symbol": symbol,
            "price": price,
            "okx_inst_id": inst_id,
        }

    def get_mark_price(self, symbol: str) -> float:
        """
        获取标记价格。

        使用 /api/v5/public/price-limit 接口或从 ticker 中获取 markPx。
        实际使用 /api/v5/market/index-tickers?instId=BTC-USDT 来获取现货指数价格，
        但我们用 mark-price 接口。

        Args:
            symbol: 内部符号

        Returns:
            标记价格（float）
        """
        inst_id = self._to_okx_symbol(symbol)
        # 使用 mark-price 接口获取标记价格
        result = self._get_public("/api/v5/public/mark-price", {"instId": inst_id})

        data_list = result.get("data", [])
        if not data_list:
            raise ValueError(f"OKX 未返回 {symbol} 的标记价格")

        mark_price = float(data_list[0].get("markPx", 0))
        if mark_price <= 0:
            raise ValueError(f"OKX 返回 {symbol} 的标记价格无效: {mark_price}")

        return mark_price

    def fetch_price(self, symbol: str) -> float:
        """
        获取最新成交价（与 BinanceTradingClient.fetch_price 兼容）。

        Args:
            symbol: 内部符号

        Returns:
            最新价格（float）
        """
        return self.get_ticker(symbol)["price"]

    # ========================================================================
    # 账户相关方法
    # ========================================================================

    def get_balance(self) -> Dict[str, Any]:
        """
        获取账户余额信息。

        Returns:
            余额字典，字段与 Binance/Hyperliquid 统一格式对齐：
            - total_equity: 总权益（USD）
            - available_balance: 可用余额
            - used_margin: 已用保证金
            - unrealized_pnl: 未实现盈亏
            - margin_usage_percent: 保证金使用率
        """
        result = self._get_signed("/api/v5/account/balance")

        data_list = result.get("data", [])
        if not data_list:
            raise ValueError("OKX 未返回账户余额数据")

        # 查找 USDT 余额（OKX 返回所有币种的余额列表）
        total_equity = 0.0
        available_balance = 0.0
        used_margin = 0.0
        unrealized_pnl = 0.0

        for item in data_list:
            details = item.get("details", [])
            for detail in details:
                ccy = detail.get("ccy", "")
                if ccy == "USDT":
                    total_equity = float(detail.get("eq", 0) or 0)
                    available_balance = float(detail.get("availEq", 0) or 0)
                    used_margin = max(total_equity - available_balance, 0)
                    unrealized_pnl = float(detail.get("upl", 0) or 0)
                    break

        # 使用账户总览接口获取保证金额详情
        try:
            account_result = self._get_signed("/api/v5/account/account-position-risk")
            account_data = account_result.get("data", [])
            if account_data:
                account_info = account_data[0]
                # adjEq 包含未实现盈亏的总权益
                adj_eq = float(account_info.get("adjEq", 0) or 0)
                if adj_eq > 0:
                    total_equity = adj_eq
                # 提取保证金使用详情
                margin_ratio = float(account_info.get("mgnRatio", 0) or 0)
                if margin_ratio > 0 and total_equity > 0:
                    used_margin = float(account_info.get("imr", 0) or 0)
                    available_balance = total_equity - used_margin
        except Exception as e:
            logger.warning(f"[OKX] 获取账户风险数据失败，使用余额数据: {e}")

        margin_usage_percent = round(
            (used_margin / total_equity * 100), 1
        ) if total_equity > 0 else 0.0

        return {
            "environment": self.environment,
            "total_equity": round(total_equity, 2),
            "available_balance": round(available_balance, 2),
            "used_margin": round(used_margin, 2),
            "maintenance_margin": round(used_margin * 0.5, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "margin_usage_percent": margin_usage_percent,
            "timestamp": int(time.time() * 1000),
            "source": "live",
        }

    def get_account_state(self, db=None) -> Dict[str, Any]:
        """
        获取账户状态（兼容 HyperliquidTradingClient.get_account_state）。

        Args:
            db: 数据库会话（用于 Hyperliquid 兼容，OKX 不使用）

        Returns:
            字典，字段与 Binance/Hyperliquid 统一格式对齐
        """
        balance = self.get_balance()
        return {
            "available_balance": balance.get("available_balance", 0.0),
            "total_equity": balance.get("total_equity", 0.0),
            "used_margin": balance.get("used_margin", 0.0),
            "margin_usage_percent": balance.get("margin_usage_percent", 0.0),
            "maintenance_margin": balance.get("maintenance_margin", 0.0),
        }

    # ========================================================================
    # 持仓相关方法
    # ========================================================================

    def get_positions(
        self, db=None, include_timing: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取所有未平仓的永续合约持仓。

        Args:
            db: 数据库会话（兼容参数，OKX 不使用）
            include_timing: 是否包含开仓时间（OKX 暂未实现开仓时间回推）

        Returns:
            持仓字典列表，统一格式：
            - coin: 内部符号（如 "BTC"）
            - szi: 持仓数量（正=多，负=空）
            - entry_px: 平均开仓价
            - position_value: 名义价值
            - unrealized_pnl: 未实现盈亏
            - leverage: 当前杠杆倍数
            - liquidation_px: 预估强平价
            - margin_used: 占用保证金
            - leverage_type: "cross" 或 "isolated"
            - side: "Long" 或 "Short"
        """
        # [OKX 修复] 去掉 instType 参数：带 query params 的请求签名在测试网返回 50113
        result = self._get_signed("/api/v5/account/positions")

        data_list = result.get("data", [])
        positions = []

        # [OKX] 杠杆信息直接从持仓数据获取，不再额外调 API
        leverage_map = {}

        for pos in data_list:
            pos_size = float(pos.get("pos", 0) or 0)
            avail_pos = float(pos.get("availPos", 0) or 0)

            # 跳过未持仓的品种
            if abs(pos_size) < 1e-8 and abs(avail_pos) < 1e-8:
                continue

            inst_id = pos.get("instId", "")
            symbol = self._from_okx_symbol(inst_id)

            side = "Long" if pos_size > 0 else "Short"

            entry_price = float(pos.get("avgPx", 0) or 0)
            mark_price = float(pos.get("markPx", 0) or 0)
            notional = float(pos.get("notionalUsd", 0) or 0)
            unrealized_pnl = float(pos.get("upl", 0) or 0)
            margin_used = float(pos.get("imr", 0) or 0)
            liquidation_px = float(pos.get("liqPx", 0) or 0)
            leverage = float(pos.get("lever", 1) or 1)

            mgn_mode = pos.get("mgnMode", "cross")
            leverage_type = "isolated" if mgn_mode == "isolated" else "cross"

            # 从 leverage_map 获取更准确的杠杆值
            if symbol in leverage_map:
                if leverage_map[symbol]["leverage"] > 1:
                    leverage = leverage_map[symbol]["leverage"]

            positions.append({
                "coin": symbol,
                "szi": pos_size,
                "entry_px": entry_price,
                "position_value": notional,
                "unrealized_pnl": unrealized_pnl,
                "leverage": int(leverage),
                "liquidation_px": liquidation_px,
                "margin_used": margin_used,
                "leverage_type": leverage_type,
                "side": side,
                # 额外字段（兼容 Binance）
                "symbol": symbol,
                "mark_price": mark_price,
                "maint_margin": float(pos.get("mmr", 0) or 0),
                "position_side": "BOTH",
                "max_leverage": 0,
                "opened_at": None,
                "opened_at_str": None,
                "holding_duration_seconds": None,
                "holding_duration_str": None,
            })

        logger.info(f"[OKX] 获取到 {len(positions)} 个持仓")
        return positions

    # ========================================================================
    # 杠杆相关方法
    # ========================================================================

    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        设置指定交易对的杠杆倍数。

        ⚠️ OKX 平台限制：杠杆按交易对(instId)统一设置，同一交易对下多空持仓
        共用同一杠杆倍率。这是 OKX 永续合约的平台行为，并非代码限制。

        因此：若已有持仓，调用此方法会同时影响该交易对所有持仓的杠杆。
        建议用户在有持仓时避免修改杠杆。

        调用 OKX POST /api/v5/account/set-leverage 接口。

        Args:
            symbol: 内部符号（如 "BTC"）
            leverage: 目标杠杆倍数（1-125）

        Returns:
            API 响应数据
        """
        inst_id = self._to_okx_symbol(symbol)

        if leverage < 1:
            raise ValueError(f"无效的杠杆倍数: {leverage}，必须 >= 1")

        body = {
            "instId": inst_id,
            "lever": str(leverage),
            "mgnMode": "cross",  # 默认全仓模式
        }

        result = self._post_signed("/api/v5/account/set-leverage", body)
        logger.info(f"[OKX] 设置杠杆: {symbol} ({inst_id}) -> {leverage}x")
        return result

    # ========================================================================
    # 合约面值查询（OKX sz 单位是合约张数，需用面值换算）
    # ========================================================================

    # [OKX] 合约面值缓存（instId → ctVal）
    _ct_val_cache: Dict[str, float] = {}

    def _get_ct_val(self, inst_id: str) -> float:
        """获取 OKX 合约面值（1 张合约代表多少币）。

        BTC-USDT-SWAP → 0.01, ETH-USDT-SWAP → 0.1, 大部分 → 1.0
        """
        if inst_id in self._ct_val_cache:
            return self._ct_val_cache[inst_id]
        try:
            resp = self._get_public("/api/v5/public/instruments", {
                "instType": "SWAP", "instId": inst_id
            })
            data = resp.get("data", [])
            ct_val = float(data[0].get("ctVal", "1")) if data else 1.0
        except Exception:
            ct_val = 1.0
        self._ct_val_cache[inst_id] = ct_val
        logger.info(f"[OKX] ctVal({inst_id})={ct_val}")
        return ct_val

    # ========================================================================
    # 订单相关方法
    # ========================================================================

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
        leverage: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        下单（不含止盈止损）。

        Args:
            symbol: 内部符号
            side: 方向 "BUY" 或 "SELL"
            quantity: 下单数量（张数）
            order_type: "MARKET" 或 "LIMIT"
            price: 限价（LIMIT 订单必填）
            time_in_force: 有效期（GTC/IOC/FOK）
            reduce_only: 是否只减仓
            leverage: 杠杆倍数（可选，如果设置则先调用 set_leverage）

        Returns:
            订单结果，统一格式:
            - order_id: OKX 订单 ID
            - symbol: 内部符号
            - side: 方向
            - quantity: 数量
            - price: 价格
            - status: 订单状态
            - raw_response: 原始 API 响应
        """
        inst_id = self._to_okx_symbol(symbol)

        # [OKX 修复] 杠杆设置：仅无持仓时设置，避免覆盖已有持仓杠杆
        if leverage and not reduce_only:
            existing_positions = self.get_positions()
            has_position = any(p['coin'] == symbol.upper() and abs(p.get('szi', 0)) > 1e-8 for p in existing_positions)
            if has_position:
                logger.info(f"[OKX] {symbol} 已有持仓，跳过杠杆设置")
            else:
                try:
                    self.set_leverage(symbol, leverage)
                except Exception as e:
                    logger.error(f"[OKX] 设置杠杆失败: {e}")

        # [OKX 修复] sz 换算：币数量 → 合约张数
        ct_val = self._get_ct_val(inst_id)
        contracts = quantity / ct_val
        sz_contracts = str(max(1, int(contracts))) if contracts >= 0.5 else "1"  # [OKX] 最小1张

        # 构建下单参数
        body: Dict[str, Any] = {
            "instId": inst_id,
            "tdMode": "cross",
            "side": side.lower(),
            "posSide": "short" if (reduce_only and side.upper() == "BUY") else ("long" if (reduce_only and side.upper() == "SELL") else ("long" if side.upper() == "BUY" else "short")),  # [OKX] hedge mode
            "ordType": order_type.lower(),
            "sz": sz_contracts,
        }

        if reduce_only:
            body["reduceOnly"] = "true"  # [OKX 修复] 布尔 → 字符串

        if order_type.lower() == "limit":
            if price is None:
                raise ValueError("限价单必须提供 price 参数")
            body["px"] = str(price)
        else:
            # 市价单：不传 px
            pass

        result = self._post_signed("/api/v5/trade/order", body)

        data_list = result.get("data", [])
        order_data = data_list[0] if data_list else {}
        ord_id = order_data.get("ordId", "")
        s_code = order_data.get("sCode", "")

        if s_code != "0":
            s_msg = order_data.get("sMsg", "未知错误")
            logger.error(f"[OKX] 下单失败: sCode={s_code}, sMsg={s_msg}")
            return {
                "order_id": ord_id or None,
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price or 0,
                "avg_price": 0,
                "executed_qty": 0,
                "status": "error",
                "error": s_msg,
                "environment": self.environment,
                "raw_response": result,
            }

        logger.info(
            f"[OKX] 下单成功: {side} {quantity} {inst_id} "
            f"@ {order_type} - ordId={ord_id}"
        )

        return {
            "order_id": ord_id,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "price": price or 0,
            "avg_price": 0,
            "executed_qty": 0,
            "status": "filled" if order_type.lower() == "market" else "resting",
            "environment": self.environment,
            "raw_response": result,
        }

    def place_order_with_tpsl(
        self,
        db,
        symbol: str,
        is_buy: bool,
        size: float,
        price: float,
        leverage: int = 1,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
        take_profit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        order_type: str = "MARKET",
        tp_execution: str = "market",
        sl_execution: str = "market",
    ) -> Dict[str, Any]:
        """
        下单并附加止盈止损单。

        使用 OKX 的 attachAlgoOrds 功能，在主订单创建时同步附加
        止损和止盈算法单，避免分两次调用。

        Args:
            db: 数据库会话（兼容参数，OKX 不使用）
            symbol: 内部符号
            is_buy: True=做多，False=做空
            size: 下单数量
            price: 价格参考
            leverage: 杠杆倍数
            time_in_force: 有效期（GTC/IOC/FOK）
            reduce_only: 是否只减仓
            take_profit_price: 止盈触发价（可选）
            stop_loss_price: 止损触发价（可选）
            order_type: "MARKET" 或 "LIMIT"
            tp_execution: 止盈执行方式（OKX 忽略此参数）
            sl_execution: 止损执行方式（OKX 忽略此参数）

        Returns:
            统一格式的结果字典:
            - status: "filled" | "resting" | "error"
            - order_id: 主订单 ID
            - tp_order_id: 止盈算法单 ID（若有）
            - sl_order_id: 止损算法单 ID（若有）
            - filled_qty: 已成交数量
            - avg_price: 成交均价
            - errors: 错误消息列表
        """
        # 参数校验
        if leverage < 1:
            raise ValueError(f"无效杠杆: {leverage}（必须 >= 1）")
        if size <= 0:
            raise ValueError(f"无效数量: {size}（必须 > 0）")
        if price <= 0 and order_type.upper() == "LIMIT":
            raise ValueError(f"无效价格: {price}（限价单必须提供正价格）")

        inst_id = self._to_okx_symbol(symbol)
        side_lower = "buy" if is_buy else "sell"
        close_side = "sell" if is_buy else "buy"

        # tif 规范化（支持 Hyperliquid 风格的 "Ioc"/"Gtc" 格式）
        tif_mapping = {
            "ioc": "ioc",
            "gtc": "gtc",
            "fok": "fok",
        }
        tif_normalized = tif_mapping.get(
            str(time_in_force).lower(),
            str(time_in_force).lower(),
        )

        logger.info(
            f"[OKX] 下单: {symbol} ({inst_id}) {side_lower.upper()} "
            f"size={size} price={price} leverage={leverage}x "
            f"TIF={tif_normalized} TP={take_profit_price} SL={stop_loss_price}"
        )

        # 结果容器
        result: Dict[str, Any] = {
            "status": "error",
            "order_id": None,
            "tp_order_id": None,
            "sl_order_id": None,
            "filled_qty": 0.0,
            "avg_price": 0.0,
            "environment": self.environment,
            "errors": [],
        }

        try:
            # [OKX 修复] 杠杆设置：仅在没有已有持仓时设置，避免覆盖现有持仓的杠杆
            if not reduce_only and leverage > 1:
                existing_positions = self.get_positions()
                has_position = any(p['coin'] == symbol.upper() and abs(p.get('szi', 0)) > 1e-8 for p in existing_positions)
                if has_position:
                    logger.info(f"[OKX] {symbol} 已有持仓，跳过杠杆设置以保留现有杠杆")
                else:
                    try:
                        set_lev_result = self.set_leverage(symbol, leverage)
                        logger.info(f"[OKX] 杠杆已设置: {symbol} -> {leverage}x, resp={set_lev_result}")
                    except Exception as e:
                        err_msg = f"[OKX] 设置杠杆失败: {symbol} {leverage}x: {e}"
                        logger.error(err_msg)
                        result["errors"].append(err_msg)

            # [OKX 修复] sz 单位换算：币数量 → 合约张数
            # OKX 的 sz 是合约张数，1 张 = ctVal 个币
            # 例: BTC ctVal=0.01, 买 0.05 BTC → sz = 0.05/0.01 = 5 张
            ct_val = self._get_ct_val(inst_id)
            contracts = size / ct_val
            # [OKX 修复] OKX 最小 1 张合约，不足 1 张的取整为 1 张
            if contracts < 1.0:
                sz_contracts = "1"
                logger.warning(f"[OKX] sz={contracts}张 < 最低1张, 自动设为1张 (≈{round(ct_val * 1, 6)}个币)")
            else:
                sz_contracts = str(int(contracts))
            logger.info(f"[OKX] sz换算: {size}币 / ctVal={ct_val} = {sz_contracts}张合约")

            # 构建下单请求体
            body: Dict[str, Any] = {
                "instId": inst_id,
                "tdMode": "cross",
                "side": side_lower,
                "posSide": "short" if (reduce_only and is_buy) else ("long" if (reduce_only and not is_buy) else ("long" if is_buy else "short")),  # [OKX] hedge mode requires posSide
                "ordType": order_type.lower(),
                "sz": sz_contracts,
            }

            if reduce_only:
                body["reduceOnly"] = "true"

            if order_type.lower() == "limit":
                body["px"] = str(price)

            # ============================================================
            # 构建附加止盈止损单（attachAlgoOrds）
            # OKX attachAlgoOrds 结构:
            # [
            #   {
            #     "attachAlgoClOrdId": "",  # 客户自定义算法单ID（可选）
            #     "tpTriggerPx": "",         # 止盈触发价
            #     "tpOrdPx": "",             # 止盈委托价（-1 表示市价）
            #     "tpTriggerPxType": "last", # 触发价格类型（last/mark/index）
            #     "slTriggerPx": "",         # 止损触发价
            #     "slOrdPx": "",             # 止损委托价（-1 表示市价）
            #     "slTriggerPxType": "last", # 触发价格类型
            #     "sz": ""                   # 数量（可选）
            #   }
            # ]
            # ============================================================
            if (take_profit_price and take_profit_price > 0) or (
                stop_loss_price and stop_loss_price > 0
            ):
                algo_ord: Dict[str, Any] = {
                    "tpTriggerPxType": "last",
                    "slTriggerPxType": "last",
                }

                if take_profit_price and take_profit_price > 0:
                    # 止盈委托价：
                    # -1 表示市价（OKX 不支持限价止盈的 ordPx 为 -1 以外值？）
                    # 实际上 OKX 的 tpOrdPx: "" 或 "-1" 都表示市价委托
                    algo_ord["tpTriggerPx"] = str(take_profit_price)
                    algo_ord["tpOrdPx"] = "-1"  # 市价止盈

                if stop_loss_price and stop_loss_price > 0:
                    algo_ord["slTriggerPx"] = str(stop_loss_price)
                    algo_ord["slOrdPx"] = "-1"  # 市价止损

                body["attachAlgoOrds"] = [algo_ord]
                logger.info(
                    f"[OKX] 附加止盈止损: TP={take_profit_price}, SL={stop_loss_price}"
                )

            # 发送下单请求
            logger.warning(  # [OKX DEBUG] 使用 WARNING 级别确保在生产日志中可见
                f"[OKX ORDER PAYLOAD] body={json.dumps(body, ensure_ascii=False)}"
            )
            order_result = self._post_signed("/api/v5/trade/order", body)
            logger.warning(  # [OKX DEBUG] 打印完整响应
                f"[OKX ORDER RESPONSE] raw={json.dumps(order_result, ensure_ascii=False)[:800]}"
            )

            data_list = order_result.get("data", [])
            if not data_list:
                result["errors"].append("OKX 未返回订单数据")
                return result

            order_data = data_list[0]
            ord_id = order_data.get("ordId", "")
            s_code = order_data.get("sCode", "")
            s_msg = order_data.get("sMsg", "")

            if s_code != "0":
                result["errors"].append(f"OKX 下单失败: sCode={s_code}, sMsg={s_msg}")
                result["status"] = "error"
                logger.error(f"[OKX] 下单失败: {s_code} - {s_msg}")

                # IOC 无流动性时返回特殊错误，上层调用者会重试 GTC
                if "51025" in str(s_code):
                    # 51025: Order placement failed due to risk management
                    result["error"] = s_msg
                return result

            # 解析订单结果
            result["order_id"] = ord_id

            # OKX 市价单通常是立即成交
            if order_type.lower() == "market":
                result["status"] = "filled"
                result["filled_qty"] = size
                result["avg_price"] = price
            else:
                result["status"] = "resting"

            # ============================================================
            # 提取附加的止盈止损算法单ID
            # OKX 在响应数据的 attachAlgoOrds 字段中返回
            # 格式: [{"algoId": "...", "attachAlgoClOrdId": "...", ...}, ...]
            # ============================================================
            attach_algo_ords = order_data.get("attachAlgoOrds", [])
            if attach_algo_ords:
                for algo_item in attach_algo_ords:
                    algo_id = algo_item.get("algoId", "")
                    att_cl_ord_id = algo_item.get("attachAlgoClOrdId", "")
                    # 根据 attachAlgoClOrdId 区分 TP 和 SL
                    # 如果无法区分，根据是否大于当前价来判断
                    if not algo_id:
                        continue

                    if att_cl_ord_id:
                        if "tp" in att_cl_ord_id.lower():
                            result["tp_order_id"] = algo_id
                        elif "sl" in att_cl_ord_id.lower():
                            result["sl_order_id"] = algo_id
                        else:
                            # 无法区分，默认第一个为 TP，第二个为 SL
                            if result["tp_order_id"] is None:
                                result["tp_order_id"] = algo_id
                            else:
                                result["sl_order_id"] = algo_id
                    else:
                        # 无 clOrdId，根据价格方向判断
                        # 做多：止盈价 > 开仓价, 止损价 < 开仓价
                        # 做空：止盈价 < 开仓价, 止损价 > 开仓价
                        if result["tp_order_id"] is None:
                            result["tp_order_id"] = algo_id
                        else:
                            result["sl_order_id"] = algo_id

            logger.info(
                f"[OKX] 下单完成: ordId={ord_id}, status={result['status']}, "
                f"TP={result['tp_order_id']}, SL={result['sl_order_id']}"
            )

            return result

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["errors"].append(str(e))
            logger.error(f"[OKX] place_order_with_tpsl 异常: {e}", exc_info=True)
            return result

    def close_position(
        self, symbol: str, cancel_tpsl: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        市价全平指定交易对的持仓。

        Args:
            symbol: 内部符号
            cancel_tpsl: 是否同时撤销关联的止盈止损单（OKX 市价平仓时止盈止损自动取消）

        Returns:
            订单结果，无持仓时返回 None
        """
        positions = self.get_positions()
        position = next(
            (p for p in positions if p["symbol"] == symbol.upper()),
            None,
        )

        if not position or abs(position["szi"]) < 1e-8:
            logger.info(f"[OKX] {symbol} 无持仓，无需平仓")
            return None

        pos_size = abs(position["szi"])
        is_long = position["szi"] > 0
        close_side = "sell" if is_long else "buy"

        logger.info(
            f"[OKX] 市价平仓: {symbol} {'多头' if is_long else '空头'} x{pos_size}"
        )

        # 如果指定了 cancel_tpsl，先撤销关联的算法单
        if cancel_tpsl:
            try:
                self._cancel_tpsl_orders(symbol)
            except Exception as e:
                logger.warning(f"[OKX] 撤销止盈止损单失败: {e}")

        # [OKX 修复] 市价平仓 — pos_size 已是合约张数，无需再换算
        inst_id = self._to_okx_symbol(symbol)
        close_contracts = str(int(pos_size)) if pos_size >= 1 else "1"
        body: Dict[str, Any] = {
            "instId": inst_id,
            "tdMode": position.get("mgnMode", "cross"),  # [OKX] 使用持仓的实际保证金模式
            "side": close_side,
            "posSide": "long" if is_long else "short",
            "ordType": "market",
            "sz": close_contracts,
            "reduceOnly": "true",
        }

        order_result = self._post_signed("/api/v5/trade/order", body)
        data_list = order_result.get("data", [])
        order_data = data_list[0] if data_list else {}

        ord_id = order_data.get("ordId", "")
        s_code = order_data.get("sCode", "")

        if s_code != "0":
            s_msg = order_data.get("sMsg", "未知错误")
            logger.error(f"[OKX] 平仓失败: {s_code} - {s_msg}")
            raise Exception(f"OKX 平仓失败: {s_msg}")

        logger.info(f"[OKX] 平仓成功: {symbol}, ordId={ord_id}")

        return {
            "order_id": ord_id,
            "symbol": symbol,
            "side": close_side.upper(),
            "quantity": pos_size,
            "status": "filled",
            "environment": self.environment,
            "raw_response": order_result,
        }

    def _cancel_tpsl_orders(self, symbol: str) -> int:
        """
        撤销指定交易对的所有未触发算法单（止盈止损单）。

        OKX 中，止盈止损单属于 algoOrder 类型，需要先获取列表再逐个撤销。

        Args:
            symbol: 内部符号

        Returns:
            已撤销的算法单数量
        """
        inst_id = self._to_okx_symbol(symbol)
        cancelled = 0

        try:
            # [OKX 修复] 不带 query params 避免 50113，获取后客户端过滤
            result = self._get_signed("/api/v5/trade/orders-algo-pending")
            all_orders = result.get("data", [])
            algo_orders = [o for o in all_orders if o.get("instId") == inst_id]
            for order in algo_orders:
                algo_id = order.get("algoId", "")
                if algo_id:
                    try:
                        cancel_body = {
                            "instId": inst_id,
                            "algoId": algo_id,
                        }
                        self._post_signed(
                            "/api/v5/trade/cancel-algos", cancel_body
                        )
                        cancelled += 1
                        logger.info(f"[OKX] 撤销算法单: algoId={algo_id}")
                    except Exception as e:
                        logger.warning(
                            f"[OKX] 撤销算法单 {algo_id} 失败: {e}"
                        )

            logger.info(f"[OKX] 共撤销 {cancelled} 个算法单 for {symbol}")
            return cancelled

        except Exception as e:
            logger.warning(f"[OKX] 获取/撤销算法单失败: {e}")
            return cancelled

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        撤销指定订单。

        Args:
            symbol: 内部符号
            order_id: OKX 订单 ID
            client_order_id: 客户自定义订单 ID（与 order_id 二选一）

        Returns:
            撤销结果
        """
        inst_id = self._to_okx_symbol(symbol)
        body: Dict[str, str] = {"instId": inst_id}

        if order_id:
            body["ordId"] = str(order_id)
        elif client_order_id:
            body["clOrdId"] = str(client_order_id)
        else:
            raise ValueError("必须提供 order_id 或 client_order_id")

        result = self._post_signed("/api/v5/trade/cancel-order", body)
        logger.info(f"[OKX] 撤销订单: {symbol} ordId={order_id or client_order_id}")
        return result

    def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """
        撤销指定交易对的所有挂单。

        Args:
            symbol: 内部符号

        Returns:
            撤销结果
        """
        inst_id = self._to_okx_symbol(symbol)

        # 获取挂单列表
        pending = self._get_signed("/api/v5/trade/orders-pending", {
            "instId": inst_id,
        })

        cancelled_count = 0
        errors = []

        for order in pending.get("data", []):
            ord_id = order.get("ordId", "")
            if ord_id:
                try:
                    self.cancel_order(symbol, order_id=ord_id)
                    cancelled_count += 1
                except Exception as e:
                    errors.append({"ordId": ord_id, "error": str(e)})

        logger.info(f"[OKX] 撤销全部挂单: {symbol} -> {cancelled_count} 个")

        return {
            "symbol": symbol,
            "cancelled_count": cancelled_count,
            "errors": errors,
        }

    def get_open_orders(
        self, db=None, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取当前挂单列表（含未触发的止盈止损算法单）。

        Args:
            db: 数据库会话（兼容参数）
            symbol: 可选的交易对筛选

        Returns:
            统一格式的订单列表
        """
        orders = []

        # 获取普通挂单
        params: Dict[str, Any] = {"instType": "SWAP"}
        if symbol:
            params["instId"] = self._to_okx_symbol(symbol)

        try:
            pending = self._get_signed(
                "/api/v5/trade/orders-pending", params
            )
            for o in pending.get("data", []):
                inst_id = o.get("instId", "")
                sym = self._from_okx_symbol(inst_id)

                side_raw = o.get("side", "")
                side = "Buy" if side_raw == "buy" else "Sell"
                reduce_only = o.get("reduceOnly", "") == "true"

                if side == "Buy":
                    direction = "Close Short" if reduce_only else "Open Long"
                else:
                    direction = "Close Long" if reduce_only else "Open Short"

                orders.append({
                    "order_id": o.get("ordId", ""),
                    "symbol": sym,
                    "side": side,
                    "direction": direction,
                    "order_type": o.get("ordType", "limit").upper(),
                    "size": float(o.get("sz", 0) or 0),
                    "price": float(o.get("px", 0) or 0),
                    "trigger_price": None,
                    "reduce_only": reduce_only,
                    "is_trigger": False,
                    "trigger_condition": None,
                    "timestamp": int(o.get("cTime", 0) or 0),
                })

        except Exception as e:
            logger.warning(f"[OKX] 获取挂单列表失败: {e}")

        # 获取未触发的算法单（止盈止损）
        try:
            algo_params: Dict[str, Any] = {"algoOrdType": "conditional"}
            if symbol:
                algo_params["instId"] = self._to_okx_symbol(symbol)

            algo_pending = self._get_signed(
                "/api/v5/trade/orders-algo-pending", algo_params
            )
            for o in algo_pending.get("data", []):
                inst_id = o.get("instId", "")
                sym = self._from_okx_symbol(inst_id)

                side_raw = o.get("side", "")
                side = "Buy" if side_raw == "buy" else "Sell"

                # 从 ordType 判断是 TP 还是 SL
                ord_type = o.get("ordType", "conditional")
                if "tp" in str(ord_type).lower():
                    order_type_label = "Take Profit"
                elif "sl" in str(ord_type).lower():
                    order_type_label = "Stop Loss"
                else:
                    order_type_label = "Conditional"

                trigger_px = float(o.get("triggerPx", 0) or 0)

                orders.append({
                    "order_id": o.get("algoId", ""),
                    "symbol": sym,
                    "side": side,
                    "direction": "Close Long" if side == "Sell" else "Close Short",
                    "order_type": order_type_label,
                    "size": float(o.get("sz", 0) or 0),
                    "price": float(o.get("ordPx", 0) or 0),
                    "trigger_price": trigger_px,
                    "reduce_only": True,
                    "is_trigger": True,
                    "trigger_condition": (
                        f"Mark Price <= {trigger_px}"
                        if "tp" in str(ord_type).lower()
                        else f"Mark Price >= {trigger_px}"
                    ),
                    "timestamp": int(o.get("cTime", 0) or 0),
                })

        except Exception as e:
            logger.warning(f"[OKX] 获取算法单列表失败: {e}")

        # 按时间倒序排列
        orders.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

        return orders

    def get_open_orders_formatted(
        self, db=None, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取格式化的挂单列表（与 HyperliquidTradingClient.get_open_orders_formatted 兼容）。

        在 get_open_orders 基础上增加 order_value 和 order_time 字段。
        """
        orders = self.get_open_orders(db, symbol)

        for o in orders:
            price = float(o.get("price", 0))
            size = float(o.get("size", 0))
            o["order_value"] = price * size
            o["original_size"] = size

            ts = o.get("timestamp", 0)
            o["order_time"] = (
                datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if ts
                else "N/A"
            )

        return orders

    # ========================================================================
    # 成交记录相关方法
    # ========================================================================

    def get_user_fills(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        获取用户历史成交记录。

        Args:
            limit: 最大记录数

        Returns:
            统一格式的成交记录列表:
            - oid: 订单 ID
            - coin: 内部符号
            - side: "B"（买）或 "A"（卖）
            - px: 成交价格
            - sz: 成交数量
            - time: 成交时间戳（毫秒）
            - closedPnl: 已实现盈亏
            - fee: 手续费
        """
        result = self._get_signed("/api/v5/trade/fills-history", {
            "instType": "SWAP",
            "limit": str(min(limit, 100)),
        })

        fills = []
        for fill in result.get("data", []):
            inst_id = fill.get("instId", "")
            side_raw = fill.get("side", "")

            fills.append({
                "oid": str(fill.get("ordId", "")),
                "coin": self._from_okx_symbol(inst_id),
                "side": "B" if side_raw == "buy" else "A",
                "px": str(fill.get("fillPx", "0")),
                "sz": str(fill.get("fillSz", "0")),
                "time": int(fill.get("ts", 0) or 0),
                "closedPnl": str(fill.get("fillPnl", "0")),
                "fee": str(fill.get("fee", "0")),
                "main_order_id": None,
                "order_type": "main",
            })

        logger.info(f"[OKX] 获取 {len(fills)} 条成交记录")
        return fills

    def get_recent_closed_trades(
        self, db=None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取最近已平仓的交易（与 Hyperliquid 兼容）。

        使用成交历史接口，筛选具有 realizedPnl 的记录。

        Args:
            db: 数据库会话（兼容参数）
            limit: 最大返回数量

        Returns:
            已平仓交易列表
        """
        fills = self.get_user_fills(limit=100)

        # 筛选已实现盈亏的记录（平仓成交）
        closed = []
        for f in fills:
            pnl = float(f.get("closedPnl", 0) or 0)
            if abs(pnl) > 1e-8:
                ts = f.get("time", 0)
                side = "Long" if f["side"] == "A" else "Short"
                direction = "WIN" if pnl > 0 else "LOSS"

                closed.append({
                    "symbol": f["coin"],
                    "side": side,
                    "close_time": (
                        datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S UTC"
                        )
                        if ts
                        else "N/A"
                    ),
                    "close_timestamp": ts,
                    "close_price": float(f["px"]),
                    "realized_pnl": pnl,
                    "direction": direction,
                    "size": float(f["sz"]),
                })

        closed.sort(key=lambda x: x.get("close_timestamp", 0), reverse=True)
        return closed[:limit]

    def get_trading_stats(self, db=None) -> Dict[str, Any]:
        """
        获取交易统计数据（与 HyperliquidTradingClient 兼容）。

        Returns:
            {
                total_trades, wins, losses, win_rate,
                total_pnl, volume, avg_win, avg_loss,
                profit_factor, gross_profit, gross_loss
            }
        """
        try:
            fills = self.get_user_fills(limit=100)

            closed_fills = []
            for f in fills:
                pnl = float(f.get("closedPnl", 0) or 0)
                if abs(pnl) > 1e-8:
                    closed_fills.append({
                        "pnl": pnl,
                        "time": f.get("time", 0),
                        "symbol": f["coin"],
                    })

            if not closed_fills:
                return {
                    "total_trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "volume": 0.0,
                    "avg_win": 0.0,
                    "avg_loss": 0.0,
                    "profit_factor": 0.0,
                    "gross_profit": 0.0,
                    "gross_loss": 0.0,
                }

            wins = [t for t in closed_fills if t["pnl"] > 0]
            losses = [t for t in closed_fills if t["pnl"] < 0]

            total_trades = len(closed_fills)
            win_count = len(wins)
            loss_count = len(losses)

            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
            gross_profit = sum(t["pnl"] for t in wins) if wins else 0.0
            gross_loss = abs(sum(t["pnl"] for t in losses)) if losses else 0.0
            avg_win = gross_profit / win_count if win_count > 0 else 0.0
            avg_loss = -gross_loss / loss_count if loss_count > 0 else 0.0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

            total_pnl = sum(t["pnl"] for t in closed_fills)

            stats = {
                "total_trades": total_trades,
                "wins": win_count,
                "losses": loss_count,
                "win_rate": round(win_rate, 1),
                "total_pnl": round(total_pnl, 2),
                "volume": 0.0,  # OKX fills API 不含交易量统计
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2),
                "gross_profit": round(gross_profit, 2),
                "gross_loss": round(gross_loss, 2),
            }

            logger.info(
                f"[OKX] 交易统计: {win_count}W/{loss_count}L, PNL=${total_pnl:.2f}"
            )
            return stats

        except Exception as e:
            logger.error(f"[OKX] 获取交易统计失败: {e}", exc_info=True)
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "volume": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "error": str(e),
            }

    # ========================================================================
    # 频率限制信息
    # ========================================================================

    def get_rate_limit(self) -> Dict[str, Any]:
        """
        获取当前 API 频率限制信息。

        Returns:
            {"remaining": ..., "limit": ..., "reset": ...}
        """
        return dict(self._last_rate_limit_info)

    # ========================================================================
    # 其他辅助方法
    # ========================================================================

    def check_rebate_eligibility(self) -> Dict[str, Any]:
        """
        检查返佣资格（OKX 暂无返佣机制，保留接口兼容）。

        Returns:
            {"eligible": False, ...}
        """
        return {
            "eligible": False,
            "rebate_working": False,
            "is_new_user": False,
            "note": "OKX 暂不支持 API 返佣检查",
        }

    def get_income_history(
        self,
        income_type: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        获取账户流水记录（兼容 BinanceTradingClient.get_income_history）。

        OKX 使用 /api/v5/account/bills 接口获取账单流水。

        Args:
            income_type: 账单类型（OKX 使用 billType 参数）
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            limit: 最大记录数

        Returns:
            账单记录列表
        """
        params: Dict[str, Any] = {
            "instType": "SWAP",
            "limit": str(min(limit, 100)),
        }

        if income_type:
            params["billType"] = income_type
        if start_time:
            params["begin"] = str(start_time)
        if end_time:
            params["end"] = str(end_time)

        result = self._get_signed("/api/v5/account/bills", params)
        return result.get("data", [])
