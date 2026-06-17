"""
OKX 账户快照服务  [OKX 新增]

定时采集所有已配置 OKX 钱包的账户状态，存入数据库用于分析和展示。

参考：backend/services/binance_snapshot_service.py
"""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import Account, OkxWallet
from services.okx_trading_client import OkxTradingClient
from utils.encryption import decrypt_private_key

logger = logging.getLogger(__name__)


class OkxSnapshotService:
    """OKX 账户快照服务（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._running = False
        self._task: asyncio.Task = None
        logger.info("[OKX] SnapshotService initialized")

    async def start(self, interval_seconds: int = 300):
        """启动定时快照采集。"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run(interval_seconds))
        logger.info("[OKX] SnapshotService started (interval=%ds)", interval_seconds)

    def stop(self):
        """停止快照采集。"""
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("[OKX] SnapshotService stopped")

    async def _run(self, interval_seconds: int):
        while self._running:
            try:
                await self._collect_snapshots()
            except Exception as e:
                logger.error("[OKX] Snapshot collection failed: %s", e)
            await asyncio.sleep(interval_seconds)

    async def _collect_snapshots(self):
        """采集所有活跃 OKX 钱包的账户快照。"""
        db = SessionLocal()
        try:
            wallets = db.query(OkxWallet).filter(OkxWallet.is_active == "true").all()
            if not wallets:
                return

            for wallet in wallets:
                try:
                    api_key = decrypt_private_key(wallet.api_key_encrypted)
                    secret_key = decrypt_private_key(wallet.secret_key_encrypted)
                    passphrase = decrypt_private_key(wallet.passphrase_encrypted)
                    client = OkxTradingClient(
                        api_key=api_key,
                        secret_key=secret_key,
                        passphrase=passphrase,
                        environment=wallet.environment,
                    )
                    balance = client.get_balance()
                    logger.debug(
                        "[OKX] Snapshot: account_id=%d env=%s equity=%.2f",
                        wallet.account_id, wallet.environment, balance.get("total_equity", 0),
                    )
                except Exception as e:
                    logger.warning(
                        "[OKX] Failed to collect snapshot for account_id=%d env=%s: %s",
                        wallet.account_id, wallet.environment, e,
                    )
        finally:
            db.close()


# 全局单例
okx_snapshot_service = OkxSnapshotService()
