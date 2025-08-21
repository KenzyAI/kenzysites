'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity } from 'lucide-react'
import { useState, useEffect } from 'react'

interface ActivityItem {
  id: string
  type: 'site_created' | 'content_generated' | 'backup_completed' | 'user_registered'
  message: string
  time: string
  status: 'success' | 'warning' | 'info'
}

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'site_created',
    message: 'Site "E-commerce Fashion" criado com sucesso',
    time: 'Há 12 minutos',
    status: 'success',
  },
  {
    id: '2',
    type: 'content_generated',
    message: '8 posts de blog gerados com IA para "Tech Startup"',
    time: 'Há 45 minutos',
    status: 'info',
  },
  {
    id: '3',
    type: 'backup_completed',
    message: 'Backup automático concluído para 15 sites',
    time: 'Há 2 horas',
    status: 'success',
  },
  {
    id: '4',
    type: 'user_registered',
    message: 'Novo usuário "maria.silva@email.com" registrado',
    time: 'Há 3 horas',
    status: 'info',
  },
  {
    id: '5',
    type: 'site_created',
    message: 'Site "Consultoria Jurídica" criado',
    time: 'Há 5 horas',
    status: 'success',
  },
]

const statusColors = {
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  info: 'bg-blue-500',
}

export function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simular carregamento
    setTimeout(() => {
      setActivities(mockActivities)
      setLoading(false)
    }, 1000)
  }, [])

  if (loading) {
    return (
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Atividade Recente
          </CardTitle>
          <CardDescription>Suas últimas ações na plataforma</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-start space-x-4 animate-pulse">
                <div className="h-2 w-2 rounded-full bg-muted mt-2" />
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-1/4" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Atividade Recente
        </CardTitle>
        <CardDescription>Suas últimas ações na plataforma</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-4">
              <div className={`h-2 w-2 rounded-full mt-2 ${statusColors[activity.status]}`} />
              <div className="space-y-1 flex-1">
                <p className="text-sm font-medium leading-none">{activity.message}</p>
                <p className="text-xs text-muted-foreground">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
