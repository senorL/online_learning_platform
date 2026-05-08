import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器：自动附加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || '请求失败'
    if (status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    } else if (status === 403) {
      alert('没有权限执行此操作')
    } else if (status === 422) {
      const errors = error.response?.data?.detail
      if (Array.isArray(errors)) {
        alert(errors.map((e: any) => e.msg).join('\n'))
      } else {
        alert(detail)
      }
    } else {
      alert(detail)
    }
    return Promise.reject(error)
  }
)

export default api
