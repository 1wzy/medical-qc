import os
from functools import lru_cache


class Settings:
    """应用配置。默认使用 MySQL，可通过环境变量覆盖。"""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:1234@127.0.0.1:3306/medical_qc?charset=utf8mb4",
    )
    # 可选：LLM 服务等配置
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    # 其他：日志、跨域、鉴权开关等
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()

