"""
OKX K-line 历史数据回填服务  [OKX 新增]

从 OKX REST API 拉取历史 K 线数据并存入数据库。
"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import KlineCollectionTask
from services.exchanges.okx_adapter import OkxAdapter
from services.exchanges.data_persistence import ExchangeDataPersistence

logger = logging.getLogger(__name__)


class OkxBackfillService:
    """OKX 历史数据回填服务"""

    def __init__(self):
        self.adapter = OkxAdapter()
        logger.info("[OKX] BackfillService initialized")

    async def start_backfill(self, task_id: int):
        """执行回填任务"""
        db = SessionLocal()
        try:
            task = db.query(KlineCollectionTask).filter(
                KlineCollectionTask.id == task_id
            ).first()
            if not task:
                logger.error(f"[OKX] Backfill task {task_id} not found")
                return

            task.status = "running"
            db.commit()

            symbols = task.symbol.split(",") if task.symbol else ["BTC"]
            periods = task.period.split(",") if task.period else ["1m", "5m", "15m", "1h"]

            persistence = ExchangeDataPersistence(db)
            total_collected = 0

            for symbol in symbols:
                for period in periods:
                    try:
                        klines = self.adapter.fetch_klines(symbol.strip(), period.strip(), limit=300)
                        if klines:
                            result = persistence.save_klines(klines)
                            total_collected += result.get("inserted", 0) + result.get("updated", 0)
                        await asyncio.sleep(1)  # Rate limit
                    except Exception as e:
                        logger.warning(f"[OKX] Backfill {symbol}/{period} failed: {e}")

            task.status = "completed"
            task.collected_records = total_collected
            task.progress = 100
            db.commit()
            logger.info(f"[OKX] Backfill completed: {total_collected} records")

        except Exception as e:
            logger.error(f"[OKX] Backfill failed: {e}")
            try:
                task = db.query(KlineCollectionTask).filter(
                    KlineCollectionTask.id == task_id
                ).first()
                if task:
                    task.status = "error"
                    task.error_message = str(e)[:500]
                    db.commit()
            except Exception:
                pass
        finally:
            db.close()


# 全局单例
okx_backfill_service = OkxBackfillService()
