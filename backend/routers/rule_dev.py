"""
规则开发工具接口
用于编写、测试规则，测试通过后再导入到系统
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from ruleengine.core.engine import RuleEngine
from db import get_db
from services.rule_service import create_rule
from schemas.rule import RuleOut

router = APIRouter(prefix="/rule-dev", tags=["rule-dev"])


class TestRuleRequest(BaseModel):
    """测试规则请求"""
    rule_config: Dict[str, Any]  # 完整的规则配置
    medical_record: Dict[str, Any]  # 测试用的病历数据


class TestRuleResponse(BaseModel):
    """测试规则响应"""
    success: bool
    passed: Optional[bool] = None
    flag: int
    explanation: str
    answer: Dict[str, Any]
    error: Optional[str] = None
    duration_ms: int


class ImportRuleRequest(BaseModel):
    """导入规则请求"""
    name: str
    module: Optional[str] = None
    description: Optional[str] = None
    type: str = "unknown"
    deduct: int = 0
    fields_name: list = []
    rule_config: Dict[str, Any]  # 完整的规则配置
    auto_publish: bool = False  # 是否导入后自动发布


@router.post("/test", response_model=TestRuleResponse)
def test_rule(req: TestRuleRequest):
    """
    测试规则（不保存到数据库）
    
    用于在导入规则前测试规则配置是否正确
    """
    try:
        # 创建规则引擎
        engine = RuleEngine(req.rule_config)
        
        # 执行规则
        result = engine.execute(req.medical_record)
        
        return TestRuleResponse(
            success=True,
            passed=result.get("passed"),
            flag=result.get("flag", -1),
            explanation=result.get("explanation", ""),
            answer=result.get("answer", {}),
            duration_ms=result.get("duration_ms", 0)
        )
    except Exception as e:
        return TestRuleResponse(
            success=False,
            flag=-1,
            explanation=f"规则执行失败：{str(e)}",
            answer={},
            error=str(e),
            duration_ms=0
        )


@router.post("/import", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def import_rule(req: ImportRuleRequest, db: Session = Depends(get_db)):
    """
    导入规则到系统（需要先通过测试）
    
    验证规则配置后，创建规则并保存到数据库
    """
    # 验证规则配置
    try:
        # 简单验证：尝试创建引擎
        engine = RuleEngine(req.rule_config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"规则配置无效：{str(e)}"
        )
    
    # 创建规则（使用 RuleCreate schema）
    from schemas.rule import RuleCreate
    
    rule_create = RuleCreate(
        name=req.name,
        module=req.module,
        description=req.description,
        type=req.type,
        deduct=req.deduct,
        fields_name=req.fields_name,
        config=req.rule_config,
        auto_publish=req.auto_publish
    )
    
    # 保存到数据库
    rule = create_rule(db, rule_create)
    return rule

