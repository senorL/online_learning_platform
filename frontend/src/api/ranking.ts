import api from './index'

export const getRanking = (params?: { period?: string; dimension?: string }) =>
  api.get('/ranking', { params })
