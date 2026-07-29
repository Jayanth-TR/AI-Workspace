import { AutoAwesomeRounded, DescriptionOutlined, HomeRounded, LogoutRounded, SettingsOutlined, StarBorderRounded } from '@mui/icons-material'
import { Box, Button, Divider, List, ListItemButton, ListItemIcon, ListItemText, Typography } from '@mui/material'
import { NavLink, useNavigate } from 'react-router-dom'
import useAuth from '../../hooks/useAuth'

const items = [
  { to: '/', label: 'Overview', icon: HomeRounded },
  { to: '/chat', label: 'AI Chat', icon: AutoAwesomeRounded },
  { to: '/files', label: 'My Files', icon: DescriptionOutlined },
  { to: '/knowledge', label: 'Knowledge Assistant', icon: StarBorderRounded },
  { to: '/settings', label: 'Settings', icon: SettingsOutlined }
]

export default function Sidebar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  return (
    <Box component="aside" sx={{ width: 248, flexShrink: 0, borderRight: '1px solid #e7ebf2', bgcolor: '#fff', minHeight: '100vh', display: { xs: 'none', md: 'flex' }, flexDirection: 'column', p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, px: 1, pb: 4 }}>
        <Box sx={{ width: 36, height: 36, display: 'grid', placeItems: 'center', borderRadius: 2.5, color: '#fff', bgcolor: '#2563EB' }}>
          <AutoAwesomeRounded fontSize="small" />
        </Box>
        <Typography variant="h6" sx={{ fontFamily: 'Outfit', fontWeight: 700 }}>AI Workspace</Typography>
      </Box>

      <Button onClick={() => navigate('/chat')} variant="contained" startIcon={<AutoAwesomeRounded />} sx={{ mb: 2, py: 1.2 }}>
        New Conversation
      </Button>

      <List disablePadding>
        {items.map(({ to, label, icon: Icon }) => (
          <ListItemButton
            key={label}
            component={NavLink}
            to={to}
            end={to === '/'}
            sx={{ my: 0.5, borderRadius: 2, '&.active': { bgcolor: '#eaf0ff', color: '#2455d9', '& .MuiListItemIcon-root': { color: '#2455d9' } } }}
          >
            <ListItemIcon sx={{ minWidth: 38, color: '#72809a' }}>
              <Icon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary={label} slotProps={{ primary: { sx: { fontWeight: 600, fontSize: 14 } } }} />
          </ListItemButton>
        ))}
      </List>

      <Box sx={{ mt: 'auto' }}>
        <Divider sx={{ mb: 1.5 }} />
        <ListItemButton onClick={() => { logout(); navigate('/login') }} sx={{ borderRadius: 2, color: '#63708a' }}>
          <ListItemIcon sx={{ minWidth: 38, color: 'inherit' }}>
            <LogoutRounded fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Sign out" slotProps={{ primary: { sx: { fontWeight: 600, fontSize: 14 } } }} />
        </ListItemButton>
      </Box>
    </Box>
  )
}