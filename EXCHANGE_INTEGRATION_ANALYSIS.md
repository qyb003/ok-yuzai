# 交易所集成分析报告

> 分析日期：2026-05-31  
> 项目版本：0.9.12  
> 项目名称：Hyper Alpha Arena

---

## 一、交易所集成的抽象层设计

本项目采用 **三层架构 + 适配器模式** 实现多交易所集成：

### 1.1 数据适配层（Data Adapter Layer）

位于 `backend/services/exchanges/`，核心是 **`BaseExchangeAdapter(ABC)`**（[base_adapter.py:93](backend/services/exchanges/base_adapter.py#L93)）。

定义了6个统一数据结构（dataclass）作为所有交易所的"通用语言"：

| 数据结构 | 用途 |
|---|---|
| `UnifiedKline` | K线数据（含taker买卖量） |
| `UnifiedTrade` | 逐笔成交 |
| `UnifiedOrderbook` | 订单簿快照 |
| `UnifiedFunding` | 资金费率 |
| `UnifiedOpenInterest` | 持仓量 |
| `UnifiedSentiment` | 多空比 |

`BaseExchangeAdapter` 是抽象基类，声明了4个必须实现的抽象方法和3个可选方法。目前只有 `BinanceAdapter` 是遵循此模式的完整实现。

> **注意**：Hyperliquid 并未遵循此适配器模式。它使用原生 SDK（`hyperliquid-python-sdk` + CCXT）直接在 `HyperliquidTradingClient` 中实现，而非通过 `BaseExchangeAdapter` 抽象。

### 1.2 交易客户端层（Trading Client Layer）

位于 `backend/services/`，每种交易所拥有独立的交易客户端：

- **`HyperliquidTradingClient`**（[hyperliquid_trading_client.py](backend/services/hyperliquid_trading_client.py)）：基于 EIP-712 签名 + Hyperliquid SDK + CCXT。约3577行。
- **`BinanceTradingClient`**（[binance_trading_client.py](backend/services/binance_trading_client.py)）：基于 HMAC SHA256 签名 + REST API。约1558行。

两个客户端对外暴露**统一的方法签名**以实现互换：

- `get_account_state(db)` → 账户状态
- `get_positions(db, include_timing)` → 持仓列表
- `get_open_orders(db, symbol)` → 挂单列表
- `place_order(db, symbol, is_buy, size, ...)` → 下单
- `place_order_with_tpsl(db, ...)` → 下单+止盈止损
- `cancel_order(db, order_id, symbol)` → 取消订单
- `close_position(symbol)` → 市价平仓
- `get_trading_stats(db)` → 交易统计
- `get_user_fills(limit)` → 用户成交记录

### 1.3 数据持久层（Data Persistence Layer）

- **`ExchangeDataPersistence`**（[data_persistence.py](backend/services/exchanges/data_persistence.py)）：通用持久化服务，接收统一数据结构（`UnifiedKline` 等），写入数据库。通过 `exchange` 字段区分来源。
- **`ExchangeDataPersistence`** 写入的数据库表：`CryptoKline`、`MarketTradesAggregated`、`MarketOrderbookSnapshots`、`MarketAssetMetrics`、`MarketSentimentMetrics`。

### 1.4 数据采集层（Data Collection Layer）

每种交易所拥有独立的采集器：

| 交易所 | REST 采集器 | WebSocket 采集器 | 回填器 |
|---|---|---|---|
| Binance | `BinanceCollector` | `BinanceWSCollector` | `BinanceBackfill` |
| Hyperliquid | 无（使用 `market_flow_collector.py`） | 无独立采集器 | `HyperliquidBackfill` |

### 1.5 前端层

- **`ExchangeContext`**（[ExchangeContext.tsx](frontend/app/contexts/ExchangeContext.tsx)）：React Context 管理当前选中交易所
- **`ExchangeId`** 类型（[exchange.ts](frontend/app/lib/types/exchange.ts)）：`'hyperliquid' | 'binance' | 'aster'`
- **`ExchangeIcon`** 组件（[ExchangeIcon.tsx](frontend/app/components/exchange/ExchangeIcon.tsx)）：交易所图标渲染
- **`ExchangeModal`** 组件（[ExchangeModal.tsx](frontend/app/components/exchange/ExchangeModal.tsx)）：交易所对比弹窗

### 1.6 辅助组件

- **`SymbolMapper`**（[symbol_mapper.py](backend/services/exchanges/symbol_mapper.py)）：内部符号 ↔ 交易所符号的双向转换（如 "BTC" ↔ "BTCUSDT"）
- **`ErrorRegistry`**（[error_registry.py](backend/services/error_registry.py)）：按交易所分类错误模式（`HL = "hyperliquid"`, `BN = "binance"`, `ALL = "all"`）
- **`settings.py`**（[settings.py](backend/config/settings.py)）：交易所配置（`HyperliquidBuilderConfig`, `BinanceBrokerConfig`, `BINANCE_DAILY_QUOTA_LIMIT`）

---

## 二、添加新交易所需要实现的类/接口及方法签名

### 2.1 必须新建的类

#### A. 交易所适配器（Exchange Adapter）— 继承 `BaseExchangeAdapter(ABC)`

```python
class OkxAdapter(BaseExchangeAdapter):
    # === 必须实现的抽象方法 ===

    def _get_exchange_name(self) -> str:
        """返回交易所名称，如 'okx'"""
        pass

    def fetch_klines(
        self,
        symbol: str,           # 内部格式符号，如 "BTC"
        interval: str,         # "1m", "5m", "15m", "30m", "1h", "4h", "1d"
        limit: int = 100,
        start_time: Optional[int] = None,   # 毫秒时间戳
        end_time: Optional[int] = None,     # 毫秒时间戳
    ) -> List[UnifiedKline]:
        """获取K线数据，返回 UnifiedKline 列表"""
        pass

    def fetch_orderbook(
        self, symbol: str, depth: int = 10
    ) -> UnifiedOrderbook:
        """获取订单簿快照"""
        pass

    def fetch_funding_rate(self, symbol: str) -> UnifiedFunding:
        """获取当前资金费率"""
        pass

    def fetch_open_interest(self, symbol: str) -> UnifiedOpenInterest:
        """获取当前持仓量"""
        pass

    # === 可选重写的方法 ===

    def fetch_sentiment(self, symbol: str) -> Optional[UnifiedSentiment]:
        """获取多空比（若交易所支持）"""
        return None

    def fetch_funding_history(
        self, symbol: str, limit: int = 100,
        start_time: Optional[int] = None
    ) -> List[UnifiedFunding]:
        """获取历史资金费率"""
        return []

    def fetch_open_interest_history(
        self, symbol: str, interval: str = "5m",
        limit: int = 100, start_time: Optional[int] = None
    ) -> List[UnifiedOpenInterest]:
        """获取历史持仓量"""
        return []

    def get_supported_intervals(self) -> List[str]:
        """返回支持的K线周期"""
        return ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

    def is_connected(self) -> bool:
        """检查连接状态"""
        ...
```

#### B. 交易客户端（Trading Client）

需要实现与 `BinanceTradingClient` / `HyperliquidTradingClient` **统一的方法签名**：

```python
class OkxTradingClient:
    def __init__(self, api_key: str, secret_key: str,
                 passphrase: str, environment: str = "testnet"):
        """初始化客户端，配置 API 端点、签名机制"""

    # === 账户相关 ===
    def get_account_state(self, db=None) -> Dict[str, Any]:
        """返回: {available_balance, total_equity, used_margin,
                  margin_usage_percent, maintenance_margin}"""

    def get_balance(self) -> Dict[str, Any]:
        """返回: {total_equity, available_balance, used_margin,
                  unrealized_pnl, margin_usage_percent}"""

    # === 行情相关 ===
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """返回: {symbol, price}"""

    def get_mark_price(self, symbol: str) -> float:
        """获取标记价格"""

    # === 持仓相关 ===
    def get_positions(self, db=None, include_timing: bool = False
                      ) -> List[Dict[str, Any]]:
        """返回统一格式持仓列表:
        [{coin, szi, entry_px, position_value, unrealized_pnl,
          leverage, liquidation_px, margin_used, leverage_type, side, ...}]"""

    # === 订单相关 ===
    def place_order(
        self, symbol: str, side: str, quantity: float,
        order_type: str = "MARKET", price: Optional[float] = None,
        time_in_force: str = "GTC", reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """返回: {order_id, symbol, side, quantity, price, status, ...}"""

    def place_order_with_tpsl(
        self, db, symbol: str, is_buy: bool, size: float,
        price: float, leverage: int = 1,
        time_in_force: str = "GTC", reduce_only: bool = False,
        take_profit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        order_type: str = "MARKET",
        tp_execution: str = "market",
        sl_execution: str = "market",
    ) -> Dict[str, Any]:
        """返回: {status, order_id, tp_order_id, sl_order_id,
                  filled_qty, avg_price, errors}"""

    def place_stop_order(
        self, symbol: str, side: str, quantity: float,
        stop_price: float, order_type: str = "STOP_MARKET",
        reduce_only: bool = True, working_type: str = "MARK_PRICE",
        ...
    ) -> Dict[str, Any]:
        """下止盈止损单"""

    def cancel_order(self, symbol: str, order_id, ...) -> Dict:
        """取消订单"""

    def cancel_all_orders(self, symbol: str) -> Dict:
        """取消全部订单"""

    def close_position(self, symbol: str, cancel_tpsl: bool = True
                       ) -> Optional[Dict]:
        """市价全平仓位"""

    def get_open_orders(self, db=None, symbol=None
                        ) -> List[Dict[str, Any]]:
        """获取挂单（含止盈止损条件单）"""

    # === 统计相关 ===
    def get_trading_stats(self, db=None) -> Dict[str, Any]:
        """返回: {total_trades, wins, losses, win_rate, total_pnl,
                  volume, avg_win, avg_loss, profit_factor, ...}"""

    def get_user_fills(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """返回统一格式成交记录:
        [{oid, coin, side, px, sz, time, closedPnl, fee, ...}]"""

    # === 杠杆相关 ===
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """设置杠杆倍数"""
```

#### C. 数据采集器（Data Collector）

```python
class OkxCollector:
    """单例模式，使用 APScheduler 定时采集"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls): ...          # 单例模式
    def __init__(self): ...        # 初始化 adapter
    def start(self, symbols): ...  # 启动调度器，添加采集任务
    def stop(self): ...            # 停止调度器
    def refresh_symbols(self, new_symbols): ...
    # 内部方法：_add_kline_job, _add_oi_job, _add_funding_job,
    #          _add_orderbook_job, _add_sentiment_job
    #          _collect_klines, _collect_oi, _collect_funding, ...
```

#### D. 符号服务（Symbol Service）

```python
# 类似 binance_symbol_service.py
def fetch_remote_symbols() -> List[Dict[str, str]]:
    """从 OKX API 获取可交易 symbol 列表"""

def refresh_okx_symbols() -> List[Dict[str, str]]:
    """刷新并持久化 symbol 列表"""

def get_selected_symbols() -> List[str]:
    """获取用户选中的自选列表"""

def update_selected_symbols(symbols: List[str]) -> List[str]:
    """更新自选列表"""

def schedule_symbol_refresh_task(interval_seconds: int = 7200):
    """注册定期刷新任务"""
```

#### E. 账户快照服务（Snapshot Service）

```python
class OkxSnapshotService:
    """定时采集账户快照，存入数据库"""
    async def start(self): ...
    async def stop(self): ...
```

### 2.2 必须实现的统一返回格式

所有交易客户端方法必须返回与现有客户端**字段名和数据类型完全一致**的字典，以确保上层调用者（AI Trader、Program Trader、API Routes）无需修改。

核心统一字段规范参见 [binance_trading_client.py](backend/services/binance_trading_client.py) 中每个方法的 docstring（如 `get_positions` 返回 `coin`, `szi`, `entry_px` 等字段）。

---

## 三、新交易所要注册到系统中的全部位置

### 3.1 后端：类型/常量定义

| 文件 | 修改内容 |
|---|---|
| `backend/services/exchanges/__init__.py` | 导出新 Adapter 和 Collector |
| `backend/services/exchanges/symbol_mapper.py` | 添加 `EXCHANGE_QUOTE_CURRENCY["okx"]`、`SPECIAL_MAPPINGS["okx"]`、`REVERSE_MAPPINGS["okx"]` |
| `backend/services/error_registry.py` | 添加 `OK = "okx"` 常量，注册 OKX 特有错误模式（~10条） |

### 3.2 后端：配置

| 文件 | 修改内容 |
|---|---|
| `backend/config/settings.py` | 添加 `OkxBrokerConfig`（如有返佣）、`OKX_DAILY_QUOTA_LIMIT` 等 |
| `backend/.env.example` | 添加 OKX API 相关环境变量 |
| `.env.example`（根目录） | 同上 |

### 3.3 后端：启动初始化

| 文件 | 修改内容 |
|---|---|
| `backend/services/startup.py` | 在 `initialize_services()` 中添加：刷新 OKX symbol 目录、启动 OKX Collector、启动 OKX Snapshot Service；在 `shutdown_services()` 中添加对应的停止逻辑 |

### 3.4 后端：数据库模型

| 文件 | 修改内容 |
|---|---|
| `backend/database/models.py` | **新建 `OkxWallet` 表**（参考 `BinanceWallet`，字段：`account_id`, `environment`, `api_key_encrypted`, `secret_key_encrypted`, `passphrase_encrypted`, `max_leverage`, `default_leverage`, `is_active`）；**新建 `OkxAccountSnapshot` 表** |
| `backend/database/` | 添加迁移脚本 `migrate_add_okx.py` / `init_okx_tables.py` |

### 3.5 后端：API 路由

| 文件 | 修改内容 |
|---|---|
| `backend/api/okx_routes.py`（**新建**） | OKX 钱包绑定、余额/持仓查询、下单、环境切换等 API |
| `backend/api/account_routes.py` | 注册 OKX 路由；在统一账户接口中支持 `exchange="okx"` |
| `backend/main.py` | 注册 `okx_routes` 路由器 |

### 3.6 后端：API 用户配置端点

| 文件 | 修改内容 |
|---|---|
| `backend/api/user_routes.py`（或 `config_routes.py`） | `/api/users/exchange-config` 端点需在验证列表中增加 `"okx"` |
| `backend/database/models.py` | `UserExchangeConfig.selected_exchange` 可选值需包含 `"okx"`（当前默认支持字符串，但前端类型需同步） |

### 3.7 前端：类型定义

| 文件 | 修改内容 |
|---|---|
| `frontend/app/lib/types/exchange.ts` | `ExchangeId` 类型增加 `'okx'`；`EXCHANGE_DISPLAY_NAMES`、`EXCHANGE_STATUS_COLORS` 增加 OKX 条目 |

### 3.8 前端：Context / 状态管理

| 文件 | 修改内容 |
|---|---|
| `frontend/app/contexts/ExchangeContext.tsx` | `exchanges` 数组中添加 OKX 交易所对象（含 `id`, `name`, `selectable`, `logo`, `description`, `features`, `referralLink` 等）；`selectExchange` 白名单数组中添加 `"okx"`（包括 localStorage 恢复和 API 验证） |

### 3.9 前端：UI 组件

| 文件 | 修改内容 |
|---|---|
| `frontend/app/components/exchange/ExchangeIcon.tsx` | `icons` Record 中增加 `okx` 条目（SVG 图标或 `<img>` 引用） |
| `frontend/app/components/exchange/ExchangeModal.tsx` | `dataInfo` 对象增加 `okx` 数据采集方式说明；`exchangeTranslations` 增加 OKX 翻译；过滤条件中增加 `'okx'` |
| `frontend/public/` | 添加 `okx_logo.svg` |

### 3.10 前端：国际化

| 文件 | 修改内容 |
|---|---|
| `frontend/app/locales/en.json` | 添加 OKX 相关翻译键（`exchange.okx.description`, `exchange.okx.feature1-3`, `exchange.okx.button` 等） |
| `frontend/app/locales/zh.json` | 同上，中文翻译 |

### 3.11 前端：交易所专属组件

| 文件 | 修改内容 |
|---|---|
| `frontend/app/components/okx/`（**新建目录**） | 参考 `frontend/app/components/binance/` 和 `frontend/app/components/hyperliquid/`，创建 OKX 专属组件（钱包配置面板、余额卡片、持仓表格、下单表单等） |
| `frontend/app/lib/okxApi.ts`（**新建**） | OKX 专属 API 调用函数 |

---

## 四、OKX 集成需要新增和修改的文件清单（参考 Binance 实现）

### 4.1 新增文件

```
backend/
├── services/
│   ├── exchanges/
│   │   ├── okx_adapter.py          # OKX 适配器 (继承 BaseExchangeAdapter)
│   │   ├── okx_collector.py        # OKX REST 数据采集器 (单例+APScheduler)
│   │   ├── okx_ws_collector.py     # OKX WebSocket 数据采集器
│   │   └── okx_backfill.py         # OKX 历史数据回填
│   ├── okx_trading_client.py       # OKX 交易客户端 (HMAC签名+ REST API)
│   ├── okx_symbol_service.py       # OKX 交易对管理服务
│   ├── okx_snapshot_service.py     # OKX 账户快照服务
│   └── okx_environment.py          # OKX 环境管理 (testnet/mainnet切换)
├── api/
│   └── okx_routes.py              # OKX API 路由
└── database/
    ├── init_okx_tables.py          # OKX 数据库表初始化
    └── migrate_add_okx.py          # OKX 数据库迁移脚本

frontend/
├── app/
│   ├── components/
│   │   └── okx/                    # OKX 专属UI组件目录
│   │       ├── index.ts            # 导出汇总
│   │       ├── OkxWalletPanel.tsx   # 钱包配置面板
│   │       ├── OkxBalanceCard.tsx   # 余额卡片
│   │       ├── OkxPositionsTable.tsx # 持仓表格
│   │       └── OkxOrderForm.tsx     # 下单表单
│   └── lib/
│       └── okxApi.ts               # OKX API 调用封装
└── public/
    └── okx_logo.svg                # OKX Logo
```

### 4.2 修改现有文件

```
backend/
├── services/
│   ├── exchanges/
│   │   ├── __init__.py             # +导出 OkxAdapter, okx_collector
│   │   └── symbol_mapper.py        # +okx 映射配置
│   ├── error_registry.py           # +OK="okx" 常量 + OKX 错误模式
│   ├── startup.py                  # +initialize_services / shutdown_services
│   └── hyper_ai_tools.py           # (如需) AI 工具支持 OKX 数据源
├── config/
│   └── settings.py                 # +OkxBrokerConfig, OKX_DAILY_QUOTA_LIMIT
├── database/
│   └── models.py                   # +OkxWallet, OkxAccountSnapshot 表
├── api/
│   ├── account_routes.py           # +支持 exchange="okx"
│   └── user_routes.py              # +白名单验证 "okx"
├── main.py                         # +注册 okx_routes 路由器
├── .env.example                    # +OKX 环境变量
└── pyproject.toml                  # (如需) +OKX SDK 依赖

frontend/
├── app/
│   ├── lib/
│   │   └── types/
│   │       └── exchange.ts         # +'okx' 到 ExchangeId, 所有映射表
│   ├── contexts/
│   │   └── ExchangeContext.tsx     # +OKX 交易所对象, +白名单
│   └── components/
│       └── exchange/
│           ├── ExchangeIcon.tsx     # +okx SVG/图标
│           └── ExchangeModal.tsx    # +okx dataInfo, +translations
├── app/locales/
│   ├── en.json                     # +okx 翻译键
│   └── zh.json                     # +okx 翻译键
└── public/
    └── auth-config.json            # (如需) OKX 相关认证配置

根目录/
├── .env.example                    # +OKX 环境变量
└── docker-compose.yml              # (如需) OKX 相关环境变量
```

### 4.3 OKX 特殊注意事项

1. **API 认证**：OKX 使用 `api_key + secret_key + passphrase` 三重认证（比 Binance 的 HMAC 多一个 passphrase）。`OkxWallet` 表需额外 `passphrase_encrypted` 字段；`OkxTradingClient` 签名逻辑需包含 passphrase。

2. **WebSocket**：OKX 支持 WebSocket 实时数据（公有频道无需认证），可以完全对标 Binance 的 WS Collector 架构。

3. **交易对格式**：OKX 永续合约格式为 `BTC-USDT-SWAP`，需要在 `SymbolMapper` 中添加映射规则：内部 `"BTC"` ↔ OKX `"BTC-USDT-SWAP"`。

4. **测试网**：OKX 提供 demo 交易环境（`https://www.okx.com/zh-hans/trading-demo`），与 Binance testnet 对应。

5. **Simulated Trading 兼容**：OKX demo 环境使用虚拟资金，适合模拟交易场景。

---

## 五、总结

本项目设计了一套清晰的多交易所适配架构，以 `BaseExchangeAdapter` + 统一 TradingClient 接口 + `ExchangeDataPersistence` 作为核心抽象。参考 Binance 的完整实现路径，OKX 集成预估需要：

- **新增约 14-16 个后端文件 + 约 7-8 个前端文件**
- **修改约 15-18 个现有文件**

关键设计原则是：适配器专注数据获取，交易客户端专注订单执行，采集器专注定时数据收集，三层各司其职。
