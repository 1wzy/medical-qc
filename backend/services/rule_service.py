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

    # 如果规则是已发布状态，只允许修改 status 字段（用于下线操作）
    # 不允许修改其他字段（name, module, description, type, deduct, fields_name, config）
    if rule.status == RuleStatus.published.value:
        # 检查是否有非 status 字段的修改
        has_non_status_update = any([
            payload.name is not None,
            payload.module is not None,
            payload.description is not None,
            payload.type is not None,
            payload.deduct is not None,
            payload.fields_name is not None,
            payload.config is not None,
        ])
        
        if has_non_status_update:
            raise ValueError("已发布的规则不能修改，请先下线后再编辑。")
        
        # 只允许修改 status 字段
        if payload.status is not None:
            rule.status = payload.status
    else:
        # 非已发布状态，允许修改所有字段
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

