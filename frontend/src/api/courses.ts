import api from './index'

export const getCourses = (params?: { subject?: string; grade?: string }) =>
  api.get('/courses', { params })

export const getCourseDetail = (id: number) => api.get(`/courses/${id}`)

export const createCourse = (data: any) => api.post('/courses', data)
export const updateCourse = (id: number, data: any) => api.put(`/courses/${id}`, data)
export const deleteCourse = (id: number) => api.delete(`/courses/${id}`)

export const createChapter = (courseId: number, data: any) =>
  api.post(`/courses/${courseId}/chapters`, data)
export const updateChapter = (id: number, data: any) => api.put(`/chapters/${id}`, data)
export const deleteChapter = (id: number) => api.delete(`/chapters/${id}`)

export const createVideo = (chapterId: number, data: any) =>
  api.post(`/chapters/${chapterId}/videos`, data)
export const updateVideo = (id: number, data: any) => api.put(`/videos/${id}`, data)
export const deleteVideo = (id: number) => api.delete(`/videos/${id}`)
