import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from schemas.rule import ExecuteRequest, ExecuteResponse
from services.execution_service import execute_rule_by_id

router = APIRouter()


@router.post("/execute", response_model=ExecuteResponse)
def api_execute(req: ExecuteRequest, db: Session = Depends(get_db)):
    start = time.time()
    result = execute_rule_by_id(db, req.rule_id, req.medical_record, req.medical_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    result["duration_ms"] = int((time.time() - start) * 1000)
    return result

