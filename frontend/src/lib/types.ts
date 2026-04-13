export interface Thread {
  id: string
  openai_thread_id: string
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  thread_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  subagentEvents?: SubAgentEvent[]
}

export interface SubAgentEvent {
  type: 'start' | 'reasoning' | 'done'
  data: Record<string, unknown>
}
