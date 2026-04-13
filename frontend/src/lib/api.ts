import type { Thread, Message, SubAgentEvent } from './types'
export type { Thread, Message, SubAgentEvent }

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  async createThread(token: string, title?: string): Promise<Thread> {
    const res = await fetch(`${API_URL}/api/threads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ title })
    })
    return res.json()
  },

  async getThreads(token: string): Promise<Thread[]> {
    const res = await fetch(`${API_URL}/api/threads`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    return res.json()
  },

  async getMessages(token: string, threadId: string): Promise<Message[]> {
    const res = await fetch(`${API_URL}/api/threads/${threadId}/messages`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    return res.json()
  },

  async sendMessage(
    token: string,
    threadId: string,
    content: string,
    onChunk: (chunk: string) => void,
    onSubAgentEvent: (event: SubAgentEvent) => void,
    onDone: () => void
  ) {
    const response = await fetch(`${API_URL}/api/threads/${threadId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          // handled via data line below
        } else if (line.startsWith('data: ')) {
          // find the event type from the preceding event: line
          const eventLineIdx = lines.indexOf(line) - 1
          const eventType = eventLineIdx >= 0 && lines[eventLineIdx].startsWith('event: ')
            ? lines[eventLineIdx].slice(7).trim()
            : 'message'

          try {
            const data = JSON.parse(line.slice(6))

            if (eventType === 'message' && data.content) {
              onChunk(data.content)
            } else if (eventType === 'subagent_start') {
              onSubAgentEvent({ type: 'start', data })
            } else if (eventType === 'subagent_reasoning') {
              onSubAgentEvent({ type: 'reasoning', data })
            } else if (eventType === 'subagent_done') {
              onSubAgentEvent({ type: 'done', data })
            } else if (data.status === 'complete') {
              onDone()
            }
          } catch {
            // skip malformed lines
          }
        }
      }
    }
  }
}
