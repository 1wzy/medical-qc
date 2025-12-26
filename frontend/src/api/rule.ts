/**
 * 规则管理 API
 */
import request from './request'

export interface RuleCreate {
  name: string
  module?: string
  description?: string
  type?: string
  deduct?: number
  fields_name?: string[][]
  config: Record<string, any>
  auto_publish?: boolean
}

export interface RuleUpdate {
  name?: string
  module?: string
  description?: string
  type?: string
  deduct?: number
  fields_name?: string[][]
  config?: Record<string, any>
  status?: string
}

export interface Rule {
  id: number
  name: string
  module?: string
  description?: string
  type: string
  deduct: number
  fields_name: string[][]
  config: Record<string, any>
  status: string
  version: number
  created_at?: string
  updated_at?: string
}

/**
 * 获取规则列表
 */
export function getRules(): Promise<Rule[]> {
  return request.get('/rules/')
}

/**
 * 获取单个规则
 */
export function getRule(id: number): Promise<Rule> {
  return request.get(`/rules/${id}`)
}

/**
 * 创建规则
 */
export function createRule(data: RuleCreate): Promise<Rule> {
  return request.post('/rules/', data)
}

/**
 * 更新规则
 */
export function updateRule(id: number, data: RuleUpdate): Promise<Rule> {
  return request.put(`/rules/${id}`, data)
}

/**
 * 发布规则
 */
export function publishRule(id: number): Promise<Rule> {
  return request.post(`/rules/${id}/publish`)
}

