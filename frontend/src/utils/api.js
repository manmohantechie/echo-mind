import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 60000,
})

// ── Documents ─────────────────────────────────────────────────────
export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
  return res.data
}

export const listDocuments = async () => {
  const res = await api.get('/documents/')
  return res.data
}

export const getDocument = async (id) => {
  const res = await api.get(`/documents/${id}`)
  return res.data
}

export const deleteDocument = async (id) => {
  await api.delete(`/documents/${id}`)
}

// ── Query ─────────────────────────────────────────────────────────
export const queryKnowledgeBase = async ({ query, top_k = 5, document_ids = null }) => {
  const res = await api.post('/query/', { query, top_k, document_ids })
  return res.data
}

export const getQueryHistory = async (limit = 20) => {
  const res = await api.get(`/query/history?limit=${limit}`)
  return res.data
}

// ── Health ────────────────────────────────────────────────────────
export const checkHealth = async () => {
  const res = await axios.get(`${BASE_URL}/health`)
  return res.data
}
