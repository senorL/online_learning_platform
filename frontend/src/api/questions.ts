import api from './index'

export const getQuestions = (params?: any) => api.get('/questions', { params })
export const getQuestionsBySubject = (subject: string) => api.get(`/questions/by-subject/${subject}`)
export const submitAnswer = (data: { question_id: number; user_answer: string; subject?: string; chapter?: string }) =>
  api.post('/questions/submit', data)
export const createQuestion = (data: any) => api.post('/questions', data)
export const updateQuestion = (id: number, data: any) => api.put(`/questions/${id}`, data)
export const deleteQuestion = (id: number) => api.delete(`/questions/${id}`)
export const importQuestions = (data: any[]) => api.post('/questions/import', data)

// AI智能出题
export const generateQuestions = (data: {
  subject: string
  chapter: string
  difficulty?: string
  types?: string[]
  count?: number
}) => api.post('/questions/generate', data, { timeout: 60000 })
