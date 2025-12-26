from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from schemas.rule import RuleCreate, RuleOut, RuleUpdate
from services.rule_service import (
    create_rule,
    get_rule,
    list_rules,
    update_rule,
    publish_rule,
)

router = APIRouter()


@router.get("/", response_model=List[RuleOut])
def api_list_rules(db: Session = Depends(get_db)):
    return list_rules(db)


@router.get("/{rule_id}", response_model=RuleOut)
def api_get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = get_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.post("/", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def api_create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    return create_rule(db, payload)


@router.put("/{rule_id}", response_model=RuleOut)
def api_update_rule(rule_id: int, payload: RuleUpdate, db: Session = Depends(get_db)):
    rule = update_rule(db, rule_id, payload)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.post("/{rule_id}/publish", response_model=RuleOut)
def api_publish_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = publish_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule

