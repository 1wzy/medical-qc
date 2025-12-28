import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.batch import Batch, BatchStatus
from models.data import Dataset, BasicData
from models.rule import Rule
from models.rule_set import RuleSet
from schemas.batch import BatchCreate, BatchUpdate
from services.execution_service import execute_rule_by_id


def create_batch(db: Session, payload: BatchCreate) -> Batch:
    """创建批次"""
    # 验证数据集是否存在
    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise ValueError("数据集不存在")
    
    # 确定规则ID列表
    rule_ids = payload.rule_ids
    
    # 如果提供了规则集ID，使用规则集中的规则
    if payload.rule_set_id:
        rule_set = db.query(RuleSet).filter(RuleSet.id == payload.rule_set_id).first()
        if not rule_set:
            raise ValueError("规则集不存在")
        if rule_set.status != "active":
            raise ValueError("规则集未启用")
        rule_ids = rule_set.rule_ids_list()
        if not rule_ids:
            raise ValueError("规则集为空，请先为规则集添加规则")
    
    # 如果没有提供规则ID且没有提供规则集ID，报错
    if not rule_ids:
        raise ValueError("请选择规则或规则集")
    
    # 验证规则是否存在
    rules = db.query(Rule).filter(Rule.id.in_(rule_ids)).all()
    if len(rules) != len(rule_ids):
        raise ValueError("部分规则不存在")
    
    # 获取数据集的数据条数
    if dataset.data_source == 'select':
        data_count = len(dataset.data_ids_list())
    else:
        data_count = dataset.data_count
    
    batch = Batch(
        name=payload.name,
        description=payload.description,
        rule_ids=json.dumps(rule_ids),
        dataset_id=payload.dataset_id,
        status=BatchStatus.pending.value,
        total_count=data_count,
        processed_count=0,
        passed_count=0,
        failed_count=0
    )
    
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def list_batches(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> tuple[List[Batch], int]:
    """获取批次列表"""
    query = db.query(Batch)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Batch.name.like(search_term),
                Batch.id == int(search) if search.isdigit() else None
            )
        )
    
    total = query.count()
    items = query.order_by(Batch.id.desc()).offset(skip).limit(limit).all()
    
    return items, total


def get_batch(db: Session, batch_id: int) -> Optional[Batch]:
    """获取单个批次"""
    return db.query(Batch).filter(Batch.id == batch_id).first()


def update_batch(db: Session, batch_id: int, payload: BatchUpdate) -> Optional[Batch]:
    """更新批次"""
    batch = get_batch(db, batch_id)
    if not batch:
        return None
    
    if payload.name is not None:
        batch.name = payload.name
    if payload.description is not None:
        batch.description = payload.description
    if payload.rule_ids is not None:
        batch.rule_ids = json.dumps(payload.rule_ids)
    if payload.status is not None:
        batch.status = payload.status
    if payload.total_count is not None:
        batch.total_count = payload.total_count
    if payload.processed_count is not None:
        batch.processed_count = payload.processed_count
    if payload.passed_count is not None:
        batch.passed_count = payload.passed_count
    if payload.failed_count is not None:
        batch.failed_count = payload.failed_count
    if payload.error_message is not None:
        batch.error_message = payload.error_message
    
    db.commit()
    db.refresh(batch)
    return batch


def delete_batch(db: Session, batch_id: int) -> bool:
    """删除批次"""
    batch = get_batch(db, batch_id)
    if not batch:
        return False
    
    db.delete(batch)
    db.commit()
    return True


def execute_batch(db: Session, batch_id: int) -> Batch:
    """执行批次质控"""
    batch = get_batch(db, batch_id)
    if not batch:
        raise ValueError("批次不存在")
    
    if batch.status == BatchStatus.processing.value:
        raise ValueError("批次正在处理中")
    
    # 更新状态为处理中
    batch.status = BatchStatus.processing.value
    batch.error_message = None
    db.commit()
    
    try:
        # 获取数据集
        dataset = db.query(Dataset).filter(Dataset.id == batch.dataset_id).first()
        if not dataset:
            raise ValueError("数据集不存在")
        
        # 获取规则ID列表
        rule_ids = batch.rule_ids_list()
        if not rule_ids:
            raise ValueError("批次没有配置规则")
        
        # 获取数据集中的所有基础数据
        if dataset.data_source == 'select':
            data_ids = dataset.data_ids_list()
            if not data_ids:
                raise ValueError("数据集没有关联的基础数据")
            basic_data_list = db.query(BasicData).filter(BasicData.id.in_(data_ids)).all()
        else:
            # 上传类型的数据集暂不支持批次质控
            # 因为上传的数据没有存储为基础数据，无法进行质控
            raise ValueError("上传类型的数据集暂不支持批次质控，请使用从基础数据选择的数据集")
        
        if not basic_data_list:
            raise ValueError("数据集没有数据")
        
        # 初始化统计
        total_count = len(basic_data_list)
        processed_count = 0
        passed_count = 0
        failed_count = 0
        
        # 对每个基础数据执行所有规则
        for basic_data in basic_data_list:
            medical_record = basic_data.data_dict()
            medical_id = f"data_{basic_data.id}"
            
            # 执行所有规则
            all_passed = True
            for rule_id in rule_ids:
                try:
                    result = execute_rule_by_id(db, rule_id, medical_record, medical_id)
                    if result and not result.get('passed', False):
                        all_passed = False
                        break
                except Exception as e:
                    # 规则执行出错，视为失败
                    all_passed = False
                    break
            
            processed_count += 1
            if all_passed:
                passed_count += 1
            else:
                failed_count += 1
            
            # 更新批次进度
            batch.processed_count = processed_count
            batch.passed_count = passed_count
            batch.failed_count = failed_count
            db.commit()
        
        # 更新批次状态为已完成
        batch.status = BatchStatus.completed.value
        batch.total_count = total_count
        db.commit()
        
    except Exception as e:
        # 更新批次状态为失败
        batch.status = BatchStatus.failed.value
        batch.error_message = str(e)
        db.commit()
        raise
    
    return batch


