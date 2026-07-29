import api from '../api/axios'
export const generateFile = async (prompt) => (await api.post('/files/generate', { prompt })).data
export const downloadFile = async (filename) => {
  const response = await api.get(`/files/download/${encodeURIComponent(filename)}`, { responseType: 'blob' })
  const url = URL.createObjectURL(response.data)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
export const deleteFile = async (filename) => api.delete(`/files/${encodeURIComponent(filename)}`)
