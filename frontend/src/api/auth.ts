/**
 * 认证相关 API
 */
import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    real_name?: string
    email?: string
    role: string
    status: string
    created_at: string
    last_login_at?: string
  }
}

export interface UserInfo {
  id: number
  username: string
  real_name?: string
  email?: string
  role: string
  status: string
  created_at: string
  last_login_at?: string
}

/**
 * 用户登录
 */
export function login(params: LoginParams): Promise<LoginResponse> {
  return request.post('/auth/login', params)
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<UserInfo> {
  return request.get('/auth/me')
}

/**
 * 用户登出
 */
export function logout(): Promise<{ message: string }> {
  return request.post('/auth/logout')
}




