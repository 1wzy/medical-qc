import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.data import BasicData, Dataset
from schemas.data import BasicDataCreate, BasicDataUpdate, DatasetCreate, DatasetUpdate


def list_basic_data(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> tuple[List[BasicData], int]:
    """查询基础数据列表"""
    query = db.query(BasicData)
    
    if search:
        search_term = f"%{search}%"
        # ID 是整数，不能使用 like，尝试转换为整数搜索
        try:
            search_id = int(search)
            query = query.filter(
                or_(
                    BasicData.file_name.like(search_term),
                    BasicData.id == search_id
                )
            )
        except ValueError:
            # 如果搜索词不是数字，只搜索文件名
            query = query.filter(BasicData.file_name.like(search_term))
    
    total = query.count()
    items = query.order_by(BasicData.id.desc()).offset(skip).limit(limit).all()
    return items, total


def get_basic_data(db: Session, data_id: int) -> Optional[BasicData]:
    """获取单个基础数据"""
    return db.query(BasicData).filter(BasicData.id == data_id).first()


def create_basic_data(db: Session, payload: BasicDataCreate) -> BasicData:
    """创建基础数据"""
    basic_data = BasicData(
        file_name=payload.file_name,
        file_size=payload.file_size or 0,
        data_content=json.dumps(payload.data_content, ensure_ascii=False),
        data_type="json",
        description=payload.description
    )
    db.add(basic_data)
    db.commit()
    db.refresh(basic_data)
    return basic_data


def update_basic_data(
    db: Session,
    data_id: int,
    payload: BasicDataUpdate
) -> Optional[BasicData]:
    """更新基础数据"""
    basic_data = get_basic_data(db, data_id)
    if not basic_data:
        return None
    
    if payload.file_name is not None:
        basic_data.file_name = payload.file_name
    if payload.description is not None:
        basic_data.description = payload.description
    if payload.data_content is not None:
        basic_data.data_content = json.dumps(payload.data_content, ensure_ascii=False)
        # 更新文件大小（估算）
        basic_data.file_size = len(basic_data.data_content.encode('utf-8'))
    
    db.add(basic_data)
    db.commit()
    db.refresh(basic_data)
    return basic_data


def delete_basic_data(db: Session, data_id: int) -> bool:
    """删除基础数据"""
    basic_data = get_basic_data(db, data_id)
    if not basic_data:
        return False
    
    db.delete(basic_data)
    db.commit()
    return True


def batch_delete_basic_data(db: Session, data_ids: List[int]) -> int:
    """批量删除基础数据"""
    count = db.query(BasicData).filter(BasicData.id.in_(data_ids)).delete(synchronize_session=False)
    db.commit()
    return count


def list_datasets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> tuple[List[Dataset], int]:
    """查询数据集列表"""
    query = db.query(Dataset)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Dataset.name.like(search_term),
                Dataset.description.like(search_term)
            )
        )
    
    total = query.count()
    items = query.order_by(Dataset.id.desc()).offset(skip).limit(limit).all()
    return items, total


def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
    """获取单个数据集"""
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def create_dataset(db: Session, payload: DatasetCreate) -> Dataset:
    """创建数据集"""
    data_count = 0
    data_ids_json = None
    
    if payload.data_source == "select":
        # 从基础数据选择
        if payload.data_ids:
            data_count = len(payload.data_ids)
            data_ids_json = json.dumps(payload.data_ids, ensure_ascii=False)
    else:
        # 直接上传
        if payload.data_content:
            # 如果上传的是单个JSON对象，计数为1
            # 如果是数组，计数为数组长度
            if isinstance(payload.data_content, list):
                data_count = len(payload.data_content)
            else:
                data_count = 1
    
    dataset = Dataset(
        name=payload.name,
        description=payload.description,
        data_source=payload.data_source,
        data_ids=data_ids_json,
        data_count=data_count
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def update_dataset(
    db: Session,
    dataset_id: int,
    payload: DatasetUpdate
) -> Optional[Dataset]:
    """更新数据集"""
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        return None
    
    if payload.name is not None:
        dataset.name = payload.name
    if payload.description is not None:
        dataset.description = payload.description
    if payload.data_ids is not None:
        dataset.data_ids = json.dumps(payload.data_ids, ensure_ascii=False)
        dataset.data_count = len(payload.data_ids)
    
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def delete_dataset(db: Session, dataset_id: int) -> bool:
    """删除数据集"""
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        return False
    
    db.delete(dataset)
    db.commit()
    return True


def get_dataset_with_basic_data(db: Session, dataset_id: int) -> Optional[Dataset]:
    """获取数据集及其关联的基础数据"""
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        return None
    
    # 如果数据集是从基础数据选择的，可以在这里加载关联数据
    # 目前直接返回数据集，前端可以根据data_ids再查询
    return dataset


