"""
OKX 永续合约管理 API 路由

提供端点：
- 钱包设置与 API 密钥绑定（API Key + Secret Key + Passphrase）
- 余额和持仓查询
- 手动下单（含止盈止损）
- 连接测试
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database.connection import get_db
from database.models import Account, OkxWallet, User, UserSubscription
from utils.encryption import encrypt_private_key, decrypt_private_key
from services.okx_trading_client import OkxTradingClient
from services.hyperliquid_environment import get_global_trading_mode

logger = logging.getLogger(__name__)

# [OKX] 创建路由
router = APIRouter(prefix="/api/okx", tags=["okx"])

# [OKX] 客户端缓存
_client_cache: dict = {}


def _get_client(wallet: OkxWallet) -> OkxTradingClient:
    """获取或创建 OKX 交易客户端（带缓存）"""
    cache_key = f"{wallet.account_id}_{wallet.environment}"
    if cache_key not in _client_cache:
        api_key = decrypt_private_key(wallet.api_key_encrypted)
        secret_key = decrypt_private_key(wallet.secret_key_encrypted)
        passphrase = decrypt_private_key(wallet.passphrase_encrypted)
        _client_cache[cache_key] = OkxTradingClient(
            api_key=api_key,
            secret_key=secret_key,
            passphrase=passphrase,
            environment=wallet.environment,
        )
    return _client_cache[cache_key]


def _clear_client_cache(account_id: int = None, environment: str = None):
    """清除客户端缓存"""
    if account_id is not None and environment:
        cache_key = f"{account_id}_{environment}"
        _client_cache.pop(cache_key, None)
    else:
        _client_cache.clear()


# ============================================================================
# 请求/响应模型
# ============================================================================


class OkxSetupRequest(BaseModel):
    """[OKX] OKX 钱包设置请求 — 包含 API Key、Secret Key、Passphrase"""
    environment: str = Field(..., pattern="^(testnet|mainnet)$")
    api_key: str = Field(..., min_length=10, alias="apiKey")
    secret_key: str = Field(..., min_length=10, alias="secretKey")
    passphrase: str = Field(..., min_length=4, alias="passphrase")  # [OKX] OKX 特有字段
    max_leverage: int = Field(20, ge=1, le=125, alias="maxLeverage")
    default_leverage: int = Field(1, ge=1, le=125, alias="defaultLeverage")

    class Config:
        populate_by_name = True


class ManualOrderRequest(BaseModel):
    """手动下单请求"""
    symbol: str = Field(..., description="内部符号（如 'BTC'）")
    side: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: float = Field(..., gt=0)
    order_type: str = Field("MARKET", pattern="^(MARKET|LIMIT)$", alias="orderType")
    price: Optional[float] = Field(None, gt=0)
    leverage: int = Field(1, ge=1, le=125)
    reduce_only: bool = Field(False, alias="reduceOnly")
    take_profit_price: Optional[float] = Field(None, gt=0, alias="takeProfitPrice")
    stop_loss_price: Optional[float] = Field(None, gt=0, alias="stopLossPrice")

    class Config:
        populate_by_name = True


# ============================================================================
# API 端点
# ============================================================================


@router.post("/accounts/{account_id}/setup")
def setup_wallet(
    account_id: int,
    request: OkxSetupRequest,
    db: Session = Depends(get_db),
):
    """
    [OKX] 设置 OKX 钱包。

    加密并存储 API Key、Secret Key、Passphrase。
    设置前先测试连接是否有效。
    """
    # 验证账户存在
    account = db.query(Account).filter(
        Account.id == account_id, Account.is_deleted != True
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # [OKX] 测试凭证有效性：使用临时客户端获取余额
    try:
        test_client = OkxTradingClient(
            api_key=request.api_key,
            secret_key=request.secret_key,
            passphrase=request.passphrase,
            environment=request.environment,
        )
        balance = test_client.get_balance()
    except Exception as e:
        logger.warning(f"[OKX] 凭证验证失败: account_id={account_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid credentials: {e}")

    # [OKX] 加密存储凭证（三个字段）
    api_key_encrypted = encrypt_private_key(request.api_key)
    secret_key_encrypted = encrypt_private_key(request.secret_key)
    passphrase_encrypted = encrypt_private_key(request.passphrase)

    # 检查是否已存在同环境钱包
    existing = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == request.environment,
    ).first()

    if existing:
        # 更新已有钱包
        existing.api_key_encrypted = api_key_encrypted
        existing.secret_key_encrypted = secret_key_encrypted
        existing.passphrase_encrypted = passphrase_encrypted  # [OKX]
        existing.max_leverage = request.max_leverage
        existing.default_leverage = request.default_leverage
        existing.is_active = "true"
        _clear_client_cache(account_id, request.environment)
    else:
        # 新建钱包
        wallet = OkxWallet(
            account_id=account_id,
            environment=request.environment,
            api_key_encrypted=api_key_encrypted,
            secret_key_encrypted=secret_key_encrypted,
            passphrase_encrypted=passphrase_encrypted,  # [OKX]
            max_leverage=request.max_leverage,
            default_leverage=request.default_leverage,
            is_active="true",
        )
        db.add(wallet)

    db.commit()

    logger.info(
        f"[OKX] 钱包配置成功: account_id={account_id}, "
        f"environment={request.environment}"
    )

    return {
        "success": True,
        "message": f"OKX {request.environment} wallet configured",
        "environment": request.environment,
        "balance": balance,
    }


@router.get("/accounts/{account_id}/config")
def get_config(account_id: int, db: Session = Depends(get_db)):
    """
    [OKX] 获取 OKX 钱包配置状态。

    返回各环境（testnet / mainnet）的配置情况和掩码后的 API Key。
    """
    wallets = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id
    ).all()

    # 掩码 API Key
    def mask_api_key(wallet: OkxWallet) -> str:
        try:
            api_key = decrypt_private_key(wallet.api_key_encrypted)
            if len(api_key) > 8:
                return f"{api_key[:4]}****{api_key[-4:]}"
            return "****"
        except Exception:
            return "****"

    testnet_wallet = next(
        (w for w in wallets if w.environment == "testnet" and w.is_active == "true"),
        None,
    )
    mainnet_wallet = next(
        (w for w in wallets if w.environment == "mainnet" and w.is_active == "true"),
        None,
    )

    testnet_info = None
    if testnet_wallet:
        testnet_info = {
            "configured": True,
            "api_key_masked": mask_api_key(testnet_wallet),
            "max_leverage": testnet_wallet.max_leverage,
            "default_leverage": testnet_wallet.default_leverage,
        }

    mainnet_info = None
    if mainnet_wallet:
        mainnet_info = {
            "configured": True,
            "api_key_masked": mask_api_key(mainnet_wallet),
            "max_leverage": mainnet_wallet.max_leverage,
            "default_leverage": mainnet_wallet.default_leverage,
        }

    return {
        "account_id": account_id,
        "testnet_configured": testnet_wallet is not None,
        "mainnet_configured": mainnet_wallet is not None,
        "testnet": testnet_info,
        "mainnet": mainnet_info,
    }


@router.delete("/accounts/{account_id}/wallet")
def delete_wallet(
    account_id: int,
    environment: str = "testnet",
    db: Session = Depends(get_db),
):
    """
    [OKX] 删除（停用）指定环境的 OKX 钱包。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
    ).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.is_active = "false"
    db.commit()
    _clear_client_cache(account_id, environment)

    logger.info(
        f"[OKX] 钱包已停用: account_id={account_id}, environment={environment}"
    )
    return {"success": True, "message": f"OKX {environment} wallet deactivated"}


