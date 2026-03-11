import { useState, useEffect, useCallback } from 'react'
import { listDocuments, uploadDocument, deleteDocument, getDocument } from '../utils/api'
import toast from 'react-hot-toast'

export function useDocuments() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const fetchDocuments = useCallback(async () => {
    setLoading(true)
    try {
      const data = await listDocuments()
      setDocuments(data.documents || [])
    } catch (err) {
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  // Poll for status updates on processing documents
  useEffect(() => {
    const processingDocs = documents.filter(d => d.status === 'processing')
    if (processingDocs.length === 0) return

    const interval = setInterval(async () => {
      let updated = false
      for (const doc of processingDocs) {
        try {
          const fresh = await getDocument(doc.id)
          if (fresh.status !== 'processing') {
            updated = true
            if (fresh.status === 'ready') {
              toast.success(`"${fresh.original_name}" is ready!`)
            } else if (fresh.status === 'error') {
              toast.error(`Failed to process "${fresh.original_name}"`)
            }
          }
        } catch {}
      }
      if (updated) fetchDocuments()
    }, 3000)

    return () => clearInterval(interval)
  }, [documents, fetchDocuments])

  const upload = useCallback(async (file) => {
    setUploading(true)
    setUploadProgress(0)
    try {
      const doc = await uploadDocument(file, setUploadProgress)
      toast.success(`Uploading "${file.name}"...`)
      setDocuments(prev => [doc, ...prev])
      return doc
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed'
      toast.error(msg)
      throw err
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [])

  const remove = useCallback(async (id) => {
    const doc = documents.find(d => d.id === id)
    try {
      await deleteDocument(id)
      setDocuments(prev => prev.filter(d => d.id !== id))
      toast.success(`"${doc?.original_name}" deleted`)
    } catch {
      toast.error('Failed to delete document')
    }
  }, [documents])

  return { documents, loading, uploading, uploadProgress, upload, remove, refetch: fetchDocuments }
}
