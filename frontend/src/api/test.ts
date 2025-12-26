/**
 * 测试接口
 */
import request from './request'
import { HEALTH_CHECK_URL } from './config'
import axios from 'axios'

/**
 * 健康检查
 */
export function healthCheck() {
  return axios.get(HEALTH_CHECK_URL)
}

/**
 * 获取所有规则
 */
export function getRules() {
  return request.get('/rules/')
}

/**
 * 获取单个规则
 */
export function getRule(id: number) {
  return request.get(`/rules/${id}`)
}

