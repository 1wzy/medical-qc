import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.rule import Rule, RuleExecutionRecord
from services.rule_service import get_rule
from schemas.rule import ExecuteResponse
from ruleengine.core.engine import RuleEngine  # 使用新的规则引擎


def execute_rule_by_id(
    db: Session,
    rule_id: int,
    medical_record: Dict[str, Any],
    medical_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    rule: Rule = get_rule(db, rule_id)
    if not rule or rule.status != "published":
        return None

    rule_config = rule.config_dict()
    engine = RuleEngine(rule_config)

    result = engine.execute(medical_record)

    record = RuleExecutionRecord(
        rule_id=rule.id,
        rule_version=rule.version,
        medical_id=medical_id,
        passed=result.get("passed"),
        flag=result.get("flag", 0),
        deduct=result.get("deduct", 0),
        explanation=result.get("explanation"),
        answer=json.dumps(result.get("answer"), ensure_ascii=False) if result.get("answer") else None,
        error=result.get("answer", {}).get("error") if isinstance(result.get("answer"), dict) else None,
    )
    db.add(record)
    db.commit()

    return ExecuteResponse(
        rule_id=rule.id,  # 使用数据库中的整数ID，而不是配置中的字符串ID
        rule_name=result.get("rule_name"),
        description=result.get("description"),
        module=result.get("module"),
        passed=result.get("passed"),
        flag=result.get("flag"),
        deduct=result.get("deduct"),
        answer=result.get("answer"),
        explanation=result.get("explanation"),
        type=result.get("type"),
        fields_name=result.get("fields_name") or [],
    ).dict()

