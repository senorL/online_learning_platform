import api from './index'

export const getMistakes = (subject?: string) =>
  api.get('/my/mistakes', { params: { subject } })

export const removeMistake = (id: number) => api.delete(`/my/mistakes/${id}`)

export const getReview = () => api.get('/my/review')

export const markReviewed = (id: number) => api.post(`/my/review/${id}`)

export const aiExplain = (id: number) => api.post(`/my/mistakes/${id}/ai-explain`)
