import { useEffect, useRef, useState } from 'react'
import {
  AutoAwesomeRounded,
  CloudUploadOutlined,
  DeleteOutlineRounded,
  InsertDriveFileOutlined,
  SendRounded
} from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Paper,
  Tooltip,
  Typography,
  Checkbox,
  FormControlLabel
} from '@mui/material'
import useAuth from '../hooks/useAuth'
import api from '../api/axios'
import FormattedMarkdown from '../components/common/FormattedMarkdown'
import { downloadFile } from '../services/fileService'

const ACCEPTED_TYPES = ['.pdf', '.docx', '.txt', '.xlsx', '.xls', '.csv']
const SUGGESTED = [
  'Summarize this document',
  'What are the key points?',
  'Generate an Excel sheet of WFH solutions',
  'Explain the main conclusions',
]

function formatErrorMessage(detail) {
  if (!detail) return 'An error occurred. Please try again.'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((e) => (typeof e === 'object' && e ? e.msg || e.message || JSON.stringify(e) : String(e)))
      .join('; ')
  }
  if (typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail)
  }
  return String(detail)
}

export default function KnowledgeAssistant() {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [isGlobal, setIsGlobal] = useState(false)
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)
  const bottomRef = useRef(null)

  /* ── Load uploaded documents on mount ── */
  const fetchDocuments = async () => {
    try {
      const res = await api.get('/knowledge/documents')
      if (Array.isArray(res.data)) {
        setDocuments(res.data)
      }
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  /* ── File Upload to Backend ── */
  const handleUploadFiles = async (incoming) => {
    if (!incoming || incoming.length === 0) return

    const validFiles = Array.from(incoming).filter((f) =>
      f && f.name && ACCEPTED_TYPES.some((ext) => f.name.toLowerCase().endsWith(ext))
    )
    const invalidFiles = Array.from(incoming).filter(
      (f) => f && f.name && !ACCEPTED_TYPES.some((ext) => f.name.toLowerCase().endsWith(ext))
    )

    if (invalidFiles.length > 0) {
      setError('Unsupported file type. Only PDF, DOCX, TXT, XLSX, and CSV are allowed.')
    }

    if (validFiles.length === 0) return

    setError('')
    setUploading(true)

    for (const file of validFiles) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_global', isGlobal)
      try {
        const res = await api.post('/knowledge/upload', formData)
        if (res?.data) {
          setDocuments((prev) => [res.data, ...prev.filter((d) => d.id !== res.data.id)])
        }
      } catch (err) {
        setError(formatErrorMessage(err.response?.data?.detail || err.message || 'Failed to upload document.'))
      }
    }

    setUploading(false)
    await fetchDocuments()
  }

  const handleDeleteDocument = async (id) => {
    try {
      await api.delete(`/knowledge/documents/${id}`)
      setDocuments((prev) => prev.filter((d) => d.id !== id))
    } catch (err) {
      setError(formatErrorMessage(err.response?.data?.detail || err.message || 'Could not delete document.'))
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    if (e.dataTransfer.files) {
      handleUploadFiles(e.dataTransfer.files)
    }
  }

  /* ── Ask Question via RAG Mode ── */
  const ask = async (promptOverride) => {
    const textToSubmit = (promptOverride || question).trim()
    if (!textToSubmit || loading) return

    setQuestion('')
    setError('')
    setLoading(true)

    setMessages((prev) => [...prev, { role: 'user', content: textToSubmit }])

    try {
      const res = await api.post('/knowledge/query', { query: textToSubmit })
      const answer = res?.data?.answer || res?.data?.response || res?.data?.content || res?.data || 'No response returned.'

      setMessages((prev) => [...prev, { role: 'assistant', content: String(answer) }])
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (err) {
      setError(formatErrorMessage(err.response?.data?.detail || err.message || 'Could not get a response. Please try again.'))
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask()
    }
  }

  const fileIcon = (filename) => {
    const str = String(filename || '').toLowerCase()
    if (str.endsWith('.pdf')) return '📄'
    if (str.endsWith('.docx')) return '📝'
    if (str.endsWith('.xlsx') || str.endsWith('.xls') || str.endsWith('.csv')) return '📊'
    return '📃'
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2.5 }}>

      {/* ── Header ── */}
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, mb: 0.5 }}>
          <Box sx={{ width: 34, height: 34, borderRadius: 2, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'grid', placeItems: 'center' }}>
            <AutoAwesomeRounded sx={{ color: '#fff', fontSize: 20 }} />
          </Box>
          <Typography variant="h5" sx={{ fontFamily: 'Outfit', fontWeight: 700, color: '#0f172a' }}>
            Knowledge Assistant
          </Typography>
        </Box>
        <Typography sx={{ fontSize: 13.5, color: '#64748b', ml: 5.7 }}>
          Upload PDF, Word, Excel, CSV, or Text documents and query them using Retrieval-Augmented Generation (RAG).
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '300px minmax(0, 1fr)' }, gap: 2.5, flex: 1, minHeight: 0 }}>

        {/* ══ LEFT PANEL: Upload ══ */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, minHeight: 0 }}>

          {/* Drop Zone */}
          <Paper
            variant="outlined"
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: dragging ? '2px dashed #6366f1' : '2px dashed #cbd5e1',
              borderRadius: 3,
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              background: dragging ? '#f5f3ff' : '#fafbff',
              transition: 'all 0.18s ease',
              '&:hover': { borderColor: '#818cf8', background: '#f5f3ff' }
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.csv,.xlsx,.xls"
              hidden
              onChange={(e) => {
                if (e.target.files) {
                  handleUploadFiles(e.target.files)
                  e.target.value = ''
                }
              }}
            />
            {uploading ? (
              <CircularProgress size={36} sx={{ color: '#6366f1', mb: 1 }} />
            ) : (
              <CloudUploadOutlined sx={{ fontSize: 36, color: dragging ? '#6366f1' : '#94a3b8', mb: 1 }} />
            )}
            <Typography sx={{ fontWeight: 600, fontSize: 14, color: '#334155' }}>
              {uploading ? 'Processing & embedding document...' : dragging ? 'Drop files here' : 'Click or drag files here'}
            </Typography>
            <Typography sx={{ fontSize: 12, color: '#94a3b8', mt: 0.5 }}>
              PDF, DOCX, TXT, XLSX, CSV supported
            </Typography>
          </Paper>

          {user?.is_admin && (
            <Box sx={{ mt: 1 }}>
              <FormControlLabel
                control={<Checkbox size="small" checked={isGlobal} onChange={(e) => setIsGlobal(e.target.checked)} />}
                label={<Typography fontSize={13}>Make available to all employees (Company Document)</Typography>}
              />
            </Box>
          )}

          {/* Uploaded Document List */}
          {Array.isArray(documents) && documents.length > 0 && (
            <Paper variant="outlined" sx={{ borderRadius: 3, overflow: 'hidden' }}>
              <Box sx={{ px: 2, py: 1.2, borderBottom: '1px solid #f1f5f9', background: '#f8fafc' }}>
                <Typography sx={{ fontSize: 12, fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  Uploaded Documents ({documents.length})
                </Typography>
              </Box>
              {documents.map((doc, idx) => {
                const name = doc?.original_filename || doc?.stored_filename || 'Document'
                const docId = doc?.id || idx
                return (
                  <Box
                    key={docId}
                    sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 2, py: 1.2, borderBottom: '1px solid #f1f5f9', '&:last-child': { borderBottom: 'none' }, '&:hover': { background: '#f8fafc' } }}
                  >
                    <Typography sx={{ fontSize: 18, lineHeight: 1 }}>{fileIcon(name)}</Typography>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography sx={{ fontSize: 13, fontWeight: 600, color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {name}
                      </Typography>
                      <Typography sx={{ fontSize: 11, color: '#10b981', fontWeight: 600 }}>
                        Indexed & Ready
                      </Typography>
                    </Box>
                    <Tooltip title="Remove">
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleDeleteDocument(docId) }} sx={{ color: '#94a3b8', '&:hover': { color: '#ef4444', background: '#fee2e2' } }}>
                        <DeleteOutlineRounded fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                )
              })}
            </Paper>
          )}

          {(!Array.isArray(documents) || documents.length === 0) && !uploading && (
            <Paper variant="outlined" sx={{ borderRadius: 3, p: 2.5, textAlign: 'center', background: '#f8fafc', border: '1px dashed #e2e8f0' }}>
              <InsertDriveFileOutlined sx={{ fontSize: 28, color: '#cbd5e1', mb: 0.5 }} />
              <Typography sx={{ fontSize: 13, color: '#94a3b8' }}>No documents uploaded yet</Typography>
            </Paper>
          )}
        </Box>

        {/* ══ RIGHT PANEL: Q&A ══ */}
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <Paper variant="outlined" sx={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: 3, overflow: 'hidden', minHeight: 0 }}>

            {/* Chat header */}
            <Box sx={{ px: 2.5, py: 1.5, borderBottom: '1px solid #f1f5f9', background: '#f8fafc', flexShrink: 0 }}>
              <Typography sx={{ fontSize: 13, fontWeight: 700, color: '#475569' }}>
                Ask questions about your documents
              </Typography>
            </Box>

            {/* Messages */}
            <Box sx={{ flex: 1, overflowY: 'auto', p: 2.5, display: 'flex', flexDirection: 'column', gap: 1.5, minHeight: 0, background: '#fbfcff' }}>
              {messages.length === 0 && (
                <Box sx={{ m: 'auto', textAlign: 'center', color: '#94a3b8', py: 4 }}>
                  <AutoAwesomeRounded sx={{ fontSize: 36, mb: 1, opacity: 0.4 }} />
                  <Typography sx={{ fontSize: 14, fontWeight: 600, color: '#475569' }}>
                    {documents.length === 0 ? 'Upload a document to get started' : 'Ready! Ask anything about your documents'}
                  </Typography>
                  {documents.length > 0 && (
                    <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                      {SUGGESTED.map((s) => (
                        <Chip
                          key={s}
                          label={s}
                          size="small"
                          onClick={() => ask(s)}
                          sx={{ cursor: 'pointer', fontSize: 12, '&:hover': { background: '#e0e7ff', color: '#4338ca' } }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              )}

              {Array.isArray(messages) && messages.map((msg, i) => {
                const rawContent = typeof msg?.content === 'string' ? msg.content : JSON.stringify(msg?.content || '')
                const sandboxMatch = rawContent.match(/sandbox:\/([^\s)]+\.(pdf|docx|xlsx))/i)
                const filename = sandboxMatch ? sandboxMatch[1] : null
                const displayContent = sandboxMatch ? rawContent.replace(/sandbox:\/[^\s)]+\.(pdf|docx|xlsx)/i, '').trim() : rawContent

                return (
                  <Box
                    key={i}
                    sx={{ display: 'flex', justifyContent: msg?.role === 'user' ? 'flex-end' : 'flex-start' }}
                  >
                    <Box
                      sx={{
                        maxWidth: '85%',
                        borderRadius: 2.5,
                        px: 2.5,
                        py: 1.5,
                        fontSize: 14,
                        lineHeight: 1.6,
                        overflowWrap: 'anywhere',
                        background: msg?.role === 'user' ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : '#fff',
                        color: msg?.role === 'user' ? '#fff' : '#1e293b',
                        boxShadow: msg?.role === 'user' ? 'none' : '0 2px 10px rgba(0,0,0,0.05)',
                        border: msg?.role === 'user' ? 'none' : '1px solid #e2e8f0'
                      }}
                    >
                      {msg?.role === 'user' ? (
                        <Typography sx={{ fontSize: 14, whiteSpace: 'pre-wrap', color: '#fff' }}>
                          {rawContent}
                        </Typography>
                      ) : (
                        <>
                          <FormattedMarkdown content={displayContent} />
                          {filename && (
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => downloadFile(filename)}
                              sx={{
                                mt: 2,
                                borderRadius: 2,
                                background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                                textTransform: 'none',
                                fontWeight: 600
                              }}
                            >
                              Download {filename.split('.').pop().toUpperCase()} File
                            </Button>
                          )}
                        </>
                      )}
                    </Box>
                  </Box>
                )
              })}
              {loading && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94a3b8' }}>
                  <CircularProgress size={14} />
                  <Typography sx={{ fontSize: 13 }}>Thinking…</Typography>
                </Box>
              )}
              <div ref={bottomRef} />
            </Box>

            {/* Error */}
            {error && (
              <Alert severity="error" onClose={() => setError('')} sx={{ mx: 2, mb: 1, borderRadius: 2, flexShrink: 0 }}>
                {error}
              </Alert>
            )}

            <Divider />

            {/* Suggested chips if messages exist */}
            {messages.length > 0 && documents.length > 0 && (
              <Box sx={{ px: 2, pt: 1.5, display: 'flex', gap: 1, flexWrap: 'wrap', flexShrink: 0 }}>
                {SUGGESTED.slice(0, 3).map((s) => (
                  <Chip
                    key={s}
                    label={s}
                    size="small"
                    onClick={() => ask(s)}
                    sx={{ cursor: 'pointer', fontSize: 12, '&:hover': { background: '#e0e7ff', color: '#4338ca' } }}
                  />
                ))}
              </Box>
            )}

            {/* Input */}
            <Box
              component="form"
              onSubmit={(e) => { e.preventDefault(); ask() }}
              sx={{ display: 'flex', gap: 1, p: 2, flexShrink: 0 }}
            >
              <Box
                component="textarea"
                id="ka-question-input"
                rows={1}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={onKey}
                disabled={loading}
                placeholder={documents.length === 0 ? 'Upload a document first…' : 'Ask a question about your documents…'}
                sx={{
                  flex: 1,
                  border: '1px solid #e2e8f0',
                  borderRadius: 2.5,
                  px: 1.5,
                  py: 1.2,
                  fontSize: 14,
                  fontFamily: 'inherit',
                  resize: 'none',
                  outline: 'none',
                  background: '#fff',
                  color: '#1e293b',
                  '&:focus': { borderColor: '#818cf8' },
                  '&::placeholder': { color: '#94a3b8' }
                }}
              />
              <IconButton
                id="ka-send-btn"
                type="submit"
                disabled={!question.trim() || loading || documents.length === 0}
                sx={{
                  width: 42,
                  height: 42,
                  borderRadius: 2.5,
                  background: question.trim() && !loading && documents.length > 0 ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : '#f1f5f9',
                  color: question.trim() && !loading && documents.length > 0 ? '#fff' : '#94a3b8',
                  transition: 'all 0.2s',
                  '&:hover': { transform: 'scale(1.05)' },
                  alignSelf: 'flex-end'
                }}
              >
                <SendRounded fontSize="small" />
              </IconButton>
            </Box>
          </Paper>
        </Box>
      </Box>
    </Box>
  )
}
