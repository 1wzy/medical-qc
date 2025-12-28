from fastapi import APIRouter

from routers import rules, execute, rule_dev, data, batch, rule_set

api_router = APIRouter()
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(execute.router, prefix="/qc", tags=["execute"])
api_router.include_router(rule_dev.router, tags=["rule-dev"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(rule_set.router, prefix="/rule-set", tags=["rule-set"])

