import { useState, useEffect, useRef } from 'react'
import { supabase } from '../lib/supabase'
import DocumentList from '../components/DocumentList'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Document {
  id: string
  filename: string
  status: 'processing' | 'completed' | 'failed'
  chunk_count: number
  created_at: string
  error?: string
}

export default function Ingestion() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [token, setToken] = useState('')
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.access_token) {
        setToken(session.access_token)
        loadDocuments(session.access_token)
      }
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.access_token) {
        setToken(session.access_token)
        loadDocuments(session.access_token)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  // Supabase Realtime — live status updates
  useEffect(() => {
    const channel = supabase
      .channel('documents')
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'documents' }, (payload) => {
        setDocuments(prev => prev.map(d => d.id === payload.new.id ? { ...d, ...payload.new } as Document : d))
      })
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [])

  const loadDocuments = async (accessToken: string) => {
    const res = await fetch(`${API_URL}/api/documents`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    })
    const data = await res.json()
    setDocuments(Array.isArray(data) ? data : [])
  }

  const uploadFile = async (file: File) => {
    if (!token) return
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_URL}/api/documents`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    const doc = await res.json()
    setDocuments(prev => [doc, ...prev])
    setUploading(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) uploadFile(file)
  }

  const handleDelete = async (id: string) => {
    await fetch(`${API_URL}/api/documents/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    setDocuments(prev => prev.filter(d => d.id !== id))
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Documents</h1>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.pdf,.docx,.html,.htm,.markdown"
          className="hidden"
          onChange={(e) => { if (e.target.files?.[0]) uploadFile(e.target.files[0]) }}
        />
        {uploading
          ? <p className="text-gray-500">Uploading...</p>
          : <p className="text-gray-500">Drag & drop a file here, or click to select<br /><span className="text-xs">.txt, .md, .pdf, .docx, .html supported</span></p>
        }
      </div>

      <DocumentList documents={documents} onDelete={handleDelete} />
    </div>
  )
}
