/**
 * 批次管理 API
 */
import request from './request'

export interface Batch {
  id: number
  name: string
  description?: string
  rule_ids: number[]
  dataset_id: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_count: number
  processed_count: number
  passed_count: number
  failed_count: number
  error_message?: string
  created_at: string
  updated_at: string
}

export interface BatchListResponse {
  items: Batch[]
  total: number
  skip: number
  limit: number
}

export interface BatchCreate {
  name: string
  description?: string
  rule_ids?: number[]
  rule_set_id?: number
  dataset_id: number
}

export interface BatchUpdate {
  name?: string
  description?: string
  rule_ids?: number[]
  status?: string
}

/**
 * 获取批次列表
 */
export function getBatchList(params: {
  skip?: number
  limit?: number
  search?: string
}): Promise<BatchListResponse> {
  return request.get('/batch', { params })
}

/**
 * 获取单个批次
 */
export function getBatch(id: number): Promise<Batch> {
  return request.get(`/batch/${id}`)
}

/**
 * 创建批次
 */
export function createBatch(data: BatchCreate): Promise<Batch> {
  return request.post('/batch', data)
}

/**
 * 更新批次
 */
export function updateBatch(id: number, data: BatchUpdate): Promise<Batch> {
  return request.put(`/batch/${id}`, data)
}

/**
 * 删除批次
 */
export function deleteBatch(id: number): Promise<void> {
  return request.delete(`/batch/${id}`)
}

/**
 * 执行批次质控
 */
export function executeBatch(id: number): Promise<Batch> {
  return request.post(`/batch/${id}/execute`)
}

/**
 * 规则执行结果
 */
export interface RuleExecutionResult {
  rule_id: number
  rule_name: string
  passed: boolean
  flag: number
  deduct: number
  explanation?: string
  answer?: any
  error?: string
  duration_ms: number
  created_at: string
}

/**
 * 数据项执行结果
 */
export interface DataItemExecutionResult {
  data_id: number
  file_name: string
  file_size: number
  overall_passed: boolean
  rule_results: RuleExecutionResult[]
  total_deduct: number
}

/**
 * 批次执行详情
 */
export interface BatchExecutionDetail {
  batch_id: number
  batch_name: string
  dataset_id: number
  dataset_name: string
  rule_ids: number[]
  rule_names: string[]
  status: string
  total_count: number
  processed_count: number
  passed_count: number
  failed_count: number
  data_results: DataItemExecutionResult[]
}

/**
 * 获取批次执行详情
 */
export function getBatchDetail(id: number): Promise<BatchExecutionDetail> {
  return request.get(`/batch/${id}/detail`)
}

