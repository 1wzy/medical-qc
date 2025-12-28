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
try:
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")
except Exception as e:
    print(f"⚠ 数据库表创建警告: {e}")
    # 不阻止启动，继续运行

settings = get_settings()

app = FastAPI(title="Medical QC System", version="0.1.0")

# CORS 配置 - 必须在所有路由之前添加
# 开发阶段：允许所有来源（使用 "*" 时必须设置 allow_credentials=False）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=False,  # 使用 "*" 时必须设为 False
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 全局异常处理器，确保即使出错也返回 CORS 头
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器，确保所有错误都包含 CORS 头"""
    from fastapi.responses import JSONResponse
    import traceback
    
    error_detail = str(exc)
    traceback_str = traceback.format_exc()
    print(f"[GLOBAL ERROR] {error_detail}")
    print(f"[GLOBAL ERROR] 堆栈:\n{traceback_str}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {error_detail}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "*",
        }
    )


if __name__ == "__main__":
    # 暂时禁用 reload 以避免进程累积问题
    # 如果需要热重载，可以改为 reload=True，但要注意进程管理
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

