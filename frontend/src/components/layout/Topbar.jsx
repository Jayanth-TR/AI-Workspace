import { MenuRounded, NotificationsNoneRounded } from '@mui/icons-material'
import { Avatar, Box, Chip, IconButton, Typography } from '@mui/material'
import { useLocation, useNavigate } from 'react-router-dom'
import useAuth from '../../hooks/useAuth'

const labels = { '/': 'Overview', '/chat': 'AI chat', '/files': 'My files', '/profile': 'Profile', '/settings': 'Settings', '/knowledge': 'Knowledge Assistant' }

export default function Topbar() {
  const { user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const initials = (user?.name || 'U').split(' ').map((x) => x[0]).join('').slice(0, 2).toUpperCase()

  return (
    <Box component="header" sx={{ height: 76, display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: { xs: 2, md: 4 }, borderBottom: '1px solid #e7ebf2', bgcolor: 'rgba(255,255,255,.82)', backdropFilter: 'blur(10px)', position: 'sticky', top: 0, zIndex: 5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <IconButton sx={{ display: { md: 'none' } }}>
          <MenuRounded />
        </IconButton>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.1 }}>{labels[location.pathname] || 'AI Workspace'}</Typography>
          <Typography color="text.secondary" sx={{ fontSize: 12 }}>AI Workspace</Typography>
        </Box>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
        <Chip label="Live workspace" size="small" color="primary" variant="outlined" sx={{ display: { xs: 'none', sm: 'flex' } }} />
        <IconButton size="small">
          <NotificationsNoneRounded />
        </IconButton>
        <Box onClick={() => navigate('/profile')} sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 34, height: 34, bgcolor: '#e5ebff', color: '#315ce7', fontSize: 13, fontWeight: 700 }}>{initials}</Avatar>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Typography sx={{ fontSize: 13, fontWeight: 700, lineHeight: 1.2 }}>{user?.name || 'Workspace member'}</Typography>
            <Typography color="text.secondary" sx={{ fontSize: 11 }}>Personal workspace</Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}