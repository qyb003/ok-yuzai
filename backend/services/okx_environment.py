"""
OKX 环境管理与客户端工厂

提供：
- 从 OkxWallet 表读取解密凭证并创建 OkxTradingClient
- 全局交易模式读取（与 Hyperliquid 共用 SystemConfig）

使用方式：
    from services.okx_environment import get_okx_client

    client = get_okx_client(db, account_id, override_environment="testnet")
    balance = client.get_account_state(db)
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from database.models import Account, OkxWallet
from services.okx_trading_client import OkxTradingClient
from utils.encryption import decrypt_private_key

logger = logging.getLogger(__name__)


# [OKX] OKX 客户端缓存（可选，用于减少重复创建开销）
_okx_client_cache: dict = {}
_okx_client_cache_lock = __import__('threading').Lock()


def get_global_trading_mode(db: Session) -> Optional[str]:
    """
    获取全局交易模式（testnet / mainnet），与 Hyperliquid 共用 SystemConfig。
    """
    from database.models import SystemConfig

    config = db.query(SystemConfig).filter(
        SystemConfig.key == "trading_mode"
    ).first()
    return config.value if config else None


def get_okx_client(
    db: Session,
    account_id: int,
    override_environment: Optional[str] = None,
) -> OkxTradingClient:
    """
    获取 OKX 交易客户端（工厂函数）。

    从 okx_wallets 表读取加密凭证（api_key / secret_key / passphrase），
    解密后创建 OkxTradingClient 实例。

    Args:
        db: 数据库会话
        account_id: 目标账户 ID
        override_environment: 可选的环境覆盖（"testnet" 或 "mainnet"）
                             如果不指定，使用全局 trading_mode

    Returns:
        已初始化的 OkxTradingClient

    Raises:
        ValueError: 账户不存在或钱包未配置
    """
    # 1. 验证账户存在
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.is_deleted != True,
    ).first()
    if not account:
        raise ValueError(f"[OKX] 账户 {account_id} 不存在")

    # 2. 确定环境
    if override_environment:
        if override_environment not in ("testnet", "mainnet"):
            raise ValueError(
                f"[OKX] 无效的环境: {override_environment!r}，必须是 'testnet' 或 'mainnet'"
            )
        environment = override_environment
    else:
        environment = get_global_trading_mode(db)
        if not environment:
            raise ValueError(
                f"[OKX] 未配置全局交易模式，请先在设置中切换为 testnet 或 mainnet"
            )

    logger.info(
        f"[OKX] 获取客户端: account={account.name} (ID={account_id}), "
        f"environment={environment}"
    )

    # 3. 查询 OKX 钱包凭证
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
    ).first()

    if not wallet:
        raise ValueError(
            f"[OKX] 账户 {account.name} (ID={account_id}) 在 {environment} 环境下"
            f"未配置 OKX 钱包。请在 AI Trader 设置中绑定 OKX API Key。"
        )

    # 检查钱包是否被停用
    if wallet.is_active and str(wallet.is_active).lower() == "false":
        raise ValueError(
            f"[OKX] 账户 {account.name} 的 {environment} 钱包已被停用"
        )

    # 4. 解密凭证
    try:
        api_key = decrypt_private_key(wallet.api_key_encrypted)
        secret_key = decrypt_private_key(wallet.secret_key_encrypted)
        passphrase = decrypt_private_key(wallet.passphrase_encrypted)
    except Exception as e:
        logger.error(f"[OKX] 解密凭证失败: account_id={account_id}: {e}")
        raise ValueError(f"[OKX] 凭证解密失败: {e}")

    # 5. 创建客户端
    client = OkxTradingClient(
        api_key=api_key,
        secret_key=secret_key,
        passphrase=passphrase,
        environment=environment,
    )

    logger.info(
        f"[OKX] 客户端创建成功: account_id={account_id}, environment={environment}"
    )
    return client


def get_okx_leverage_settings(
    db: Session,
    account_id: int,
    environment: str,
) -> dict:
    """
    获取 OKX 账户的杠杆设置。

    Args:
        db: 数据库会话
        account_id: 账户 ID
        environment: 交易环境

    Returns:
        {"max_leverage": int, "default_leverage": int}
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if wallet:
        return {
            "max_leverage": wallet.max_leverage or 20,
            "default_leverage": wallet.default_leverage or 3,
        }

    # 默认值
    return {
        "max_leverage": 20,
        "default_leverage": 3,
    }
