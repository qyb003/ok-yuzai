"""
OKX 交易对管理服务  [OKX 新增]

功能：
- 从 OKX API 获取可交易 symbol 列表
- 持久化到 SystemConfig
- 用户自选列表管理
- 定期刷新任务

参考：backend/services/binance_symbol_service.py
"""
from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

import requests
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import SystemConfig

logger = logging.getLogger(__name__)

# [OKX] SystemConfig key 名
OKX_AVAILABLE_SYMBOLS_KEY = "okx_available_symbols"
OKX_SELECTED_SYMBOLS_KEY = "okx_selected_symbols"
MAX_WATCHLIST_SYMBOLS = 10
SYMBOL_REFRESH_TASK_ID = "okx_symbol_refresh"

# [OKX] 默认 symbol
DEFAULT_SYMBOLS: List[Dict[str, str]] = [
    {"symbol": "BTC", "name": "Bitcoin"},
]

OKX_PUBLIC_API = "https://www.okx.com"


def _load_config_value(db: Session, key: str) -> Optional[str]:
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    return config.value if config else None


def _save_config_value(db: Session, key: str, value: str) -> None:
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        config = SystemConfig(key=key, value=value)
        db.add(config)
    else:
        config.value = value
    db.commit()


def _parse_symbol_json(value: Optional[str]) -> List[Dict[str, str]]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            result = []
            for entry in parsed:
                if not isinstance(entry, dict):
                    continue
                symbol = str(entry.get("symbol") or "").upper()
                if not symbol:
                    continue
                result.append({
                    "symbol": symbol,
                    "name": entry.get("name") or symbol,
                    "type": entry.get("type") or "perpetual",
                })
            return result
    except json.JSONDecodeError:
        logger.warning("[OKX] Failed to decode stored symbols")
    return []


def _serialize_symbols(symbols: List[Dict[str, str]]) -> str:
    sanitized = []
    seen = set()
    for entry in symbols:
        symbol = str(entry.get("symbol") or "").upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        sanitized.append({
            "symbol": symbol,
            "name": entry.get("name") or symbol,
            "type": "perpetual",
        })
    return json.dumps(sanitized)


def fetch_remote_symbols() -> List[Dict[str, str]]:
    """
    [OKX] 从 OKX Public API 获取可交易的永续合约 symbol 列表。
    使用 /api/v5/public/instruments?instType=SWAP 端点。
    """
    try:
        resp = requests.get(
            f"{OKX_PUBLIC_API}/api/v5/public/instruments",
            params={"instType": "SWAP", "uly": "USDT"},  # 只取 USDT 本位永续
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        instruments = data.get("data") or []
    except Exception as err:
        logger.warning("[OKX] Failed to fetch instruments: %s", err)
        return []

    results: List[Dict[str, str]] = []
    seen = set()

    for item in instruments:
        inst_id = item.get("instId", "")
        if not inst_id.endswith("-USDT-SWAP"):
            continue
        # 提取基础货币
        base = inst_id.replace("-USDT-SWAP", "")
        if base in seen:
            continue
        seen.add(base)
        results.append({
            "symbol": base,
            "name": base,
            "type": "perpetual",
        })

    logger.info("[OKX] Fetched %d tradable symbols", len(results))
    return results


def refresh_okx_symbols() -> List[Dict[str, str]]:
    """[OKX] 刷新可用 symbol 列表。"""
    remote_symbols = fetch_remote_symbols()
    if not remote_symbols:
        logger.warning("[OKX] No symbols fetched; keeping existing list")

    with SessionLocal() as db:
        if remote_symbols:
            _save_config_value(db, OKX_AVAILABLE_SYMBOLS_KEY, _serialize_symbols(remote_symbols))
            _ensure_watchlist_valid(db, remote_symbols)
        else:
            stored = _parse_symbol_json(_load_config_value(db, OKX_AVAILABLE_SYMBOLS_KEY))
            if not stored:
                _save_config_value(db, OKX_AVAILABLE_SYMBOLS_KEY, _serialize_symbols(DEFAULT_SYMBOLS))
                _ensure_watchlist_valid(db, DEFAULT_SYMBOLS)
    return get_available_symbols()


def _ensure_watchlist_valid(db: Session, available: List[Dict[str, str]]) -> None:
    """确保自选列表只包含有效 symbol。"""
    available_set = {item["symbol"] for item in available}
    raw_value = _load_config_value(db, OKX_SELECTED_SYMBOLS_KEY)

    if not raw_value:
        # 首次初始化：复制 HL 自选列表
        hl_watchlist = _load_config_value(db, "hyperliquid_selected_symbols")
        if hl_watchlist:
            try:
                hl_symbols = json.loads(hl_watchlist)
                if isinstance(hl_symbols, list) and hl_symbols:
                    valid = [s for s in hl_symbols if s in available_set][:MAX_WATCHLIST_SYMBOLS]
                    if valid:
                        _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(valid))
                        logger.info("[OKX] Initialized watchlist from Hyperliquid: %s", valid)
                        return
            except (json.JSONDecodeError, TypeError):
                pass
        # Fallback
        default = [item["symbol"] for item in DEFAULT_SYMBOLS if item["symbol"] in available_set]
        if not default:
            default = [item["symbol"] for item in available[:3]]
        _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(default))
        logger.info("[OKX] Initialized watchlist with defaults: %s", default)
        return

    try:
        symbols = json.loads(raw_value)
        if not isinstance(symbols, list):
            raise ValueError("Not a list")
    except Exception:
        default = [item["symbol"] for item in DEFAULT_SYMBOLS if item["symbol"] in available_set]
        _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(default))
        return

    filtered = [s for s in symbols if s in available_set]
    if len(filtered) != len(symbols):
        _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(filtered[:MAX_WATCHLIST_SYMBOLS]))


