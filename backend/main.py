import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import Base, engine
from routers import api_router
import models  # 确保模型被导入，从而在 create_all 时创建表

# 导入规则引擎函数库，确保装饰器执行（函数注册）
from ruleengine import functions  # 新架构的函数库

# 创建表（生产环境建议用 Alembic 管理迁移）
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(title="Medical QC System", version="0.1.0")

if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

