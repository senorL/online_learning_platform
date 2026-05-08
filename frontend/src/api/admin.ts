import api from './index'

export const getUsers = (params?: any) => api.get('/admin/users', { params })
export const updateUser = (id: number, data: any) => api.put(`/admin/users/${id}`, data)
export const getStats = () => api.get('/admin/stats')

// 章节管理
export const getChapters = (params?: any) => api.get('/admin/chapters', { params })
export const getChapterDetail = (id: number) => api.get(`/admin/chapters/${id}`)
export const updateChapter = (id: number, data: any) => api.put(`/admin/chapters/${id}`, data)
export const deleteAdminChapter = (id: number) => api.delete(`/admin/chapters/${id}`)
export const addVideoToChapter = (chapterId: number, data: any) =>
  api.post(`/admin/chapters/${chapterId}/videos`, data)
