import type { Thread } from '../lib/types'

interface ThreadListProps {
  threads: Thread[]
  currentThread: Thread | null
  onSelectThread: (thread: Thread) => void
}

export default function ThreadList({ threads, currentThread, onSelectThread }: ThreadListProps) {
  return (
    <div className="flex-1 overflow-y-auto">
      {threads.map(thread => (
        <div
          key={thread.id}
          onClick={() => onSelectThread(thread)}
          className={`p-4 cursor-pointer hover:bg-gray-50 border-b ${
            currentThread?.id === thread.id ? 'bg-blue-50' : ''
          }`}
        >
          <p className="font-medium truncate">{thread.title || 'New Chat'}</p>
          <p className="text-xs text-gray-500">
            {new Date(thread.updated_at).toLocaleDateString()}
          </p>
        </div>
      ))}
    </div>
  )
}