@router.get("/accounts/{account_id}/balance")
def get_balance(
    account_id: int,
    environment: str = "testnet",
    db: Session = Depends(get_db),
):
    """
    [OKX] 获取账户余额。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"No active OKX wallet for {environment}",
        )

    try:
        client = _get_client(wallet)
        balance = client.get_balance()
        return {"success": True, "balance": balance}
    except Exception as e:
        logger.error(f"[OKX] 获取余额失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_id}/positions")
def get_positions(
    account_id: int,
    environment: str = "testnet",
    db: Session = Depends(get_db),
):
    """
    [OKX] 获取当前持仓。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"No active OKX wallet for {environment}",
        )

    try:
        client = _get_client(wallet)
        positions = client.get_positions()
        return {"success": True, "positions": positions}
    except Exception as e:
        logger.error(f"[OKX] 获取持仓失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/{account_id}/order")
def place_order(
    account_id: int,
    request: ManualOrderRequest,
    environment: str = "testnet",
    db: Session = Depends(get_db),
):
    """
    [OKX] 手动下单（含可选的止盈止损）。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"No active OKX wallet for {environment}",
        )

    try:
        client = _get_client(wallet)

        # 使用 place_order_with_tpsl 统一接口
        is_buy = request.side.upper() == "BUY"
        result = client.place_order_with_tpsl(
            db=db,
            symbol=request.symbol,
            is_buy=is_buy,
            size=request.quantity,
            price=request.price or 0,
            leverage=request.leverage,
            reduce_only=request.reduce_only,
            take_profit_price=request.take_profit_price,
            stop_loss_price=request.stop_loss_price,
            order_type=request.order_type,
        )

        return {"success": True, "order": result}
    except Exception as e:
        logger.error(f"[OKX] 下单失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/{account_id}/close-position")
def close_position(
    account_id: int,
    symbol: str,
    environment: str = "testnet",
    db: Session = Depends(get_db),
):
    """
    [OKX] 市价全平指定交易对持仓。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"No active OKX wallet for {environment}",
        )

    try:
        client = _get_client(wallet)
        result = client.close_position(symbol, cancel_tpsl=True)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"[OKX] 平仓失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_id}/open-orders")
def get_open_orders(
    account_id: int,
    environment: str = "testnet",
    symbol: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    [OKX] 获取挂单列表（含未触发的止盈止损单）。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"No active OKX wallet for {environment}",
        )

    try:
        client = _get_client(wallet)
        orders = client.get_open_orders(symbol=symbol)
        return {"success": True, "orders": orders}
    except Exception as e:
        logger.error(f"[OKX] 获取挂单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/accounts/{account_id}/cancel-all")
