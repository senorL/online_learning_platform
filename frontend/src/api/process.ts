import request from './index'

export const recordProcess = (data: { subject: string, chapter: string, minute: number, second: number }) => {
  return request.post('/process/record', data)
}

export const getLatestProcess = () => {
  return request.get('/process/latest')
}
