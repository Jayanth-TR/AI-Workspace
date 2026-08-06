import React, { useState, useRef } from 'react';
import { enhanceEventImage } from '../services/imageService';
import {
  AutoAwesomeRounded,
  CloudUploadOutlined,
  DownloadRounded,
  RestartAltRounded
} from '@mui/icons-material';
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Typography,
  Alert,
  Divider
} from '@mui/material';

export default function EventImageEnhancer() {
    const [originalImage, setOriginalImage] = useState(null);
    const [originalImageFile, setOriginalImageFile] = useState(null);
    const [enhancedImage, setEnhancedImage] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        processSelectedFile(file);
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        processSelectedFile(file);
    };

    const processSelectedFile = (file) => {
        if (file && file.type.startsWith('image/')) {
            setError(null);
            setOriginalImageFile(file);
            setOriginalImage(URL.createObjectURL(file));
            setEnhancedImage(null); // Reset previous enhancement
        } else {
            setError('Please select a valid image file.');
        }
    };

    const handleEnhanceClick = async () => {
        if (!originalImageFile) return;

        setIsLoading(true);
        setError(null);

        try {
            const resultBlob = await enhanceEventImage(originalImageFile);
            setEnhancedImage(URL.createObjectURL(resultBlob));
        } catch (err) {
            console.error("Enhancement failed:", err);
            setError('Failed to enhance image. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleReset = () => {
        setOriginalImage(null);
        setOriginalImageFile(null);
        setEnhancedImage(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const downloadEnhancedImage = () => {
        if (!enhancedImage) return;
        const link = document.createElement('a');
        link.href = enhancedImage;
        link.download = 'enhanced_event_photo.jpg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2.5 }}>
            {/* Header */}
            <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, mb: 0.5 }}>
                    <Box sx={{ width: 34, height: 34, borderRadius: 2, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'grid', placeItems: 'center' }}>
                        <AutoAwesomeRounded sx={{ color: '#fff', fontSize: 20 }} />
                    </Box>
                    <Typography variant="h5" sx={{ fontFamily: 'Outfit', fontWeight: 700, color: '#0f172a' }}>
                        Premium Image Enhancer
                    </Typography>
                </Box>
                <Typography sx={{ fontSize: 13.5, color: '#64748b', ml: 5.7 }}>
                    Upload your event photograph to intelligently enhance sharpness, lighting, and colors while perfectly preserving authenticity.
                </Typography>
            </Box>

            <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', gap: 2 }}>
                {!originalImage && (
                    <Paper
                        variant="outlined"
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current.click()}
                        sx={{
                            border: isDragging ? '2px dashed #6366f1' : '2px dashed #cbd5e1',
                            borderRadius: 3,
                            p: 6,
                            textAlign: 'center',
                            cursor: 'pointer',
                            background: isDragging ? '#f5f3ff' : '#fafbff',
                            transition: 'all 0.18s ease',
                            '&:hover': { borderColor: '#818cf8', background: '#f5f3ff' }
                        }}
                    >
                        <CloudUploadOutlined sx={{ fontSize: 48, color: isDragging ? '#6366f1' : '#94a3b8', mb: 2 }} />
                        <Typography sx={{ fontWeight: 600, fontSize: 16, color: '#334155' }}>
                            {isDragging ? 'Drop photo here' : 'Drag & Drop your photo here'}
                        </Typography>
                        <Typography sx={{ fontSize: 13, color: '#94a3b8', mt: 1 }}>
                            or click to browse from your computer
                        </Typography>
                        <input
                            type="file"
                            style={{ display: 'none' }}
                            ref={fileInputRef}
                            accept="image/*"
                            onChange={handleFileSelect}
                        />
                    </Paper>
                )}

                {error && (
                    <Alert severity="error" sx={{ borderRadius: 2 }}>{error}</Alert>
                )}

                {originalImage && isLoading && (
                    <Paper variant="outlined" sx={{ borderRadius: 3, p: 6, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, background: '#f8fafc' }}>
                        <CircularProgress size={40} sx={{ color: '#6366f1' }} />
                        <Typography sx={{ fontWeight: 600, color: '#475569' }}>Applying Premium Enhancements...</Typography>
                    </Paper>
                )}

                {originalImage && !isLoading && (
                    <Paper variant="outlined" sx={{ borderRadius: 3, p: 3, background: '#f8fafc', display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: enhancedImage ? '1fr 1fr' : '1fr' }, gap: 3 }}>
                            <Box>
                                <Typography sx={{ fontSize: 13, fontWeight: 700, color: '#475569', mb: 1, textTransform: 'uppercase', letterSpacing: 0.5 }}>Original</Typography>
                                <Box component="img" src={originalImage} alt="Original Event" sx={{ width: '100%', borderRadius: 2, border: '1px solid #e2e8f0', display: 'block', maxHeight: '500px', objectFit: 'contain', backgroundColor: '#fff' }} />
                            </Box>
                            {enhancedImage && (
                                <Box>
                                    <Typography sx={{ fontSize: 13, fontWeight: 700, color: '#10b981', mb: 1, textTransform: 'uppercase', letterSpacing: 0.5 }}>Enhanced (Ready for PPT)</Typography>
                                    <Box component="img" src={enhancedImage} alt="Enhanced Event" sx={{ width: '100%', borderRadius: 2, border: '2px solid #10b981', display: 'block', maxHeight: '500px', objectFit: 'contain', backgroundColor: '#fff' }} />
                                </Box>
                            )}
                        </Box>
                        
                        <Divider />
                        
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                            {!enhancedImage ? (
                                <>
                                    <Button variant="outlined" color="inherit" onClick={handleReset} sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600, color: '#475569', borderColor: '#cbd5e1' }}>Cancel</Button>
                                    <Button variant="contained" onClick={handleEnhanceClick} sx={{ borderRadius: 2, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', textTransform: 'none', fontWeight: 600, boxShadow: 'none', '&:hover': { boxShadow: '0 4px 12px rgba(99,102,241,0.2)' } }}>Enhance Image</Button>
                                </>
                            ) : (
                                <>
                                    <Button variant="outlined" color="inherit" startIcon={<RestartAltRounded />} onClick={handleReset} sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600, color: '#475569', borderColor: '#cbd5e1' }}>Enhance Another</Button>
                                    <Button variant="contained" startIcon={<DownloadRounded />} onClick={downloadEnhancedImage} sx={{ borderRadius: 2, background: 'linear-gradient(135deg,#10b981,#059669)', textTransform: 'none', fontWeight: 600, boxShadow: 'none', '&:hover': { boxShadow: '0 4px 12px rgba(16,185,129,0.2)' } }}>Download for Presentation</Button>
                                </>
                            )}
                        </Box>
                    </Paper>
                )}
            </Box>
        </Box>
    );
}