def cancel_all_orders(
    account_id: int,
    symbol: str,
    environment: str = "testnet",
    db: Session = Depends(get_db),
):
    """
    [OKX] 撤销指定交易对的所有挂单。
    """
    wallet = db.query(OkxWallet).filter(
        OkxWallet.account_id == account_id,
        OkxWallet.environment == environment,
        OkxWallet.is_active == "true",
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"No active OKX wallet for {environment}",
        )

    try:
        client = _get_client(wallet)
        result = client.cancel_all_orders(symbol)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"[OKX] 撤销订单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# [OKX 新增] Symbol 自选列表端点
# ============================================================================

@router.get("/symbols/watchlist")
def get_okx_watchlist():
    """[OKX] 获取 OKX 自选 symbol 列表。"""
    try:
        from services.okx_symbol_service import get_selected_symbols
        symbols = get_selected_symbols()
        return {"symbols": symbols, "count": len(symbols)}
    except Exception as e:
        logger.error(f"[OKX] 获取自选列表失败: {e}")
        # 返回默认列表
        return {"symbols": ["BTC", "ETH", "SOL"], "count": 3}


@router.put("/symbols/watchlist")
async def update_okx_watchlist(payload: dict):
    """[OKX] 更新 OKX 自选 symbol 列表。"""
    try:
        from services.okx_symbol_service import update_selected_symbols
        symbols = payload.get("symbols", [])
        updated = update_selected_symbols(symbols)
        return {"symbols": updated, "count": len(updated), "success": True}
    except Exception as e:
        logger.error(f"[OKX] 更新自选列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols/available")
def get_okx_available_symbols():
    """[OKX] 获取 OKX 所有可交易 symbol。"""
    try:
        from services.okx_symbol_service import get_available_symbols
        symbols_list = get_available_symbols()
        return {"symbols": symbols_list, "count": len(symbols_list)}
    except Exception as e:
        logger.error(f"[OKX] 获取可用symbol失败: {e}")
        # 返回固定主流列表
        default_symbols = [
            {"symbol": "BTC", "name": "Bitcoin"},
            {"symbol": "ETH", "name": "Ethereum"},
            {"symbol": "SOL", "name": "Solana"},
            {"symbol": "DOGE", "name": "Dogecoin"},
            {"symbol": "XRP", "name": "Ripple"},
            {"symbol": "ADA", "name": "Cardano"},
            {"symbol": "AVAX", "name": "Avalanche"},
            {"symbol": "LINK", "name": "Chainlink"},
            {"symbol": "DOT", "name": "Polkadot"},
            {"symbol": "LTC", "name": "Litecoin"},
            {"symbol": "BCH", "name": "Bitcoin Cash"},
            {"symbol": "SUI", "name": "Sui"},
            {"symbol": "TRX", "name": "TRON"},
            {"symbol": "APT", "name": "Aptos"},
            {"symbol": "ARB", "name": "Arbitrum"},
            {"symbol": "OP", "name": "Optimism"},
            {"symbol": "NEAR", "name": "NEAR Protocol"},
            {"symbol": "ATOM", "name": "Cosmos"},
            {"symbol": "FIL", "name": "Filecoin"},
            {"symbol": "UNI", "name": "Uniswap"},
        ]
        return {"symbols": default_symbols, "count": len(default_symbols)}


# ============================================================================

# [OKX 新增] 公开行情端点（无需 API Key）
@router.get("/ticker/{symbol}")
def get_okx_ticker(symbol: str):
    """Get OKX ticker price for a symbol (public API, no auth needed)."""
    import requests
    from services.exchanges.symbol_mapper import SymbolMapper
    try:
        inst_id = SymbolMapper.to_exchange(symbol, "okx")
        resp = requests.get(
            "https://www.okx.com/api/v5/market/ticker",
            params={"instId": inst_id},
            timeout=5,
        )
        data = resp.json()
        ticker = data.get("data", [{}])[0] if data.get("data") else {}
        price = float(ticker.get("last", 0) or 0)
        return {"symbol": symbol, "price": price, "instId": inst_id, "success": True}
    except Exception as e:
        return {"symbol": symbol, "price": 0, "error": str(e), "success": False}

# [OKX 新增] 钱包列表端点
# ============================================================================

@router.get("/wallets/all")
def get_all_okx_wallets(db: Session = Depends(get_db)):
    """[OKX] 获取所有活跃的 OKX 钱包列表。"""
    try:
        from database.models import Account
        wallets = db.query(OkxWallet).filter(OkxWallet.is_active == "true").all()
        result = []
        for w in wallets:
            account = db.query(Account).filter(Account.id == w.account_id).first()
            result.append({
                "id": w.id,
                "account_id": w.account_id,
                "account_name": account.name if account else f"Account #{w.account_id}",
                "environment": w.environment,
                "is_active": w.is_active == "true",
            })
        return {"wallets": result, "count": len(result)}
    except Exception as e:
        logger.error(f"[OKX] 获取钱包列表失败: {e}")
        return {"wallets": [], "count": 0}
