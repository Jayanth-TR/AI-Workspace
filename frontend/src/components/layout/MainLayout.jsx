import { DescriptionOutlined, ForumOutlined, HomeRounded, SettingsOutlined } from '@mui/icons-material'
import { BottomNavigation, BottomNavigationAction, Box, Paper } from '@mui/material'
import { useLocation, useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
export default function MainLayout({ children }) {
  const location = useLocation(); const navigate = useNavigate()
  return <Box sx={{ height: '100vh', display: 'flex', bgcolor: '#f6f8fc', overflow: 'hidden' }}><Sidebar />
    <Box component="main" sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', bgcolor: '#f6f8fc', height: '100vh', overflow: 'hidden' }}><Topbar />
      <Box sx={{ maxWidth: 1380, mx: 'auto', px: { xs: 2, md: 4 }, pt: 3, flex: 1, minHeight: 0, width: '100%', overflowY: 'auto', overflowX: 'hidden' }}>{children}</Box>
    </Box><Paper elevation={8} sx={{ display: { xs: 'block', md: 'none' }, position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 10 }}><BottomNavigation showLabels value={location.pathname} onChange={(_, value) => navigate(value)}><BottomNavigationAction value="/" label="Home" icon={<HomeRounded />} /><BottomNavigationAction value="/chat" label="Chat" icon={<ForumOutlined />} /><BottomNavigationAction value="/files" label="Files" icon={<DescriptionOutlined />} /><BottomNavigationAction value="/settings" label="Settings" icon={<SettingsOutlined />} /></BottomNavigation></Paper></Box>
}
