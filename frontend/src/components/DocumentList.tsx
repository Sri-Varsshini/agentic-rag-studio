interface Document {
  id: string
  filename: string
  status: 'processing' | 'completed' | 'failed'
  chunk_count: number
  created_at: string
  error?: string
}

interface DocumentListProps {
  documents: Document[]
  onDelete: (id: string) => void
}

const statusBadge = (status: string) => {
  const styles: Record<string, string> = {
    processing: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] ?? ''}`}>
      {status}
    </span>
  )
}

export default function DocumentList({ documents, onDelete }: DocumentListProps) {
  if (documents.length === 0) {
    return <p className="text-gray-500 text-sm mt-4">No documents uploaded yet.</p>
  }

  return (
    <div className="mt-4 space-y-2">
      {documents.map(doc => (
        <div key={doc.id} className="flex items-center justify-between p-3 bg-white border rounded-lg">
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{doc.filename}</p>
            <p className="text-xs text-gray-500">
              {doc.status === 'completed' ? `${doc.chunk_count} chunks` : doc.error ?? ''}
            </p>
          </div>
          <div className="flex items-center gap-3 ml-4">
            {statusBadge(doc.status)}
            <button
              onClick={() => onDelete(doc.id)}
              className="text-red-500 hover:text-red-700 text-sm"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
