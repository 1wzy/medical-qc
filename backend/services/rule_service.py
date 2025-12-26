import json
from typing import List, Optional

from sqlalchemy.orm import Session

from models.rule import Rule, RuleStatus
from schemas.rule import RuleCreate, RuleUpdate


def list_rules(db: Session) -> List[Rule]:
    return db.query(Rule).order_by(Rule.id.desc()).all()


def get_rule(db: Session, rule_id: int) -> Optional[Rule]:
    return db.query(Rule).filter(Rule.id == rule_id).first()


def create_rule(db: Session, payload: RuleCreate) -> Rule:
    # 如果设置了自动发布，则创建为已发布状态
    status = RuleStatus.published.value if payload.auto_publish else RuleStatus.draft.value
    
    rule = Rule(
        name=payload.name,
        module=payload.module,
        description=payload.description,
        type=payload.type,
        deduct=payload.deduct,
        fields_name=json.dumps(payload.fields_name, ensure_ascii=False),
        config=json.dumps(payload.config, ensure_ascii=False),
        status=status,
        version=1,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: int, payload: RuleUpdate) -> Optional[Rule]:
    rule = get_rule(db, rule_id)
    if not rule:
        return None

    for field in ["name", "module", "description", "type", "deduct", "status"]:
        val = getattr(payload, field, None)
        if val is not None:
            setattr(rule, field, val)

    if payload.fields_name is not None:
        rule.fields_name = json.dumps(payload.fields_name, ensure_ascii=False)

    if payload.config is not None:
        rule.config = json.dumps(payload.config, ensure_ascii=False)
        rule.version += 1  # 配置更新则版本自增

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def publish_rule(db: Session, rule_id: int) -> Optional[Rule]:
    rule = get_rule(db, rule_id)
    if not rule:
        return None
    rule.status = RuleStatus.published.value
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

