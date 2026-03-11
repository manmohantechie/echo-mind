import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Loader2, CheckCircle, XCircle, Trash2 } from 'lucide-react'
import clsx from 'clsx'

function StatusBadge({ status }) {
  const map = {
    ready:      { label: 'Ready',      cls: 'bg-green-900/40 text-green-400 border-green-800' },
    processing: { label: 'Processing', cls: 'bg-yellow-900/40 text-yellow-400 border-yellow-800' },
    error:      { label: 'Error',      cls: 'bg-red-900/40 text-red-400 border-red-800' },
  }
  const s = map[status] || map.processing
  return (
    <span className={clsx('text-xs px-2 py-0.5 rounded border font-mono', s.cls)}>
      {s.label}
    </span>
  )
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function DocumentUploader({ documents, uploading, uploadProgress, onUpload, onDelete }) {
  const onDrop = useCallback((accepted) => {
    accepted.forEach(file => onUpload(file))
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'text/plain': ['.txt'], 'text/markdown': ['.md'] },
    multiple: true,
    disabled: uploading,
  })

  return (
    <div className="flex flex-col h-full">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 mb-4',
          isDragActive
            ? 'border-cyan-400 bg-cyan-950/30'
            : 'border-slate-700 hover:border-cyan-600 hover:bg-slate-800/50',
          uploading && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
            <p className="text-sm text-slate-400">Uploading... {uploadProgress}%</p>
            <div className="w-full bg-slate-700 rounded-full h-1.5 mt-1">
              <div
                className="bg-cyan-400 h-1.5 rounded-full transition-all"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="w-8 h-8 text-slate-500" />
            <p className="text-sm text-slate-400">
              {isDragActive ? 'Drop files here...' : 'Drag & drop or click to upload'}
            </p>
            <p className="text-xs text-slate-600">PDF, TXT, MD — up to 20 MB</p>
          </div>
        )}
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {documents.length === 0 && (
          <p className="text-center text-slate-600 text-sm py-8">No documents yet.</p>
        )}
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/60 border border-slate-700 group"
          >
            <FileText className="w-4 h-4 text-cyan-500 mt-0.5 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 truncate font-medium">{doc.original_name}</p>
              <div className="flex items-center gap-2 mt-1">
                <StatusBadge status={doc.status} />
                <span className="text-xs text-slate-600">{formatSize(doc.file_size)}</span>
                {doc.chunk_count > 0 && (
                  <span className="text-xs text-slate-600">{doc.chunk_count} chunks</span>
                )}
              </div>
            </div>
            <button
              onClick={() => onDelete(doc.id)}
              className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-600 hover:text-red-400 p-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
