import { useRef, useState } from 'react'
import {
  AutoAwesomeRounded,
  CloudUploadRounded,
  DeleteOutlineRounded,
  DescriptionOutlined,
  ForumOutlined,
  FolderOpenRounded,
  StarBorderRounded,
  CloseRounded,
  RequestQuoteRounded
} from '@mui/icons-material'
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  Stack,
  TextField,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import useAuth from '../hooks/useAuth'

const initialDocuments = [
  { name: 'Product Strategy.pdf', kind: 'PDF', size: '2.4 MB' },
  { name: 'Q3 Roadmap.docx', kind: 'DOCX', size: '840 KB' },
  { name: 'Team Insights.csv', kind: 'CSV', size: '300 KB' }
]

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  
  // Knowledge Assistant states
  const [assistantOpen, setAssistantOpen] = useState(false)
  const [question, setQuestion] = useState('')
  const [documents, setDocuments] = useState(initialDocuments)
  const [dragActive, setDragActive] = useState(false)
  const [isGlobal, setIsGlobal] = useState(false)

  const addDocuments = (files) => {
    const nextDocuments = Array.from(files).map((file) => ({
      name: file.name,
      kind: file.name.split('.').pop()?.toUpperCase() || 'FILE',
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`
    }))

    setDocuments((previous) => [...nextDocuments, ...previous].slice(0, 4))
  }

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files || [])
    if (files.length) addDocuments(files)
    event.target.value = ''
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setDragActive(false)
    const files = Array.from(event.dataTransfer?.files || [])
    if (files.length) addDocuments(files)
  }

  const removeDocument = (name) => {
    setDocuments((previous) => previous.filter((document) => document.name !== name))
  }

  return (
    <Box sx={{ display: 'grid', gap: 4, pb: 6 }}>
      {/* 1. Welcome Section Hero Banner */}
      <Card
        sx={{
          background: 'linear-gradient(135deg, #1E40AF 0%, #2563EB 50%, #3B82F6 100%)',
          color: '#FFFFFF',
          border: 'none',
          boxShadow: '0px 10px 30px rgba(37, 99, 235, 0.25)',
          overflow: 'hidden',
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '-20%',
            right: '-10%',
            width: '300px',
            height: '300px',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.08)',
            filter: 'blur(40px)',
            pointerEvents: 'none'
          }
        }}
      >
        <CardContent sx={{ p: { xs: 4, md: 5 } }}>
          <Stack spacing={2.5}>
            <Box>
              <Typography
                variant="h4"
                component="h1"
                fontWeight={800}
                sx={{
                  fontFamily: 'Outfit',
                  letterSpacing: '-0.02em',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                  mb: 1.5
                }}
              >
                👋 Welcome to AI Workspace
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: 'rgba(255, 255, 255, 0.9)',
                  maxWidth: '720px',
                  lineHeight: 1.6,
                  fontSize: '1.15rem'
                }}
              >
                Your all-in-one internal AI productivity platform. Use this workspace to securely generate official documents (like proposals and estimates), interact with company knowledge bases, and brainstorm ideas using our AI chat. Please ensure that you do not upload sensitive PII or unapproved client data.
              </Typography>
            </Box>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
              <Button
                variant="contained"
                onClick={() => navigate('/chat')}
                startIcon={<AutoAwesomeRounded />}
                sx={{
                  bgcolor: '#FFFFFF',
                  color: '#2563EB',
                  px: 3.5,
                  py: 1.5,
                  fontSize: '0.95rem',
                  fontWeight: 700,
                  '&:hover': {
                    bgcolor: 'rgba(255, 255, 255, 0.95)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                  }
                }}
              >
                Start AI Chat
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {/* 2. What You Can Do Section */}
      <Box>
        <Typography
          variant="h5"
          fontWeight={800}
          sx={{
            fontFamily: 'Outfit',
            letterSpacing: '-0.01em',
            display: 'flex',
            alignItems: 'center',
            gap: 1.25,
            mb: 3
          }}
        >
          ✨ What You Can Do
        </Typography>
        <Grid container spacing={3}>
          {[
            {
              title: 'Generate Documents',
              desc: 'Create PDF, Word and Excel files using AI.',
              icon: DescriptionOutlined,
              color: '#3B82F6',
              bg: '#EFF6FF',
              action: () => navigate('/files')
            },
            {
              title: 'AI Chat',
              desc: 'Ask questions, brainstorm ideas and get instant answers.',
              icon: ForumOutlined,
              color: '#8B5CF6',
              bg: '#F5F3FF',
              action: () => navigate('/chat')
            },
            {
              title: 'Knowledge Assistant',
              desc: 'Upload PDFs, DOCX and TXT files and chat with them.',
              icon: StarBorderRounded,
              color: '#EC4899',
              bg: '#FDF2F8',
              action: () => setAssistantOpen(true)
            },
            {
              title: 'Estimate Generator',
              desc: 'Create professional 2-page commercial event estimates.',
              icon: RequestQuoteRounded,
              color: '#F59E0B',
              bg: '#FEF3C7',
              action: () => navigate('/estimate')
            },
            {
              title: 'File Management',
              desc: 'Download and manage all AI-generated documents.',
              icon: FolderOpenRounded,
              color: '#10B981',
              bg: '#ECFDF5',
              action: () => navigate('/files')
            }
          ].map((item) => {
            const IconComponent = item.icon
            return (
              <Grid item xs={12} md={6} key={item.title}>
                <Card
                  onClick={item.action}
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-6px)',
                      boxShadow: '0px 12px 30px rgba(0, 0, 0, 0.08)',
                      borderColor: item.color
                    }
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 3,
                        bgcolor: item.bg,
                        color: item.color,
                        display: 'grid',
                        placeItems: 'center',
                        mb: 2.25
                      }}
                    >
                      <IconComponent sx={{ fontSize: 24 }} />
                    </Box>
                    <Typography
                      variant="subtitle1"
                      fontWeight={700}
                      sx={{ fontFamily: 'Outfit', mb: 1, color: '#1F2937' }}
                    >
                      {item.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ lineHeight: 1.5 }}
                    >
                      {item.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )
          })}
        </Grid>
      </Box>

      {/* 4. Footer Version info */}
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography
          variant="body2"
          color="text.disabled"
          fontWeight={500}
          sx={{ letterSpacing: '0.05em' }}
        >
          AI Workspace v1.0
        </Typography>
      </Box>

      {/* Knowledge Assistant Dialog */}
      <Dialog
        open={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        fullWidth
        maxWidth="md"
        PaperProps={{
          sx: { borderRadius: 4, p: 1 }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pb: 1 }}>
          <Box>
            <Typography variant="h6" fontWeight={800} sx={{ fontFamily: 'Outfit' }}>
              Knowledge Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Upload documents and ask questions using AI.
            </Typography>
          </Box>
          <IconButton onClick={() => setAssistantOpen(false)}>
            <CloseRounded />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers sx={{ py: 3 }}>
          <Box
            onDragOver={(event) => {
              event.preventDefault()
              setDragActive(true)
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            sx={{
              border: `2px dashed ${dragActive ? '#2563EB' : '#D7E3F2'}`,
              borderRadius: 3,
              bgcolor: dragActive ? '#F4F9FF' : '#FCFDFF',
              p: 3,
              textAlign: 'center',
              transition: 'all 0.2s ease',
              mb: 3
            }}
          >
            <CloudUploadRounded sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography fontWeight={700} mb={0.4}>
              Drag and drop files here
            </Typography>
            <Typography color="text.secondary" fontSize={13} mb={2}>
              PDF • DOCX • TXT • XLSX • CSV
            </Typography>
            <Button component="label" variant="outlined" size="small">
              Browse Files
              <input hidden accept=".pdf,.docx,.txt,.csv,.xlsx,.xls" multiple type="file" onChange={handleFileChange} ref={fileInputRef} />
            </Button>
            {user?.is_admin && (
              <Box mt={2}>
                <FormControlLabel
                  control={<Checkbox size="small" checked={isGlobal} onChange={(e) => setIsGlobal(e.target.checked)} />}
                  label={<Typography fontSize={13}>Make available to all employees (Company Document)</Typography>}
                />
              </Box>
            )}
          </Box>

          <Typography fontWeight={700} mb={1.5} fontSize={14}>
            Uploaded Documents
          </Typography>
          <Stack spacing={1.25} sx={{ mb: 3, maxHeight: '200px', overflowY: 'auto' }}>
            {documents.length === 0 ? (
              <Typography color="text.secondary" fontSize={13} textAlign="center" py={2}>
                No documents uploaded yet.
              </Typography>
            ) : (
              documents.map((document) => (
                <Box key={document.name} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid #E7ECF3', borderRadius: 2.5, px: 2, py: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Box sx={{ width: 36, height: 36, borderRadius: 2, bgcolor: '#F4F7FB', display: 'grid', placeItems: 'center', color: 'primary.main' }}>
                      <DescriptionOutlined fontSize="small" />
                    </Box>
                    <Box>
                      <Typography fontWeight={700} fontSize={13.5}>{document.name}</Typography>
                      <Typography color="text.secondary" fontSize={11}>{document.kind} • {document.size}</Typography>
                    </Box>
                  </Box>
                  <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
                    <Chip label="Ready" size="small" color="success" variant="outlined" sx={{ height: 20, fontSize: 10 }} />
                    <IconButton size="small" onClick={() => removeDocument(document.name)}>
                      <DeleteOutlineRounded fontSize="small" />
                    </IconButton>
                  </Stack>
                </Box>
              ))
            )}
          </Stack>

          <TextField
            fullWidth
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask something about your uploaded documents..."
            size="small"
          />
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25} sx={{ alignItems: { xs: 'stretch', sm: 'center' }, justifyContent: 'space-between', mt: 2 }}>
            <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
              {['Summarize this document', 'What is the leave policy?', 'Explain the architecture'].map((item) => (
                <Chip
                  key={item}
                  label={item}
                  variant="outlined"
                  size="small"
                  onClick={() => setQuestion(item)}
                  clickable
                  sx={{ fontSize: 11 }}
                />
              ))}
            </Stack>
            <Button variant="contained" size="small" sx={{ alignSelf: { xs: 'stretch', sm: 'auto' } }}>
              Ask
            </Button>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setAssistantOpen(false)} variant="outlined" size="small">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
