/**
 * API 请求封装
 */
import axios from 'axios'
import { API_BASE_URL } from './config'

// 创建 axios 实例
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API 请求错误:', error)
    
    // 提供更详细的错误信息
    if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
      console.error('无法连接到后端服务，请检查:')
      console.error('  1. 后端服务是否已启动 (http://127.0.0.1:8000)')
      console.error('  2. 后端服务是否正常运行')
      console.error('  3. 防火墙是否阻止了连接')
      error.message = '无法连接到后端服务，请确保后端服务已启动 (http://127.0.0.1:8000)'
    } else if (error.response) {
      // 服务器返回了错误响应
      error.message = error.response.data?.detail || error.response.data?.message || error.message
    }
    
    return Promise.reject(error)
  }
)

export default request

