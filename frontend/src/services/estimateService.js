import api from '../api/axios'
import { downloadFile } from './fileService'

export const generateEstimate = async (estimateData) => {
  const response = await api.post('/estimate/generate', estimateData)
  return response.data
}

export const exportEstimate = async (estimateData) => {
  const response = await api.post('/estimate/export', estimateData)
  if (response.data && response.data.filename) {
    await downloadFile(response.data.filename)
  }
  return response.data
}

export const refineEstimate = async (refineData) => {
  const response = await api.post('/estimate/refine', refineData)
  return response.data
}
