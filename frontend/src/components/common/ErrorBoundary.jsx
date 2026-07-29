import { Component } from 'react'
import { Alert, Box, Button, Typography } from '@mui/material'

export default class ErrorBoundary extends Component {
  state = { error: null }
  static getDerivedStateFromError(error) { return { error } }
  componentDidCatch(error) { console.error('Page render error:', error) }
  render() {
    if (!this.state.error) return this.props.children
    return <Box sx={{ maxWidth: 680, mx: 'auto', mt: 8 }}><Alert severity="error"><Typography fontWeight={700}>This page could not load.</Typography><Typography fontSize={14} mt={.5}>Refresh the page to try again. If it continues, check that the backend is running.</Typography><Typography component="code" sx={{ display: 'block', mt: 1.5, whiteSpace: 'normal', overflowWrap: 'anywhere', fontSize: 12 }}>{this.state.error.message}</Typography></Alert><Button onClick={() => this.setState({ error: null })} variant="contained" sx={{ mt: 2 }}>Try again</Button></Box>
  }
}
