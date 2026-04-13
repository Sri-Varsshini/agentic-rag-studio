import { useState } from 'react'
import type { Message, SubAgentEvent } from '../lib/types'

function SubAgentBlock({ events }: { events: SubAgentEvent[] }) {
  const [open, setOpen] = useState(false)
  const doneEvent = events.find(e => e.type === 'done')
  const answer = doneEvent?.data?.answer as string | undefined

  return (
    <div className="mt-2 border border-purple-200 rounded-md bg-purple-50 text-sm">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 text-purple-700 font-medium hover:bg-purple-100 rounded-md"
      >
        <span className="text-xs">🤖</span>
        <span>Sub-agent analysis</span>
        <span className="ml-auto text-xs text-purple-400">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="px-3 pb-3 space-y-2 border-t border-purple-200">
          {events.map((e, i) => (
            <div key={i} className="mt-2">
              {e.type === 'start' && (
                <p className="text-purple-500 text-xs italic">
                  Delegating to sub-agent for full document analysis...
                </p>
              )}
              {e.type === 'reasoning' && (
                <p className="text-purple-600 text-xs italic">
                  {(e.data?.status as string) ?? 'Thinking...'}
                </p>
              )}
              {e.type === 'done' && answer && (
                <div>
                  <p className="text-xs font-semibold text-purple-700 mb-1">Sub-agent result:</p>
                  <p className="text-gray-700 whitespace-pre-wrap text-xs">{answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

interface MessageListProps {
  messages: Message[]
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="p-4 space-y-4">
      {messages.map(message => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-2xl px-4 py-2 rounded-lg ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-900 border'
            }`}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
            {message.subagentEvents && message.subagentEvents.length > 0 && (
              <SubAgentBlock events={message.subagentEvents} />
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