def get_batch_execution_detail(db: Session, batch_id: int):
    """获取批次执行详情（包含每个数据项的执行结果）"""
    batch = get_batch(db, batch_id)
    if not batch:
        raise ValueError("批次不存在")
    
    # 获取数据集
    dataset = db.query(Dataset).filter(Dataset.id == batch.dataset_id).first()
    if not dataset:
        raise ValueError("数据集不存在")
    
    # 获取规则信息
    rule_ids = batch.rule_ids_list()
    rules = db.query(Rule).filter(Rule.id.in_(rule_ids)).all()
    rule_dict = {rule.id: rule for rule in rules}
    
    # 获取数据集中的所有基础数据
    if dataset.data_source == 'select':
        data_ids = dataset.data_ids_list()
        basic_data_list = db.query(BasicData).filter(BasicData.id.in_(data_ids)).all()
    else:
        basic_data_list = []
    
    # 获取每个数据项的执行记录
    from models.rule import RuleExecutionRecord
    from collections import defaultdict
    
    # 按 medical_id 分组执行记录
    # medical_id 格式为 "data_{basic_data.id}"
    execution_records = db.query(RuleExecutionRecord).filter(
        RuleExecutionRecord.medical_id.like(f"data_%")
    ).order_by(RuleExecutionRecord.created_at.desc()).all()
    
    # 按数据ID分组
    data_execution_map = defaultdict(list)
    for record in execution_records:
        # 从 medical_id 中提取 data_id
        if record.medical_id and record.medical_id.startswith("data_"):
            try:
                data_id = int(record.medical_id.replace("data_", ""))
                # 只包含批次中的规则
                if record.rule_id in rule_ids:
                    data_execution_map[data_id].append(record)
            except ValueError:
                continue
    
    # 构建数据项执行结果
    data_results = []
    for basic_data in basic_data_list:
        records = data_execution_map.get(basic_data.id, [])
        
        # 按规则ID组织记录
        rule_results = []
        overall_passed = True
        total_deduct = 0
        
        for rule_id in rule_ids:
            # 查找该规则的最新执行记录
            rule_record = None
            for record in records:
                if record.rule_id == rule_id:
                    rule_record = record
                    break
            
            if rule_record:
                rule = rule_dict.get(rule_id)
                rule_name = rule.name if rule else f"规则{rule_id}"
                
                import json
                answer = None
                if rule_record.answer:
                    try:
                        answer = json.loads(rule_record.answer)
                    except:
                        answer = {"raw": rule_record.answer}
                
                rule_result = {
                    "rule_id": rule_id,
                    "rule_name": rule_name,
                    "passed": rule_record.passed if rule_record.passed is not None else False,
                    "flag": rule_record.flag,
                    "deduct": rule_record.deduct,
                    "explanation": rule_record.explanation,
                    "answer": answer,
                    "error": rule_record.error,
                    "duration_ms": rule_record.duration_ms,
                    "created_at": rule_record.created_at.strftime("%Y-%m-%d %H:%M:%S") if rule_record.created_at else ""
                }
                rule_results.append(rule_result)
                
                if not rule_record.passed:
                    overall_passed = False
                total_deduct += rule_record.deduct or 0
        
        data_result = {
            "data_id": basic_data.id,
            "file_name": basic_data.file_name,
            "file_size": basic_data.file_size,
            "overall_passed": overall_passed,
            "rule_results": rule_results,
            "total_deduct": total_deduct
        }
        data_results.append(data_result)
    
    return {
        "batch_id": batch.id,
        "batch_name": batch.name,
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
        "rule_ids": rule_ids,
        "rule_names": [rule_dict.get(rid).name if rule_dict.get(rid) else f"规则{rid}" for rid in rule_ids],
        "status": batch.status,
        "total_count": batch.total_count,
        "processed_count": batch.processed_count,
        "passed_count": batch.passed_count,
        "failed_count": batch.failed_count,
        "data_results": data_results
    }

