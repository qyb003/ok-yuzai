"""
[OKX 新增] OKX 钱包表迁移

创建 okx_wallets 表，结构与 binance_wallets 一致，
额外包含 passphrase_encrypted 字段用于 OKX 签名认证。
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, UniqueConstraint, ForeignKey, text
from database.connection import engine, Base


def upgrade():
    """执行迁移：创建 okx_wallets 表"""
    # 使用原始 SQL 创建表（避免 ORM 模型依赖）
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS okx_wallets (
                id SERIAL PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id),
                environment VARCHAR(20) NOT NULL,
                api_key_encrypted VARCHAR(500) NOT NULL,
                secret_key_encrypted VARCHAR(500) NOT NULL,
                passphrase_encrypted VARCHAR(500) NOT NULL,
                max_leverage INTEGER NOT NULL DEFAULT 20,
                default_leverage INTEGER NOT NULL DEFAULT 1,
                is_active VARCHAR(10) NOT NULL DEFAULT 'true',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_okx_wallets_account_environment UNIQUE (account_id, environment)
            )
        """))
        conn.commit()
        print("[OKX Migration] okx_wallets table created successfully")


def downgrade():
    """回滚迁移：删除 okx_wallets 表"""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS okx_wallets"))
        conn.commit()
        print("[OKX Migration] okx_wallets table dropped")


if __name__ == "__main__":
    upgrade()
