import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Box } from '@mui/material'

export default function FormattedMarkdown({ content }) {
  if (!content || typeof content !== 'string') return null

  return (
    <Box
      sx={{
        '& p': { my: 0.8, lineHeight: 1.65, fontSize: '0.925rem' },
        '& p:first-of-type': { mt: 0 },
        '& p:last-of-type': { mb: 0 },
        '& h1, & h2, & h3, & h4': {
          fontWeight: 700,
          color: '#0f172a',
          mt: 1.8,
          mb: 0.8,
          fontFamily: 'Outfit, sans-serif',
        },
        '& h1': { fontSize: '1.25rem', borderBottom: '2px solid #e2e8f0', pb: 0.5 },
        '& h2': { fontSize: '1.1rem', color: '#1e293b' },
        '& h3': { fontSize: '1rem', color: '#334155' },
        '& ul, & ol': { pl: 2.5, my: 1 },
        '& li': { my: 0.4, lineHeight: 1.6 },
        '& strong': { color: '#0f172a', fontWeight: 600 },
        '& code': {
          background: '#f1f5f9',
          color: '#4f46e5',
          px: 0.8,
          py: 0.2,
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '0.85em',
        },
        '& pre': {
          background: '#1e293b',
          color: '#f8fafc',
          p: 2,
          borderRadius: 2,
          overflowX: 'auto',
          my: 1.5,
          '& code': { background: 'transparent', color: 'inherit', p: 0 },
        },
        '& blockquote': {
          borderLeft: '4px solid #6366f1',
          pl: 2,
          ml: 0,
          my: 1.5,
          color: '#475569',
          fontStyle: 'italic',
        },
        '& hr': {
          borderColor: '#e2e8f0',
          my: 2,
        },
      }}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </Box>
  )
}
