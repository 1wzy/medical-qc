/**
 * 数据管理 API
 */
import request from './request'
import axios from 'axios'
import { API_BASE_URL } from './config'

export interface BasicData {
  id: number
  file_name: string
  file_size: number
  data_content: Record<string, any>
  data_type: string
  description?: string
  created_at: string
  updated_at: string
}

export interface BasicDataListResponse {
  items: BasicData[]
  total: number
  skip: number
  limit: number
}

export interface BasicDataCreate {
  file_name: string
  file_size?: number
  data_content: Record<string, any>
  description?: string
}

export interface BasicDataUpdate {
  file_name?: string
  description?: string
  data_content?: Record<string, any>
}

export interface Dataset {
  id: number
  name: string
  description?: string
  data_source: string
  data_ids: number[]
  data_count: number
  created_at: string
  updated_at: string
}

export interface DatasetDetail extends Dataset {
  basic_data_list?: BasicData[]
}

export interface DatasetListResponse {
  items: Dataset[]
  total: number
  skip: number
  limit: number
}

export interface DatasetCreate {
  name: string
  description?: string
  data_source: string
  data_ids?: number[]
  data_content?: Record<string, any>
}

export interface DatasetUpdate {
  name?: string
  description?: string
  data_ids?: number[]
  data_content?: Record<string, any>
}

/**
 * 获取基础数据列表
 */
export function getBasicDataList(params: {
  skip?: number
  limit?: number
  search?: string
}): Promise<BasicDataListResponse> {
  return request.get('/data/basic', { params })
}

/**
 * 获取单个基础数据
 */
export function getBasicData(id: number): Promise<BasicData> {
  return request.get(`/data/basic/${id}`)
}

/**
 * 上传JSON文件创建基础数据
 */
export function uploadBasicData(file: File, description?: string): Promise<BasicData> {
  const formData = new FormData()
  formData.append('file', file)
  if (description) {
    formData.append('description', description)
  }
  
  return axios.post(`${API_BASE_URL}/data/basic/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(res => res.data).catch(error => {
    // 提取详细的错误信息
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || '上传失败'
    throw new Error(errorMessage)
  })
}

/**
 * 创建基础数据（直接提交JSON）
 */
export function createBasicData(data: BasicDataCreate): Promise<BasicData> {
  return request.post('/data/basic', data)
}

/**
 * 更新基础数据
 */
export function updateBasicData(id: number, data: BasicDataUpdate): Promise<BasicData> {
  return request.put(`/data/basic/${id}`, data)
}

/**
 * 删除基础数据
 */
export function deleteBasicData(id: number): Promise<void> {
  return request.delete(`/data/basic/${id}`)
}

/**
 * 批量删除基础数据
 */
export function batchDeleteBasicData(dataIds: number[]): Promise<{ deleted_count: number }> {
  return request.post('/data/basic/batch-delete', dataIds)
}

/**
 * 获取数据集列表
 */
export function getDatasetList(params: {
  skip?: number
  limit?: number
  search?: string
}): Promise<DatasetListResponse> {
  return request.get('/data/dataset', { params })
}

/**
 * 获取单个数据集
 */
export function getDataset(id: number): Promise<Dataset> {
  return request.get(`/data/dataset/${id}`)
}

/**
 * 获取数据集详情（包含关联的基础数据）
 */
export function getDatasetDetail(id: number): Promise<DatasetDetail> {
  return request.get(`/data/dataset/${id}/detail`)
}

/**
 * 上传JSON文件创建数据集
 */
export function uploadDataset(file: File, name: string, description?: string): Promise<Dataset> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  if (description) {
    formData.append('description', description)
  }
  
  return axios.post(`${API_BASE_URL}/data/dataset/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(res => res.data).catch(error => {
    // 提取详细的错误信息
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || '上传失败'
    throw new Error(errorMessage)
  })
}

/**
 * 创建数据集
 */
export function createDataset(data: DatasetCreate): Promise<Dataset> {
  return request.post('/data/dataset', data)
}

/**
 * 更新数据集
 */
export function updateDataset(id: number, data: DatasetUpdate): Promise<Dataset> {
  return request.put(`/data/dataset/${id}`, data)
}

/**
 * 删除数据集
 */
export function deleteDataset(id: number): Promise<void> {
  return request.delete(`/data/dataset/${id}`)
}


