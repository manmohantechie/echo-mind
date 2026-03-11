import { useState, useCallback } from 'react'
import { queryKnowledgeBase } from '../utils/api'
import toast from 'react-hot-toast'

export function useChat() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm **EchoMind**. Upload your documents and ask me anything about them. I'll provide answers with cited sources from your knowledge base.",
      sources: [],
      timestamp: new Date(),
    },
  ])
  const [loading, setLoading] = useState(false)
  const [selectedDocIds, setSelectedDocIds] = useState(null)

  const sendMessage = useCallback(async (query) => {
    if (!query.trim() || loading) return

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const result = await queryKnowledgeBase({
        query,
        top_k: 5,
        document_ids: selectedDocIds,
      })

      const assistantMsg = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
        tokens: result.tokens_used,
        latency: result.latency_ms,
        model: result.model_used,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your query. Please try again.',
        sources: [],
        isError: true,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMsg])
      toast.error('Query failed. Check that the API is running.')
    } finally {
      setLoading(false)
    }
  }, [loading, selectedDocIds])

  const clearChat = useCallback(() => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: "Chat cleared! Ask me anything about your documents.",
      sources: [],
      timestamp: new Date(),
    }])
  }, [])

  return { messages, loading, sendMessage, clearChat, selectedDocIds, setSelectedDocIds }
}
