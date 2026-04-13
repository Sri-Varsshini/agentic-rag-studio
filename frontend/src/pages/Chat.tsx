import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { api } from '../lib/api'
import type { Thread, Message, SubAgentEvent } from '../lib/types'
import ThreadList from '../components/ThreadList'
import MessageList from '../components/MessageList'
import MessageInput from '../components/MessageInput'

export default function Chat() {
  const [threads, setThreads] = useState<Thread[]>([])
  const [currentThread, setCurrentThread] = useState<Thread | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [token, setToken] = useState<string>('')

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.access_token) setToken(session.access_token)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setToken(session?.access_token ?? '')
    })

    return () => subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (!token) return
    api.getThreads(token).then(data => {
      setThreads(Array.isArray(data) ? data : [])
    })
  }, [token])

  const loadMessages = async (threadId: string) => {
    const data = await api.getMessages(token, threadId)
    setMessages(Array.isArray(data) ? data : [])
  }

  const handleNewThread = async () => {
    const thread = await api.createThread(token, 'New Chat')
    setThreads(prev => [thread, ...prev])
    setCurrentThread(thread)
    setMessages([])
  }

  const handleSelectThread = (thread: Thread) => {
    setCurrentThread(thread)
    loadMessages(thread.id)
  }

  const handleSendMessage = async (content: string) => {
    if (!currentThread) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      thread_id: currentThread.id,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])

    let assistantContent = ''
    const subagentEvents: SubAgentEvent[] = []

    const updateStreaming = () => {
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== 'streaming')
        return [...filtered, {
          id: 'streaming',
          thread_id: currentThread.id,
          role: 'assistant' as const,
          content: assistantContent,
          created_at: new Date().toISOString(),
          subagentEvents: subagentEvents.length > 0 ? [...subagentEvents] : undefined
        }]
      })
    }

    await api.sendMessage(
      token,
      currentThread.id,
      content,
      (chunk) => {
        assistantContent += chunk
        updateStreaming()
      },
      (event) => {
        subagentEvents.push(event)
        updateStreaming()
      },
      () => loadMessages(currentThread.id)
    )
  }

  return (
    <div className="flex h-full bg-gray-100">
      <div className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b">
          <button
            onClick={handleNewThread}
            disabled={!token}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            New Chat
          </button>
        </div>
        <ThreadList
          threads={threads}
          currentThread={currentThread}
          onSelectThread={handleSelectThread}
        />
      </div>
      <div className="flex-1 flex flex-col min-h-0">
        {currentThread ? (
          <>
            <div className="flex-1 overflow-y-auto">
              <MessageList messages={messages} />
            </div>
            <MessageInput onSend={handleSendMessage} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a thread or create a new one
          </div>
        )}
      </div>
    </div>
  )
}
