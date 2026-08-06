import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Chip,
  Stack,
  CircularProgress,
  Paper,
  Alert,
  Snackbar,
  Stepper,
  Step,
  StepLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider
} from '@mui/material'
import {
  AutoAwesomeRounded,
  ContentCopyRounded,
  PictureAsPdfRounded,
  DescriptionRounded,
  ArrowForwardRounded,
  ArrowBackRounded,
  CheckCircleRounded,
  RestartAltRounded,
  AddCircleOutlineRounded,
  DeleteOutlineRounded,
  RequestQuoteRounded
} from '@mui/icons-material'
import { generateEstimate, exportEstimate, refineEstimate } from '../services/estimateService'

const WIZARD_STEPS = [
  'Estimate Header',
  'Line Items',
  'Export & Download'
]

export default function EstimateGenerator() {
  const [activeTab, setActiveTab] = useState(0) // 0: Guided Wizard, 1: Quick Prompt
  const [activeStep, setActiveStep] = useState(0)

  // Form State
  const [formData, setFormData] = useState({
    quote_no: 'BP/EST/' + new Date().getFullYear().toString().slice(-2) + '-' + (new Date().getFullYear() + 1).toString().slice(-2) + '/' + Math.floor(100 + Math.random() * 900),
    quote_date: new Date().toISOString().split('T')[0],
    event_date: '',
    client_name: '',
    company_name: '',
    address: '',
    gst_no: '',
    tax_type: 'IGST',
    tax_rate: 18.0,
    line_items: [
      { sl: 1, description: 'Stage & Trussing Production Setup', qty: 1, rate: 75000, amount: 75000 }
    ],
    company_knowledge_override: ''
  })

  const [quickPrompt, setQuickPrompt] = useState('')
  const [refineSession, setRefineSession] = useState(null)
  const [chatAnswer, setChatAnswer] = useState('')

  // Generation state
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [estimateData, setEstimateData] = useState(null)
  const [toast, setToast] = useState({ open: false, message: '', severity: 'info' })

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  // Line Item Management
  const handleLineItemChange = (index, field, value) => {
    setFormData((prev) => {
      const items = [...prev.line_items]
      const item = { ...items[index], [field]: value }
      if (field === 'qty' || field === 'rate') {
        const q = parseFloat(field === 'qty' ? value : item.qty) || 0
        const r = parseFloat(field === 'rate' ? value : item.rate) || 0
        item.amount = q * r
      }
      items[index] = item
      return { ...prev, line_items: items }
    })
  }

  const addLineItem = () => {
    setFormData((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        { sl: prev.line_items.length + 1, description: '', qty: 1, rate: 0, amount: 0 }
      ]
    }))
  }

  const removeLineItem = (index) => {
    if (formData.line_items.length <= 1) return
    setFormData((prev) => {
      const filtered = prev.line_items.filter((_, idx) => idx !== index)
      const renumbered = filtered.map((item, idx) => ({ ...item, sl: idx + 1 }))
      return { ...prev, line_items: renumbered }
    })
  }

  const handleNextStep = () => {
    if (activeStep < WIZARD_STEPS.length - 1) {
      setActiveStep((prev) => prev + 1)
    } else {
      handleGenerate()
    }
  }

  const handleBackStep = () => {
    if (activeStep > 0) {
      setActiveStep((prev) => prev - 1)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      if (activeTab === 1 && quickPrompt.trim()) {
        const res = await refineEstimate({ prompt: quickPrompt, history: [] })
        if (res.status === 'needs_info') {
          setRefineSession({
            prompt: quickPrompt,
            history: [
              { role: 'assistant', content: res.question }
            ]
          })
          setToast({ open: true, message: 'AI requires some clarification.', severity: 'info' })
        } else if (res.status === 'completed' && res.estimate) {
          setEstimateData(res.estimate)
          setToast({ open: true, message: 'Estimate generated successfully!', severity: 'success' })
        } else {
          setToast({ open: true, message: 'Failed to generate estimate.', severity: 'error' })
        }
      } else {
        const res = await generateEstimate({ ...formData })
        if (res.success && res.estimate) {
          setEstimateData(res.estimate)
          setToast({ open: true, message: 'Estimate generated successfully!', severity: 'success' })
        } else {
          setToast({ open: true, message: 'Failed to generate estimate.', severity: 'error' })
        }
      }
    } catch (err) {
      setToast({
        open: true,
        message: err?.response?.data?.detail || 'Error generating estimate.',
        severity: 'error'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSendAnswer = async (e) => {
    if (e) e.preventDefault()
    if (!chatAnswer.trim() || !refineSession) return

    const userMsg = { role: 'user', content: chatAnswer.trim() }
    const updatedHistory = [...refineSession.history, userMsg]

    setRefineSession((prev) => ({
      ...prev,
      history: updatedHistory
    }))
    setChatAnswer('')
    setLoading(true)

    try {
      const res = await refineEstimate({ prompt: refineSession.prompt, history: updatedHistory })
      if (res.status === 'needs_info') {
        setRefineSession((prev) => ({
          ...prev,
          history: [...updatedHistory, { role: 'assistant', content: res.question }]
        }))
      } else if (res.status === 'completed' && res.estimate) {
        setEstimateData(res.estimate)
        setRefineSession(null)
        setToast({ open: true, message: 'Estimate generated successfully!', severity: 'success' })
      } else {
        setToast({ open: true, message: 'AI returned an unexpected response.', severity: 'warning' })
      }
    } catch (err) {
      setToast({
        open: true,
        message: err?.response?.data?.detail || 'Error processing response.',
        severity: 'error'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format) => {
    if (!estimateData) return
    setExporting(true)
    try {
      const payload = {
        ...estimateData,
        format
      }
      await exportEstimate(payload)
      setToast({
        open: true,
        message: `Estimate exported successfully as ${format.toUpperCase()}!`,
        severity: 'success'
      })
    } catch (err) {
      setToast({
        open: true,
        message: err?.response?.data?.detail || `Failed to export ${format.toUpperCase()}.`,
        severity: 'error'
      })
    } finally {
      setExporting(false)
    }
  }

  const handleReset = () => {
    setEstimateData(null)
    setRefineSession(null)
    setActiveStep(0)
    setQuickPrompt('')
    setChatAnswer('')
  }

  const subtotal = formData.line_items.reduce((sum, item) => sum + (item.amount || 0), 0)
  const taxAmount = subtotal * (formData.tax_rate / 100)
  const total = subtotal + taxAmount

  return (
    <Box sx={{ maxWidth: 960, mx: 'auto', pb: 6, display: 'grid', gap: 3 }}>
      {/* Hero Banner */}
      <Card
        sx={{
          background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #2563EB 100%)',
          color: '#FFFFFF',
          border: 'none',
          boxShadow: '0px 10px 30px rgba(15, 23, 42, 0.3)',
          borderRadius: 3
        }}
      >

      </Card>

      {/* Main Container */}
      <Paper sx={{ p: { xs: 3, md: 4 }, borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        {/* Toggle between Guided Wizard and Quick Prompt */}
        {!estimateData && (
          <Box sx={{ display: 'flex', borderBottom: 1, borderColor: 'divider', mb: 4 }}>
            <Button
              onClick={() => setActiveTab(0)}
              sx={{
                flex: 1,
                py: 1.5,
                borderBottom: activeTab === 0 ? '3px solid #2563EB' : 'none',
                color: activeTab === 0 ? '#2563EB' : 'text.secondary',
                fontWeight: 700,
                borderRadius: 0
              }}
            >
              <AutoAwesomeRounded sx={{ mr: 1, fontSize: 20 }} /> Wizard Mode
            </Button>
            <Button
              onClick={() => setActiveTab(1)}
              sx={{
                flex: 1,
                py: 1.5,
                borderBottom: activeTab === 1 ? '3px solid #2563EB' : 'none',
                color: activeTab === 1 ? '#2563EB' : 'text.secondary',
                fontWeight: 700,
                borderRadius: 0
              }}
            >
              <RequestQuoteRounded sx={{ mr: 1, fontSize: 20 }} /> Quick Prompt Mode
            </Button>
          </Box>
        )}

        {/* Success / Download State */}
        {estimateData ? (
          <Box sx={{ textAlign: 'center', py: 4, px: 2 }}>
            <CheckCircleRounded sx={{ fontSize: 64, color: '#10B981', mb: 2 }} />
            <Typography variant="h5" sx={{ fontFamily: 'Outfit', fontWeight: 700, color: '#0f172a', mb: 1 }}>
              Estimate Generated Successfully!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, mx: 'auto', mb: 4 }}>
              Your formal 2-page estimate for <strong>{estimateData.company_name}</strong> is ready. Download in PDF or Word formats.
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
              <Button
                variant="contained"
                size="large"
                startIcon={exporting ? <CircularProgress size={20} color="inherit" /> : <PictureAsPdfRounded />}
                disabled={exporting}
                onClick={() => handleExport('pdf')}
                sx={{ py: 1.5, px: 4, fontWeight: 700, bgcolor: '#2563EB', '&:hover': { bgcolor: '#1D4ED8' } }}
              >
                Download PDF Estimate
              </Button>
            </Box>

            <Button
              startIcon={<RestartAltRounded />}
              onClick={handleReset}
              sx={{ color: '#64748B', fontWeight: 600 }}
            >
              Create Another Estimate
            </Button>
          </Box>
        ) : activeTab === 0 ? (
          /* Wizard Mode */
          <Box>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
              {WIZARD_STEPS.map((label) => (
                <Step key={label}>
                  <StepLabel
                    slotProps={{
                      label: { sx: { fontSize: '0.75rem', fontWeight: 600 } }
                    }}
                  >
                    {label}
                  </StepLabel>
                </Step>
              ))}
            </Stepper>

            {/* Step 0: Header Info */}
            {activeStep === 0 && (
              <Stack spacing={2.5}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e293b' }}>
                  Step 1: Estimate Details & Billing Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Quote / Estimate Number"
                      fullWidth
                      value={formData.quote_no}
                      onChange={(e) => handleInputChange('quote_no', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Quote Date"
                      type="date"
                      fullWidth
                      slotProps={{ inputLabel: { shrink: true } }}
                      value={formData.quote_date}
                      onChange={(e) => handleInputChange('quote_date', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Event Date"
                      type="date"
                      fullWidth
                      slotProps={{ inputLabel: { shrink: true } }}
                      value={formData.event_date}
                      onChange={(e) => handleInputChange('event_date', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Client Contact Name"
                      fullWidth
                      placeholder="e.g. Rahul Sharma"
                      value={formData.client_name}
                      onChange={(e) => handleInputChange('client_name', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Company Name"
                      fullWidth
                      placeholder="e.g. Nexus Global Innovations"
                      value={formData.company_name}
                      onChange={(e) => handleInputChange('company_name', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={8}>
                    <TextField
                      label="Billing Address"
                      fullWidth
                      multiline
                      rows={2}
                      placeholder="Full billing address details..."
                      value={formData.address}
                      onChange={(e) => handleInputChange('address', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Client GSTIN"
                      fullWidth
                      placeholder="e.g. 27AAQCA6935R1ZN"
                      value={formData.gst_no}
                      onChange={(e) => handleInputChange('gst_no', e.target.value)}
                    />
                  </Grid>
                </Grid>
              </Stack>
            )}

            {/* Step 1: Line Items */}
            {activeStep === 1 && (
              <Stack spacing={2.5}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e293b' }}>
                  Step 2: Line Items & Commercial Details
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                      <TableRow>
                        <TableCell width="6%">Sl.</TableCell>
                        <TableCell width="50%">Service/Product Description</TableCell>
                        <TableCell width="12%" align="right">Qty</TableCell>
                        <TableCell width="16%" align="right">Rate (₹)</TableCell>
                        <TableCell width="16%" align="right">Amount (₹)</TableCell>
                        <TableCell width="6%"></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {formData.line_items.map((item, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{item.sl}</TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              fullWidth
                              variant="standard"
                              placeholder="Describe service..."
                              value={item.description}
                              onChange={(e) => handleLineItemChange(idx, 'description', e.target.value)}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <TextField
                              size="small"
                              type="number"
                              variant="standard"
                              inputProps={{ style: { textAlign: 'right' } }}
                              value={item.qty}
                              onChange={(e) => handleLineItemChange(idx, 'qty', parseFloat(e.target.value) || 0)}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <TextField
                              size="small"
                              type="number"
                              variant="standard"
                              inputProps={{ style: { textAlign: 'right' } }}
                              value={item.rate}
                              onChange={(e) => handleLineItemChange(idx, 'rate', parseFloat(e.target.value) || 0)}
                            />
                          </TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600 }}>
                            ₹{(item.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </TableCell>
                          <TableCell align="center">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => removeLineItem(idx)}
                              disabled={formData.line_items.length <= 1}
                            >
                              <DeleteOutlineRounded fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                <Button
                  startIcon={<AddCircleOutlineRounded />}
                  onClick={addLineItem}
                  sx={{ alignSelf: 'flex-start', fontWeight: 600 }}
                >
                  Add Line Item
                </Button>

                <Divider sx={{ my: 1 }} />

                <Grid container spacing={2} justifyContent="flex-end">
                  <Grid item xs={12} sm={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Tax Type</InputLabel>
                      <Select
                        value={formData.tax_type}
                        label="Tax Type"
                        onChange={(e) => handleInputChange('tax_type', e.target.value)}
                      >
                        <MenuItem value="IGST">IGST (Inter-State)</MenuItem>
                        <MenuItem value="CGST+SGST">CGST + SGST (Intra-State)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Tax Rate (%)"
                      type="number"
                      size="small"
                      fullWidth
                      value={formData.tax_rate}
                      onChange={(e) => handleInputChange('tax_rate', parseFloat(e.target.value) || 0)}
                    />
                  </Grid>
                </Grid>

                <Box sx={{ alignSelf: 'flex-end', width: 300, textAlign: 'right', display: 'grid', gap: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Subtotal: <strong>₹{subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    GST ({formData.tax_rate}%): <strong>₹{taxAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#0F172A', fontWeight: 700 }}>
                    Total: ₹{total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </Typography>
                </Box>
              </Stack>
            )}

            {/* Step 2: Final Review & Generate */}
            {activeStep === 2 && (
              <Stack spacing={2.5}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e293b' }}>
                  Step 3: Review Details & Generate
                </Typography>
                <TextField
                  label="Company Knowledge / Past Requirements (Optional)"
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Custom terms, specific AV specs, or specific Beats Production company details..."
                  value={formData.company_knowledge_override}
                  onChange={(e) => handleInputChange('company_knowledge_override', e.target.value)}
                />
                <Box sx={{ bgcolor: '#F8FAFC', p: 3, borderRadius: 2, border: '1px solid #E2E8F0' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                    Summary of Quote:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Quote No: {formData.quote_no}<br />
                    • Client: {formData.client_name || '<Unspecified>'} ({formData.company_name})<br />
                    • Event Date: {formData.event_date || '<Unspecified>'}<br />
                    • Line Items Count: {formData.line_items.length}<br />
                    • Total: ₹{total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </Typography>
                </Box>
              </Stack>
            )}

            {/* Wizard Navigation Buttons */}
            <Stack direction="row" justifyContent="space-between" sx={{ mt: 5, pt: 2, borderTop: '1px solid #e2e8f0' }}>
              <Button
                disabled={activeStep === 0 || loading}
                onClick={handleBackStep}
                startIcon={<ArrowBackRounded />}
              >
                Back
              </Button>
              <Button
                variant="contained"
                disabled={loading}
                onClick={handleNextStep}
                endIcon={
                  loading ? (
                    <CircularProgress size={18} color="inherit" />
                  ) : activeStep === WIZARD_STEPS.length - 1 ? (
                    <AutoAwesomeRounded />
                  ) : (
                    <ArrowForwardRounded />
                  )
                }
                sx={{ py: 1.2, px: 4, fontWeight: 700 }}
              >
                {loading ? 'Generating Estimate...' : activeStep === WIZARD_STEPS.length - 1 ? 'Generate Estimate' : 'Next'}
              </Button>
            </Stack>
          </Box>
        ) : (
          /* Quick Prompt Mode */
          refineSession ? (
            <Stack spacing={3}>
              <Box sx={{ borderBottom: '1px solid #E2E8F0', pb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e293b' }}>
                    Refining Estimate Details
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Initial prompt: "{refineSession.prompt}"
                  </Typography>
                </Box>
                <Button size="small" color="error" onClick={handleReset} startIcon={<RestartAltRounded />}>
                  Start Over
                </Button>
              </Box>

              {/* Chat Messages */}
              <Box sx={{
                maxHeight: 400,
                overflowY: 'auto',
                p: 2,
                borderRadius: 2,
                bgcolor: '#F8FAFC',
                border: '1px solid #E2E8F0',
                display: 'flex',
                flexDirection: 'column',
                gap: 2
              }}>
                {refineSession.history.map((msg, index) => (
                  <Box
                    key={index}
                    sx={{
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '80%',
                      p: 2,
                      borderRadius: 2.5,
                      bgcolor: msg.role === 'user' ? '#2563EB' : '#FFFFFF',
                      color: msg.role === 'user' ? '#FFFFFF' : '#0F172A',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                      border: msg.role === 'user' ? 'none' : '1px solid #E2E8F0'
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: msg.role === 'assistant' ? 500 : 400 }}>
                      {msg.content}
                    </Typography>
                  </Box>
                ))}
              </Box>

              {/* Answer Input */}
              <form onSubmit={handleSendAnswer}>
                <Stack direction="row" spacing={1}>
                  <TextField
                    placeholder="Type your answer here..."
                    fullWidth
                    value={chatAnswer}
                    onChange={(e) => setChatAnswer(e.target.value)}
                    disabled={loading}
                    autoFocus
                    size="small"
                  />
                  <Button
                    variant="contained"
                    type="submit"
                    disabled={loading || !chatAnswer.trim()}
                    sx={{ px: 3, fontWeight: 700 }}
                  >
                    {loading ? <CircularProgress size={20} color="inherit" /> : 'Send'}
                  </Button>
                </Stack>
              </form>
            </Stack>
          ) : (
            <Stack spacing={3}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e293b' }}>
                Quick AI Estimate Prompt
              </Typography>
              <TextField
                label="Enter Event / Estimate Details"
                fullWidth
                multiline
                rows={8}
                placeholder="e.g. Generate an estimate for Rahul Sharma at Nexus Global for their Annual Excellence Awards on Nov 20, 2026. Quote number BP/EST/25-26/410. Line items: Stage & Trussing setup for ₹75,000, and LED Wall setup (qty 2) for ₹35,000 each. Apply 18% IGST."
                value={quickPrompt}
                onChange={(e) => setQuickPrompt(e.target.value)}
              />
              <Button
                variant="contained"
                fullWidth
                size="large"
                disabled={loading || !quickPrompt.trim()}
                onClick={handleGenerate}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AutoAwesomeRounded />}
                sx={{ py: 1.5, fontWeight: 700 }}
              >
                {loading ? 'Generating Estimate...' : 'Generate Estimate Now'}
              </Button>
            </Stack>
          )
        )}
      </Paper>

      <Snackbar
        open={toast.open}
        autoHideDuration={4000}
        onClose={() => setToast((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity={toast.severity} onClose={() => setToast((prev) => ({ ...prev, open: false }))}>
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}
