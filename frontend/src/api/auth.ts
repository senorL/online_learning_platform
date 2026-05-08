import api from './index'

export const registerUser = (data: { username: string; password: string; grade?: string }) =>
  api.post('/register', data)

export const loginUser = (data: { username: string; password: string }) =>
  api.post('/login', data)

export const getProfile = () => api.get('/my/profile')

export const updateProfile = (data: { grade?: string; password?: string; avatar?: string }) =>
  api.put('/my/profile', data)

export const getHeatmap = () => api.get('/my/heatmap')

export const getActivity = (date?: string) =>
  api.get('/my/activity', { params: { date } })