def get_available_symbols() -> List[Dict[str, str]]:
    """[OKX] 返回缓存的可用 symbol 列表。"""
    with SessionLocal() as db:
        raw_value = _load_config_value(db, OKX_AVAILABLE_SYMBOLS_KEY)
        symbols = _parse_symbol_json(raw_value)
        return symbols if symbols else DEFAULT_SYMBOLS.copy()


def get_selected_symbols() -> List[str]:
    """[OKX] 返回当前选中的 OKX 自选列表。"""
    with SessionLocal() as db:
        raw_value = _load_config_value(db, OKX_SELECTED_SYMBOLS_KEY)
        if not raw_value:
            available = get_available_symbols()
            _ensure_watchlist_valid(db, available)
            raw_value = _load_config_value(db, OKX_SELECTED_SYMBOLS_KEY)
            if not raw_value:
                default = [item["symbol"] for item in DEFAULT_SYMBOLS]
                _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(default))
                return default
        try:
            symbols = json.loads(raw_value)
            if isinstance(symbols, list):
                return symbols
        except json.JSONDecodeError:
            logger.warning("[OKX] Failed to parse watchlist")
        default = [item["symbol"] for item in DEFAULT_SYMBOLS]
        _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(default))
        return default


def update_selected_symbols(symbols: List[str]) -> List[str]:
    """[OKX] 持久化新的自选列表。"""
    available = get_available_symbols()
    available_set = {item["symbol"] for item in available}
    unique = []
    seen = set()
    for sym in symbols:
        upper = str(sym).upper()
        if upper in seen or upper not in available_set:
            continue
        seen.add(upper)
        unique.append(upper)
    if len(unique) > MAX_WATCHLIST_SYMBOLS:
        unique = unique[:MAX_WATCHLIST_SYMBOLS]
    with SessionLocal() as db:
        _save_config_value(db, OKX_SELECTED_SYMBOLS_KEY, json.dumps(unique))
    logger.info("[OKX] Watchlist updated: %s", ", ".join(unique) or "none")
    return unique


def schedule_symbol_refresh_task(interval_seconds: int = 7200) -> None:
    """[OKX] 注册定期 symbol 刷新任务。"""
    from services.scheduler import task_scheduler

    def _task():
        try:
            refreshed = refresh_okx_symbols()
            logger.debug("[OKX] Symbol refresh: %d symbols available", len(refreshed))
        except Exception as err:
            logger.warning("[OKX] Symbol refresh failed: %s", err)

    task_scheduler.remove_task(SYMBOL_REFRESH_TASK_ID)
    task_scheduler.add_interval_task(
        task_func=_task,
        interval_seconds=interval_seconds,
        task_id=SYMBOL_REFRESH_TASK_ID,
    )
    logger.info("[OKX] Symbol refresh scheduled (interval: %ds)", interval_seconds)
