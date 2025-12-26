from fastapi import APIRouter

from routers import rules, execute, rule_dev

api_router = APIRouter()
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(execute.router, prefix="/qc", tags=["execute"])
api_router.include_router(rule_dev.router, tags=["rule-dev"])

