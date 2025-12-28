from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from schemas.rule_set import RuleSetCreate, RuleSetOut, RuleSetUpdate
from services.rule_set_service import (
    create_rule_set,
    get_rule_set,
    list_rule_sets,
    update_rule_set,
    delete_rule_set,
)

router = APIRouter()


def format_rule_set_out(rule_set) -> RuleSetOut:
    """格式化规则集输出，包含规则数量"""
    rule_ids = rule_set.rule_ids_list()
    return RuleSetOut(
        id=rule_set.id,
        name=rule_set.name,
        description=rule_set.description,
        rule_ids=rule_ids,
        status=rule_set.status,
        rule_count=len(rule_ids),
        created_at=rule_set.created_at.isoformat() if rule_set.created_at else "",
        updated_at=rule_set.updated_at.isoformat() if rule_set.updated_at else "",
    )


@router.get("/", response_model=List[RuleSetOut])
def api_list_rule_sets(db: Session = Depends(get_db)):
    """获取所有规则集"""
    rule_sets = list_rule_sets(db)
    return [format_rule_set_out(rs) for rs in rule_sets]


@router.get("/{rule_set_id}", response_model=RuleSetOut)
def api_get_rule_set(rule_set_id: int, db: Session = Depends(get_db)):
    """获取单个规则集"""
    rule_set = get_rule_set(db, rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule set not found")
    return format_rule_set_out(rule_set)


@router.post("/", response_model=RuleSetOut, status_code=status.HTTP_201_CREATED)
def api_create_rule_set(payload: RuleSetCreate, db: Session = Depends(get_db)):
    """创建规则集"""
    rule_set = create_rule_set(
        db,
        name=payload.name,
        description=payload.description,
        rule_ids=payload.rule_ids,
        status=payload.status
    )
    return format_rule_set_out(rule_set)


@router.put("/{rule_set_id}", response_model=RuleSetOut)
def api_update_rule_set(rule_set_id: int, payload: RuleSetUpdate, db: Session = Depends(get_db)):
    """更新规则集"""
    rule_set = update_rule_set(
        db,
        rule_set_id=rule_set_id,
        name=payload.name,
        description=payload.description,
        rule_ids=payload.rule_ids,
        status=payload.status
    )
    if not rule_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule set not found")
    return format_rule_set_out(rule_set)


@router.delete("/{rule_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_rule_set(rule_set_id: int, db: Session = Depends(get_db)):
    """删除规则集"""
    success = delete_rule_set(db, rule_set_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule set not found")
    return None

