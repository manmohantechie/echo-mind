import { Brain } from 'lucide-react'
import { Toaster } from 'react-hot-toast'
import DocumentUploader from '../components/DocumentUploader'
import ChatWindow from '../components/ChatWindow'
import { useDocuments } from '../hooks/useDocuments'
import { useChat } from '../hooks/useChat'

export default function App() {
  const { documents, loading, uploading, uploadProgress, upload, remove } = useDocuments()
  const { messages, loading: chatLoading, sendMessage, clearChat } = useChat()

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col" style={{ fontFamily: 'Inter, sans-serif' }}>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155' },
        }}
      />

      {/* Navbar */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Brain className="w-6 h-6 text-cyan-400" />
          <span className="font-mono font-bold text-lg tracking-wider">
            ECHO<span className="text-cyan-400">MIND</span>
          </span>
        </div>
        <span className="text-slate-600 text-sm">·</span>
        <span className="text-slate-500 text-sm">AI Knowledge Assistant</span>
        <div className="ml-auto flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-slate-500 font-mono">
            {documents.filter(d => d.status === 'ready').length} docs ready
          </span>
        </div>
      </header>

      {/* Main layout */}
      <main className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-80 border-r border-slate-800 p-4 flex flex-col overflow-hidden">
          <h2 className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-3">
            Knowledge Base
          </h2>
          <div className="flex-1 overflow-hidden">
            <DocumentUploader
              documents={documents}
              uploading={uploading}
              uploadProgress={uploadProgress}
              onUpload={upload}
              onDelete={remove}
            />
          </div>
        </aside>

        {/* Chat area */}
        <section className="flex-1 p-6 overflow-hidden">
          <ChatWindow
            messages={messages}
            loading={chatLoading}
            onSend={sendMessage}
            onClear={clearChat}
          />
        </section>
      </main>
    </div>
  )
}
