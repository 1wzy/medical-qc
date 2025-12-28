import json
from typing import List, Optional

from sqlalchemy.orm import Session

from models.rule_set import RuleSet, RuleSetStatus


def list_rule_sets(db: Session) -> List[RuleSet]:
    """获取所有规则集"""
    return db.query(RuleSet).order_by(RuleSet.id.desc()).all()


def get_rule_set(db: Session, rule_set_id: int) -> Optional[RuleSet]:
    """根据ID获取规则集"""
    return db.query(RuleSet).filter(RuleSet.id == rule_set_id).first()


def create_rule_set(db: Session, name: str, description: Optional[str] = None, 
                     rule_ids: Optional[List[int]] = None, status: str = "active") -> RuleSet:
    """创建规则集"""
    rule_set = RuleSet(
        name=name,
        description=description,
        rule_ids=json.dumps(rule_ids or [], ensure_ascii=False),
        status=status
    )
    db.add(rule_set)
    db.commit()
    db.refresh(rule_set)
    return rule_set


def update_rule_set(db: Session, rule_set_id: int, name: Optional[str] = None,
                    description: Optional[str] = None, rule_ids: Optional[List[int]] = None,
                    status: Optional[str] = None) -> Optional[RuleSet]:
    """更新规则集"""
    rule_set = get_rule_set(db, rule_set_id)
    if not rule_set:
        return None
    
    if name is not None:
        rule_set.name = name
    if description is not None:
        rule_set.description = description
    if rule_ids is not None:
        rule_set.rule_ids = json.dumps(rule_ids, ensure_ascii=False)
    if status is not None:
        rule_set.status = status
    
    db.commit()
    db.refresh(rule_set)
    return rule_set


def delete_rule_set(db: Session, rule_set_id: int) -> bool:
    """删除规则集"""
    rule_set = get_rule_set(db, rule_set_id)
    if not rule_set:
        return False
    
    db.delete(rule_set)
    db.commit()
    return True

