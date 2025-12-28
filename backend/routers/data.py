from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json

from db import get_db
from schemas.data import (
    BasicDataCreate,
    BasicDataOut,
    BasicDataUpdate,
    BasicDataListResponse,
    DatasetCreate,
    DatasetOut,
    DatasetUpdate,
    DatasetListResponse,
    DatasetDetailOut
)
from services.data_service import (
    list_basic_data,
    get_basic_data,
    create_basic_data,
    update_basic_data,
    delete_basic_data,
    batch_delete_basic_data,
    list_datasets,
    get_dataset,
    create_dataset,
    update_dataset,
    delete_dataset,
    get_dataset_with_basic_data
)

router = APIRouter()


# ========== 基础数据管理 API ==========

@router.get("/basic")
def api_list_basic_data(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取基础数据列表"""
    try:
        items, total = list_basic_data(db, skip=skip, limit=limit, search=search)
        
        # 构建列表项（不包含完整JSON内容，直接返回字典）
        items_list = []
        for item in items:
            item_dict = {
                "id": item.id,
                "file_name": item.file_name,
                "file_size": item.file_size,
                "data_content": {},  # 列表视图不返回完整JSON
                "data_type": item.data_type or "json",
                "description": item.description,
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                "updated_at": item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
            }
            items_list.append(item_dict)
        
        # 直接返回字典，FastAPI会自动序列化为JSON
        return {
            "items": items_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] 获取基础数据列表错误: {error_detail}")
        print(f"[ERROR] 错误堆栈:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据列表失败: {error_detail}"
        )


@router.get("/basic/{data_id}", response_model=BasicDataOut)
def api_get_basic_data(data_id: int, db: Session = Depends(get_db)):
    """获取单个基础数据"""
    data = get_basic_data(db, data_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basic data not found"
        )
    return data


@router.post("/basic/upload", response_model=BasicDataOut, status_code=status.HTTP_201_CREATED)
async def api_upload_basic_data(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    """上传JSON文件作为基础数据"""
    try:
        # 验证文件类型
        if not file.filename or not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能上传JSON格式的文件"
            )
        
        # 读取文件内容
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件内容为空"
            )
        
        file_size = len(content)
        
        # 解析JSON
        try:
            data_content = json.loads(content.decode('utf-8'))
        except UnicodeDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件编码错误: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON格式错误: {str(e)}"
            )
        
        # 验证JSON内容
        if not isinstance(data_content, (dict, list)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON内容必须是对象或数组"
            )
        
        # 创建基础数据
        payload = BasicDataCreate(
            file_name=file.filename,
            file_size=file_size,
            data_content=data_content,
            description=description
        )
        
        result = create_basic_data(db, payload)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"上传文件错误: {error_detail}")
        print(f"错误堆栈: {traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {error_detail}"
        )


@router.post("/basic", response_model=BasicDataOut, status_code=status.HTTP_201_CREATED)
def api_create_basic_data(payload: BasicDataCreate, db: Session = Depends(get_db)):
    """创建基础数据（直接提交JSON数据）"""
    return create_basic_data(db, payload)


@router.put("/basic/{data_id}", response_model=BasicDataOut)
def api_update_basic_data(
    data_id: int,
    payload: BasicDataUpdate,
    db: Session = Depends(get_db)
):
    """更新基础数据"""
    data = update_basic_data(db, data_id, payload)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basic data not found"
        )
    return data


@router.delete("/basic/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_basic_data(data_id: int, db: Session = Depends(get_db)):
    """删除基础数据"""
    success = delete_basic_data(db, data_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basic data not found"
        )
    return None


@router.post("/basic/batch-delete", status_code=status.HTTP_200_OK)
def api_batch_delete_basic_data(
    data_ids: List[int],
    db: Session = Depends(get_db)
):
    """批量删除基础数据"""
    count = batch_delete_basic_data(db, data_ids)
    return {"deleted_count": count}


# ========== 数据集管理 API ==========

@router.get("/dataset", response_model=DatasetListResponse)
def api_list_datasets(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取数据集列表"""
    try:
        items, total = list_datasets(db, skip=skip, limit=limit, search=search)
        
        # 使用 Pydantic 模型验证和序列化（兼容 v1 和 v2）
        items_out = []
        for item in items:
            try:
                # 尝试 Pydantic v2 方式
                if hasattr(DatasetOut, 'model_validate'):
                    item_out = DatasetOut.model_validate(item)
                    items_out.append(item_out)
                else:
                    # Pydantic v1 方式
                    item_out = DatasetOut.from_orm(item)
                    items_out.append(item_out)
            except Exception as e:
                print(f"[ERROR] 序列化数据集 {item.id} 失败: {e}")
                # 如果序列化失败，至少返回基本信息
                items_out.append(DatasetOut(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    data_source=item.data_source,
                    data_ids=item.data_ids_list(),
                    data_count=item.data_count,
                    created_at=item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                    updated_at=item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else ""
                ))
        
        return DatasetListResponse(
            items=items_out,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] 获取数据集列表错误: {error_detail}")
        print(f"[ERROR] 错误堆栈:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据集列表失败: {error_detail}"
        )


@router.get("/dataset/{dataset_id}/detail")
def api_get_dataset_detail(dataset_id: int, db: Session = Depends(get_db)):
    """获取数据集详情（包含关联的基础数据）"""
    try:
        dataset = get_dataset_with_basic_data(db, dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # 辅助函数：格式化日期时间
        def format_datetime(dt):
            if not dt:
                return ""
            if isinstance(dt, str):
                return dt
            if hasattr(dt, 'strftime'):
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return str(dt)
        
        # 构建响应数据
        result = {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "data_source": dataset.data_source,
            "data_ids": dataset.data_ids_list(),
            "data_count": dataset.data_count,
            "created_at": format_datetime(dataset.created_at),
            "updated_at": format_datetime(dataset.updated_at),
            "basic_data_list": []
        }
        
        # 如果有关联的基础数据，添加到响应中
        if hasattr(dataset, '_basic_data_list') and dataset._basic_data_list:
            basic_data_list = []
            for basic_data in dataset._basic_data_list:
                try:
                    # 解析 data_content
                    if isinstance(basic_data.data_content, str):
                        data_content = json.loads(basic_data.data_content)
                    else:
                        data_content = basic_data.data_content or {}
                    
                    basic_data_list.append({
                        "id": basic_data.id,
                        "file_name": basic_data.file_name,
                        "file_size": basic_data.file_size,
                        "data_content": data_content,
                        "data_type": basic_data.data_type or "json",
                        "description": basic_data.description,
                        "created_at": format_datetime(basic_data.created_at),
                        "updated_at": format_datetime(basic_data.updated_at)
                    })
                except Exception as e:
                    import traceback
                    print(f"[ERROR] 序列化基础数据 {basic_data.id} 失败: {e}")
                    print(f"[ERROR] 错误堆栈: {traceback.format_exc()}")
                    continue
            
            result["basic_data_list"] = basic_data_list
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] 获取数据集详情错误: {error_detail}")
        print(f"[ERROR] 错误堆栈:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据集详情失败: {error_detail}"
        )


@router.get("/dataset/{dataset_id}", response_model=DatasetOut)
def api_get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """获取单个数据集"""
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return dataset


@router.post("/dataset", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
def api_create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    """创建数据集"""
    return create_dataset(db, payload)


@router.post("/dataset/upload", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
async def api_upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    """上传JSON文件创建数据集"""
    try:
        # 验证文件类型
        if not file.filename or not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能上传JSON格式的文件"
            )
        
        # 验证名称
        if not name or not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据集名称不能为空"
            )
        
        # 读取文件内容
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件内容为空"
            )
        
        # 解析JSON
        try:
            data_content = json.loads(content.decode('utf-8'))
        except UnicodeDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件编码错误: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON格式错误: {str(e)}"
            )
        
        # 验证JSON内容
        if not isinstance(data_content, (dict, list)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON内容必须是对象或数组"
            )
        
        # 创建数据集
        payload = DatasetCreate(
            name=name.strip(),
            description=description.strip() if description else None,
            data_source="upload",
            data_content=data_content
        )
        
        result = create_dataset(db, payload)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"上传数据集文件错误: {error_detail}")
        print(f"错误堆栈: {traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {error_detail}"
        )


@router.put("/dataset/{dataset_id}", response_model=DatasetOut)
def api_update_dataset(
    dataset_id: int,
    payload: DatasetUpdate,
    db: Session = Depends(get_db)
):
    """更新数据集"""
    dataset = update_dataset(db, dataset_id, payload)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return dataset


@router.delete("/dataset/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """删除数据集"""
    success = delete_dataset(db, dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return None

