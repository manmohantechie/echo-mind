import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Send, Loader2, Trash2, ChevronDown, ChevronUp, Zap } from 'lucide-react'
import clsx from 'clsx'

function SourceCard({ source, index }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden text-xs">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-3 py-2 bg-slate-800/80 text-slate-400 hover:text-slate-200 transition-colors"
      >
        <span className="font-mono">
          [{index + 1}] {source.document_name}
          {source.page_number && ` — p.${source.page_number}`}
          <span className="ml-2 text-cyan-600">
            {(source.relevance_score * 100).toFixed(0)}% match
          </span>
        </span>
        {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>
      {open && (
        <div className="px-3 py-2 bg-slate-900/60 text-slate-500 leading-relaxed border-t border-slate-700">
          {source.chunk_text}
        </div>
      )}
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={clsx(
        'max-w-[85%] rounded-2xl px-4 py-3',
        isUser
          ? 'bg-cyan-600 text-white rounded-tr-sm'
          : msg.isError
            ? 'bg-red-950/50 border border-red-800 text-red-300 rounded-tl-sm'
            : 'bg-slate-800 text-slate-200 rounded-tl-sm'
      )}>
        {/* Message content */}
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>

        {/* Sources */}
        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-3 space-y-1.5 border-t border-slate-700 pt-3">
            <p className="text-xs text-slate-500 font-mono mb-2">SOURCES</p>
            {msg.sources.map((s, i) => (
              <SourceCard key={i} source={s} index={i} />
            ))}
          </div>
        )}

        {/* Meta */}
        {msg.tokens && (
          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-slate-700/50 text-xs text-slate-600 font-mono">
            <Zap className="w-3 h-3" />
            <span>{msg.tokens} tokens</span>
            <span>·</span>
            <span>{msg.latency?.toFixed(0)}ms</span>
            <span>·</span>
            <span>{msg.model}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, loading, onSend, onClear }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    onSend(input.trim())
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-200 font-mono">ECHOMIND</h2>
          <p className="text-xs text-slate-600">Ask anything about your documents</p>
        </div>
        <button
          onClick={onClear}
          className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-400 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map(msg => (
          <Message key={msg.id} msg={msg} />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex items-center gap-2 text-slate-500">
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                <span className="text-sm font-mono">Searching knowledge base...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          rows={1}
          disabled={loading}
          className="flex-1 resize-none bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-600 transition-colors disabled:opacity-50 font-sans"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl px-4 transition-colors"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  )
}
