import { DarkModeOutlined, NotificationsNoneRounded, SecurityOutlined } from '@mui/icons-material'
import { Card, CardContent, Divider, Stack, Switch, Typography } from '@mui/material'
import { useState } from 'react'
import PageHeader from '../components/common/PageHeader'

export default function Settings() {
  const [alerts, setAlerts] = useState(true)
  const [compact, setCompact] = useState(false)

  return (
    <>
      <PageHeader eyebrow="Preferences" title="Settings" description="Choose how your workspace feels and communicates." />
      <Card sx={{ maxWidth: 760 }}>
        <CardContent sx={{ p: 0 }}>
          <Setting icon={<NotificationsNoneRounded />} title="Workspace notifications" text="Receive updates about completed generations." control={<Switch checked={alerts} onChange={e => setAlerts(e.target.checked)} />} />
          <Divider />
          <Setting icon={<DarkModeOutlined />} title="Compact mode" text="Use denser spacing in future workspace updates." control={<Switch checked={compact} onChange={e => setCompact(e.target.checked)} />} />
          <Divider />
          <Setting icon={<SecurityOutlined />} title="Privacy" text="Your conversations and generated files stay in your workspace." />
        </CardContent>
      </Card>
    </>
  )
}

function Setting({ icon, title, text, control }) {
  return (
    <Stack direction="row" sx={{ alignItems: 'center', gap: 2, p: 2.5 }}>
      <span style={{ color: '#3563e9', display: 'grid' }}>{icon}</span>
      <span style={{ flex: 1 }}>
        <Typography sx={{ fontWeight: 700 }}>{title}</Typography>
        <Typography color="text.secondary" sx={{ fontSize: 13, mt: 0.35 }}>{text}</Typography>
      </span>
      {control}
    </Stack>
  )
}
