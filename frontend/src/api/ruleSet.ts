/**
 * 规则集管理 API
 */
import request from './request'

export interface RuleSetCreate {
  name: string
  description?: string
  rule_ids?: number[]
  status?: string
}

export interface RuleSetUpdate {
  name?: string
  description?: string
  rule_ids?: number[]
  status?: string
}

export interface RuleSet {
  id: number
  name: string
  description?: string
  rule_ids: number[]
  status: string
  rule_count: number
  created_at: string
  updated_at: string
}

/**
 * 获取规则集列表
 */
export function getRuleSets(): Promise<RuleSet[]> {
  return request.get('/rule-set/')
}

/**
 * 获取单个规则集
 */
export function getRuleSet(id: number): Promise<RuleSet> {
  return request.get(`/rule-set/${id}`)
}

/**
 * 创建规则集
 */
export function createRuleSet(data: RuleSetCreate): Promise<RuleSet> {
  return request.post('/rule-set/', data)
}

/**
 * 更新规则集
 */
export function updateRuleSet(id: number, data: RuleSetUpdate): Promise<RuleSet> {
  return request.put(`/rule-set/${id}`, data)
}

/**
 * 删除规则集
 */
export function deleteRuleSet(id: number): Promise<void> {
  return request.delete(`/rule-set/${id}`)
}

