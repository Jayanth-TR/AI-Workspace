import { useEffect, useRef, useState } from 'react'
import { getChats, getMessages, sendMessage, startChat, deleteChat } from '../services/chatService'
import { downloadFile } from '../services/fileService'
import SearchResultCard from '../components/chat/SearchResultCard'
import FormattedMarkdown from '../components/common/FormattedMarkdown'

const MODES = [
  { id: 'auto', label: 'Auto (AI Agent)', icon: '⚡' },
  { id: 'chat', label: 'AI Chat', icon: '💬' },
  { id: 'web_search', label: 'Web Search', icon: '🌐' },
  { id: 'rag', label: 'Knowledge Base', icon: '📚' },
]

const pageStyles = {
  display: 'grid', gridTemplateColumns: '250px minmax(0, 1fr)', gap: 18, height: '100%', flex: 1, minHeight: 0,
}

function parseSearchResult(content) {
  if (typeof content !== 'string') return null
  const trimmed = content.trim()
  if (!trimmed.startsWith('{') || !trimmed.endsWith('}')) return null
  try {
    const data = JSON.parse(trimmed)
    if (data && (data.title || data.summary || data.keyFacts || data.sources)) {
      return data
    }
  } catch (e) {
    return null
  }
  return null
}

export default function Chat() {
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [selectedMode, setSelectedMode] = useState('auto')
  const [plusMenuOpen, setPlusMenuOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const plusMenuRef = useRef(null)

  useEffect(() => {
    getChats()
      .then((data) => setChats(Array.isArray(data) ? data : []))
      .catch(() => setError('Your conversations could not be loaded.'))
  }, [])

  useEffect(() => {
    function handleClickOutside(event) {
      if (plusMenuRef.current && !plusMenuRef.current.contains(event.target)) {
        setPlusMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (!activeChatId) return
    getMessages(activeChatId)
      .then((data) => {
        const msgArray = Array.isArray(data) ? data : []
        setMessages(msgArray)
        setTimeout(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, 50)
      })
      .catch(() => setError('This conversation could not be loaded.'))
  }, [activeChatId])

  useEffect(() => { 
    const timer = setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
    return () => clearTimeout(timer)
  }, [messages, loading])

  const newChat = () => { setActiveChatId(null); setMessages([]); setDraft(''); setError('') }
  const chooseChat = (id) => { setActiveChatId(id); setError('') }

  const handleDeleteChat = async (id) => {
    if (!window.confirm('Are you sure you want to delete this conversation?')) return
    try {
      await deleteChat(id)
      setChats((current) => current.filter((chat) => chat.id !== id))
      if (activeChatId === id) {
        setActiveChatId(null)
        setMessages([])
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not delete the conversation.')
    }
  }

  const streamMessageWordByWord = (fullText, agentDecision) => {
    const tokens = fullText.split(/(\s+)/)
    let currentIdx = 0

    setMessages((current) => [
      ...current,
      { role: 'assistant', content: '', isStreaming: true, agent_decision: agentDecision }
    ])

    const interval = setInterval(() => {
      currentIdx++
      const partialText = tokens.slice(0, currentIdx).join('')

      setMessages((current) => {
        const next = [...current]
        const lastIndex = next.length - 1
        if (lastIndex >= 0 && next[lastIndex].role === 'assistant') {
          next[lastIndex] = {
            ...next[lastIndex],
            content: partialText,
            isStreaming: currentIdx < tokens.length
          }
        }
        return next
      })

      if (currentIdx >= tokens.length) {
        clearInterval(interval)
        setLoading(false)
      }
    }, 18)
  }

  const submit = async (event) => {
    event.preventDefault()
    const content = draft.trim()
    if (!content || loading) return

    setDraft('')
    setError('')
    setLoading(true)
    setMessages((current) => [...current, { role: 'user', content }])

    try {
      let result
      if (activeChatId) {
        result = await sendMessage(activeChatId, content, selectedMode)
      } else {
        result = await startChat(content, selectedMode)
        setActiveChatId(result.chat_id)
        setChats((current) => [{ id: result.chat_id, title: content.slice(0, 50) }, ...current])
      }
      const replyContent = result.response?.content || result.response || result.message || 'No response content.'
      streamMessageWordByWord(replyContent, result.agent_decision)
    } catch (err) {
      setError(err.response?.data?.detail || 'Message could not be sent.')
      setMessages((current) => current.slice(0, -1))
      setLoading(false)
    }
  }

  return (
    <section style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0, overflow: 'hidden', paddingBottom: 24 }}>
      <div style={{ marginBottom: 26, flexShrink: 0, overflow: 'hidden' }}>
        <div style={{ color: '#2563eb', fontSize: 12, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 7 }}>AI Agent Workspace</div>
        <p style={{ margin: '8px 0 0', color: '#64748b' }}>Autonomous agent routing across AI Chat, Web Search, & Knowledge Base.</p>
      </div>
      <div className="chat-layout" style={pageStyles}>
        <aside style={{ background: '#fff', border: '1px solid #e3e8f2', borderRadius: 16, padding: 14, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <button type="button" onClick={newChat} style={primaryButton}>+ New conversation</button>
          <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', marginTop: 12 }}>
            {chats.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: 13, textAlign: 'center', marginTop: 24 }}>No previous chats</p>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    borderRadius: 10,
                    marginBottom: 4,
                    background: chat.id === activeChatId ? '#eff4ff' : 'transparent',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  <button
                    type="button"
                    onClick={() => chooseChat(chat.id)}
                    style={{
                      border: 0,
                      width: '100%',
                      textAlign: 'left',
                      padding: '9px 12px',
                      fontSize: 13,
                      fontWeight: chat.id === activeChatId ? 700 : 500,
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      flex: 1,
                      background: 'transparent',
                      color: chat.id === activeChatId ? '#2455d9' : '#334155',
                      marginBottom: 0,
                      paddingRight: 28,
                    }}
                  >
                    {chat.title || 'Untitled conversation'}
                  </button>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteChat(chat.id)
                    }}
                    style={{
                      background: 'transparent',
                      border: 0,
                      cursor: 'pointer',
                      color: '#94a3b8',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: 6,
                      borderRadius: 6,
                      transition: 'all 0.2s',
                      position: 'absolute',
                      right: 4,
                    }}
                    title="Delete conversation"
                    onMouseEnter={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239, 68, 68, 0.08)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = '#94a3b8'; e.currentTarget.style.background = 'transparent'; }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>
        <div style={{ minWidth: 0, display: 'flex', flexDirection: 'column', background: '#fff', border: '1px solid #e3e8f2', borderRadius: 16, overflow: 'hidden', minHeight: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #e7ebf2', fontSize: 14, fontWeight: 700, flexShrink: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>✦ Workspace AI Agent</span>
            <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>Active Tool: {MODES.find(m => m.id === selectedMode)?.label}</span>
          </div>
          <div className="chat-messages" style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: 22, background: '#fbfcff', display: 'flex', flexDirection: 'column' }}>
            {messages.length === 0 && (
              <div style={{ maxWidth: 460, margin: '60px auto', textAlign: 'center', color: '#64748b' }}>
                <div style={{ fontSize: 36 }}>⚡</div>
                <strong style={{ display: 'block', color: '#26334c', marginTop: 10, fontSize: 18 }}>Auto AI Agent Workflow</strong>
                <p style={{ fontSize: 14, marginTop: 6 }}>Type any request and the Auto AI Agent will automatically choose the tool (Chat, Web Search, or Knowledge Base). Use the <strong>+</strong> icon to select a specific tool.</p>
              </div>
            )}
            {messages.map((message, index) => {
              const sandboxMatch = message.content?.match(/sandbox:\/([^\s)]+\.(pdf|docx|xlsx))/i)
              const filename = sandboxMatch ? sandboxMatch[1] : null
              const displayContent = sandboxMatch ? message.content.replace(/sandbox:\/[^\s)]+\.(pdf|docx|xlsx)/i, '').trim() : message.content
              const searchResultData = message.role === 'assistant' ? parseSearchResult(displayContent) : null

              return (
                <div key={`${message.role}-${index}`} style={{ display: 'flex', flexDirection: 'column', alignItems: message.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: 16 }}>
                  {message.role === 'assistant' && message.agent_decision && (
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 600, color: '#2563eb', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 12, padding: '3px 10px', marginBottom: 6 }}>
                      <span>🤖 Agent Tool Executed:</span>
                      <strong>{message.agent_decision.display_name}</strong>
                    </div>
                  )}
                  {searchResultData ? (
                    <div style={{ maxWidth: '88%', width: '100%' }}>
                      <SearchResultCard data={searchResultData} />
                    </div>
                  ) : (
                    <div
                      style={{
                        maxWidth: '82%',
                        borderRadius: 14,
                        padding: '12px 18px',
                        lineHeight: 1.55,
                        fontSize: 14,
                        overflowWrap: 'anywhere',
                        color: message.role === 'user' ? '#fff' : '#27344e',
                        background: message.role === 'user' ? '#3061e9' : '#fff',
                        boxShadow: message.role === 'user' ? 'none' : '0 2px 12px rgba(22,40,80,.06)',
                        border: message.role === 'user' ? 'none' : '1px solid #e3e8f2'
                      }}
                    >
                      {message.role === 'user' ? (
                        <span style={{ whiteSpace: 'pre-wrap' }}>{displayContent}</span>
                      ) : (
                        <>
                          <FormattedMarkdown content={displayContent} />
                          {message.isStreaming && (
                            <span style={{ display: 'inline-block', color: '#2563eb', fontWeight: 'bold', marginLeft: 4, animation: 'pulse 1s infinite' }}>▋</span>
                          )}
                        </>
                      )}
                      {filename && (
                        <button
                          type="button"
                          onClick={() => downloadFile(filename)}
                          style={{ ...primaryButton, width: 'auto', marginTop: 12 }}
                        >
                          📥 Download {filename.split('.').pop().toUpperCase()} File
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
            {loading && <p style={{ color: '#64748b', fontSize: 13 }}>⚡ AI Agent is selecting tool and executing workflow…</p>}<div ref={bottomRef} />
          </div>
          {error && <div style={{ margin: '12px 16px 0', padding: 12, borderRadius: 10, background: '#fff0f0', color: '#a32c2c', fontSize: 13, flexShrink: 0 }}>{error}</div>}

          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: 14, borderTop: '1px solid #e7ebf2', flexShrink: 0, background: '#fff', position: 'relative' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div ref={plusMenuRef} style={{ position: 'relative' }}>
                <button
                  type="button"
                  onClick={() => setPlusMenuOpen((prev) => !prev)}
                  title="Choose AI Tool (+)"
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    border: plusMenuOpen ? '1px solid #3061e9' : '1px solid #cbd5e1',
                    background: plusMenuOpen ? '#eff6ff' : '#f8fafc',
                    color: plusMenuOpen ? '#2455d9' : '#475569',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: 18,
                    fontWeight: 700,
                    transition: 'all 0.15s ease',
                    outline: 'none'
                  }}
                >
                  +
                </button>

                {plusMenuOpen && (
                  <div
                    style={{
                      position: 'absolute',
                      bottom: '42px',
                      left: 0,
                      width: 230,
                      background: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: 12,
                      boxShadow: '0 10px 25px -5px rgba(0,0,0,0.12), 0 8px 10px -6px rgba(0,0,0,0.05)',
                      padding: '6px',
                      zIndex: 200
                    }}
                  >
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#94a3b8', padding: '6px 10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Select AI Tool
                    </div>
                    {MODES.map((m) => {
                      const isSelected = selectedMode === m.id
                      return (
                        <button
                          key={m.id}
                          type="button"
                          onClick={() => {
                            setSelectedMode(m.id)
                            setPlusMenuOpen(false)
                          }}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            width: '100%',
                            padding: '8px 10px',
                            borderRadius: 8,
                            border: 0,
                            background: isSelected ? '#eff6ff' : 'transparent',
                            color: isSelected ? '#2455d9' : '#334155',
                            fontSize: 13,
                            fontWeight: isSelected ? 700 : 500,
                            cursor: 'pointer',
                            textAlign: 'left',
                            transition: 'background 0.15s'
                          }}
                        >
                          <span style={{ fontSize: 15 }}>{m.icon}</span>
                          <span style={{ flex: 1 }}>{m.label}</span>
                          {isSelected && <span style={{ fontSize: 12, color: '#2455d9' }}>✓</span>}
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>

              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '4px 10px',
                  borderRadius: 16,
                  background: selectedMode === 'auto' ? '#eff6ff' : '#f1f5f9',
                  border: selectedMode === 'auto' ? '1px solid #bfdbfe' : '1px solid #cbd5e1',
                  fontSize: 12,
                  color: selectedMode === 'auto' ? '#1d4ed8' : '#475569',
                  fontWeight: 600
                }}
              >
                <span>{MODES.find(m => m.id === selectedMode)?.icon}</span>
                <span>{MODES.find(m => m.id === selectedMode)?.label}</span>
                {selectedMode !== 'auto' && (
                  <button
                    type="button"
                    onClick={() => setSelectedMode('auto')}
                    title="Reset to Auto AI Agent"
                    style={{
                      border: 0,
                      background: 'transparent',
                      color: '#94a3b8',
                      cursor: 'pointer',
                      fontSize: 14,
                      marginLeft: 2,
                      padding: 0,
                      display: 'flex',
                      alignItems: 'center',
                      lineHeight: 1
                    }}
                  >
                    ×
                  </button>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <input
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                disabled={loading}
                placeholder={
                  selectedMode === 'auto'
                    ? "Ask Auto AI Agent anything..."
                    : `Message using ${MODES.find(m => m.id === selectedMode)?.label}...`
                }
                style={{ flex: 1, minWidth: 0, border: '1px solid #ccd5e3', borderRadius: 10, padding: '11px 13px', font: 'inherit' }}
              />
              <button
                type="submit"
                disabled={!draft.trim() || loading}
                style={{ ...primaryButton, width: 'auto', padding: '0 18px', opacity: !draft.trim() || loading ? 0.55 : 1 }}
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}

const primaryButton = { width: '100%', border: 0, borderRadius: 10, padding: '12px 14px', background: '#3061e9', color: '#fff', cursor: 'pointer', font: '600 14px inherit' }
const chatButton = { width: '100%', border: 0, borderRadius: 9, padding: '10px 11px', textAlign: 'left', cursor: 'pointer', font: '500 13px inherit', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginBottom: 3 }

async function createAttachmentIfNeeded(conversation) {
  const latest = conversation.length > 0 ? conversation[conversation.length - 1]?.content : ''
  const match = latest.match(/sandbox:\/([^\s)]+\.(pdf|docx|xlsx))/i)
  if (!match) return null
  const filename = match[1]
  const file = { filename }

  const saved = JSON.parse(sessionStorage.getItem('workspace_files') || '[]')
  if (!saved.some((f) => f.filename === filename)) {
    const userPrompt = conversation.length >= 2 ? conversation[conversation.length - 2]?.content : 'Generated from chat'
    sessionStorage.setItem('workspace_files', JSON.stringify([{ filename, prompt: userPrompt, createdAt: Date.now() }, ...saved]))
  }
  return file
}
