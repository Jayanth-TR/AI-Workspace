import React from 'react'

export default function SearchResultCard({ data }) {
  const { title, summary, keyFacts = [], details, sources = [] } = data

  return (
    <div
      style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)',
        maxWidth: '100%',
        fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
        color: '#1e293b',
      }}
    >
      {/* Header Badge & Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <span
          style={{
            background: 'linear-gradient(135deg, #2563eb, #3b82f6)',
            color: '#ffffff',
            fontSize: '11px',
            fontWeight: '700',
            padding: '3px 10px',
            borderRadius: '20px',
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          🌐 Web Search Result
        </span>
      </div>

      {title && (
        <h3
          style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#0f172a',
            margin: '0 0 14px 0',
            lineHeight: '1.4',
          }}
        >
          {title}
        </h3>
      )}

      {/* Summary Box */}
      {summary && (
        <div
          style={{
            background: '#f8fafc',
            borderLeft: '4px solid #3b82f6',
            padding: '12px 16px',
            borderRadius: '0 10px 10px 0',
            fontSize: '14px',
            lineHeight: '1.6',
            color: '#334155',
            marginBottom: '18px',
          }}
        >
          <strong style={{ color: '#1e293b', display: 'block', marginBottom: '4px', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Summary
          </strong>
          {summary}
        </div>
      )}

      {/* Key Facts Grid */}
      {Array.isArray(keyFacts) && keyFacts.length > 0 && (
        <div style={{ marginBottom: '18px' }}>
          <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', margin: '0 0 10px 0' }}>
            Key Facts
          </h4>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '10px',
            }}
          >
            {keyFacts.map((fact, idx) => (
              <div
                key={idx}
                style={{
                  background: '#f1f5f9',
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '10px 14px',
                }}
              >
                <div style={{ fontSize: '12px', fontWeight: '700', color: '#2563eb', marginBottom: '2px' }}>
                  {fact.label || 'Fact'}
                </div>
                <div style={{ fontSize: '13px', fontWeight: '500', color: '#1e293b', lineHeight: '1.4' }}>
                  {fact.value || ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extended Details */}
      {details && (
        <div style={{ marginBottom: '18px' }}>
          <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', margin: '0 0 8px 0' }}>
            Detailed Analysis
          </h4>
          <p style={{ fontSize: '14px', lineHeight: '1.65', color: '#334155', margin: '0', whiteSpace: 'pre-wrap' }}>
            {details}
          </p>
        </div>
      )}

      {/* Sources Links */}
      {Array.isArray(sources) && sources.length > 0 && (
        <div style={{ borderTop: '1px solid #f1f5f9', pt: '14px', marginTop: '16px', paddingTop: '14px' }}>
          <h4 style={{ fontSize: '12px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', margin: '0 0 10px 0' }}>
            Sources & References
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {sources.map((src, idx) => {
              if (!src.url) return null
              let domain = ''
              try {
                domain = new URL(src.url).hostname.replace('www.', '')
              } catch (e) {
                domain = src.url
              }

              return (
                <a
                  key={idx}
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    background: '#f8fafc',
                    border: '1px solid #cbd5e1',
                    borderRadius: '20px',
                    padding: '5px 12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#2563eb',
                    textDecoration: 'none',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#eff6ff'
                    e.currentTarget.style.borderColor = '#93c5fd'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#f8fafc'
                    e.currentTarget.style.borderColor = '#cbd5e1'
                  }}
                >
                  <span>🔗</span>
                  <span>{src.title || domain}</span>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>({domain})</span>
                </a>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
