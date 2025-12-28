from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from schemas.batch import (
    BatchCreate,
    BatchUpdate,
    BatchOut,
    BatchListResponse,
    BatchExecuteRequest
)
from services.batch_service import (
    create_batch,
    list_batches,
    get_batch,
    update_batch,
    delete_batch,
    execute_batch
)

router = APIRouter()


@router.get("", response_model=BatchListResponse)
def api_list_batches(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取批次列表"""
    try:
        items, total = list_batches(db, skip=skip, limit=limit, search=search)
        
        items_out = []
        for item in items:
            try:
                # 尝试 Pydantic v2 方式
                if hasattr(BatchOut, 'model_validate'):
                    item_out = BatchOut.model_validate({
                        'id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'rule_ids': item.rule_ids_list(),
                        'dataset_id': item.dataset_id,
                        'status': item.status,
                        'total_count': item.total_count,
                        'processed_count': item.processed_count,
                        'passed_count': item.passed_count,
                        'failed_count': item.failed_count,
                        'error_message': item.error_message,
                        'created_at': item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                        'updated_at': item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                    })
                else:
                    # Pydantic v1 方式
                    item_out = BatchOut(
                        id=item.id,
                        name=item.name,
                        description=item.description,
                        rule_ids=item.rule_ids_list(),
                        dataset_id=item.dataset_id,
                        status=item.status,
                        total_count=item.total_count,
                        processed_count=item.processed_count,
                        passed_count=item.passed_count,
                        failed_count=item.failed_count,
                        error_message=item.error_message,
                        created_at=item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                        updated_at=item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                    )
                items_out.append(item_out)
            except Exception as e:
                print(f"[ERROR] 序列化批次 {item.id} 失败: {e}")
                continue
        
        return BatchListResponse(
            items=items_out,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] 获取批次列表错误: {error_detail}")
        print(f"[ERROR] 错误堆栈:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取批次列表失败: {error_detail}"
        )


@router.get("/{batch_id}", response_model=BatchOut)
def api_get_batch(batch_id: int, db: Session = Depends(get_db)):
    """获取单个批次"""
    batch = get_batch(db, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    return BatchOut(
        id=batch.id,
        name=batch.name,
        description=batch.description,
        rule_ids=batch.rule_ids_list(),
        dataset_id=batch.dataset_id,
        status=batch.status,
        total_count=batch.total_count,
        processed_count=batch.processed_count,
        passed_count=batch.passed_count,
        failed_count=batch.failed_count,
        error_message=batch.error_message,
        created_at=batch.created_at.strftime("%Y-%m-%d %H:%M:%S") if batch.created_at else "",
        updated_at=batch.updated_at.strftime("%Y-%m-%d %H:%M:%S") if batch.updated_at else ""
    )


@router.post("", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
def api_create_batch(payload: BatchCreate, db: Session = Depends(get_db)):
    """创建批次"""
    try:
        batch = create_batch(db, payload)
        return BatchOut(
            id=batch.id,
            name=batch.name,
            description=batch.description,
            rule_ids=batch.rule_ids_list(),
            dataset_id=batch.dataset_id,
            status=batch.status,
            total_count=batch.total_count,
            processed_count=batch.processed_count,
            passed_count=batch.passed_count,
            failed_count=batch.failed_count,
            error_message=batch.error_message,
            created_at=batch.created_at.strftime("%Y-%m-%d %H:%M:%S") if batch.created_at else "",
            updated_at=batch.updated_at.strftime("%Y-%m-%d %H:%M:%S") if batch.updated_at else ""
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{batch_id}", response_model=BatchOut)
def api_update_batch(batch_id: int, payload: BatchUpdate, db: Session = Depends(get_db)):
    """更新批次"""
    batch = update_batch(db, batch_id, payload)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    return BatchOut(
        id=batch.id,
        name=batch.name,
        description=batch.description,
        rule_ids=batch.rule_ids_list(),
        dataset_id=batch.dataset_id,
        status=batch.status,
        total_count=batch.total_count,
        processed_count=batch.processed_count,
        passed_count=batch.passed_count,
        failed_count=batch.failed_count,
        error_message=batch.error_message,
        created_at=batch.created_at.strftime("%Y-%m-%d %H:%M:%S") if batch.created_at else "",
        updated_at=batch.updated_at.strftime("%Y-%m-%d %H:%M:%S") if batch.updated_at else ""
    )


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_batch(batch_id: int, db: Session = Depends(get_db)):
    """删除批次"""
    if not delete_batch(db, batch_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    return None


@router.post("/{batch_id}/execute", response_model=BatchOut)
def api_execute_batch(batch_id: int, db: Session = Depends(get_db)):
    """执行批次质控"""
    try:
        batch = execute_batch(db, batch_id)
        return BatchOut(
            id=batch.id,
            name=batch.name,
            description=batch.description,
            rule_ids=batch.rule_ids_list(),
            dataset_id=batch.dataset_id,
            status=batch.status,
            total_count=batch.total_count,
            processed_count=batch.processed_count,
            passed_count=batch.passed_count,
            failed_count=batch.failed_count,
            error_message=batch.error_message,
            created_at=batch.created_at.strftime("%Y-%m-%d %H:%M:%S") if batch.created_at else "",
            updated_at=batch.updated_at.strftime("%Y-%m-%d %H:%M:%S") if batch.updated_at else ""
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] 执行批次错误: {error_detail}")
        print(f"[ERROR] 错误堆栈:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行批次失败: {error_detail}"
        )


@router.get("/{batch_id}/detail")
def api_get_batch_detail(batch_id: int, db: Session = Depends(get_db)):
    """获取批次执行详情（包含每个数据项的执行结果）"""
    try:
        from services.batch_service import get_batch_execution_detail
        detail = get_batch_execution_detail(db, batch_id)
        return detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] 获取批次详情错误: {error_detail}")
        print(f"[ERROR] 错误堆栈:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取批次详情失败: {error_detail}"
        )

