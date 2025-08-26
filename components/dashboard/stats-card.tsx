"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/cn"
import { ReactNode } from "react"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  icon?: ReactNode
  description?: string
  change?: number
  changeType?: 'increase' | 'decrease' | 'neutral'
  className?: string
  loading?: boolean
}

export function StatsCard({
  title,
  value,
  icon,
  description,
  change,
  changeType = 'neutral',
  className,
  loading = false
}: StatsCardProps) {
  const getTrendIcon = () => {
    if (!change) return null
    
    if (changeType === 'increase') {
      return <TrendingUp className="w-4 h-4" />
    } else if (changeType === 'decrease') {
      return <TrendingDown className="w-4 h-4" />
    } else {
      return <Minus className="w-4 h-4" />
    }
  }

  const getTrendColor = () => {
    if (changeType === 'increase') return 'text-green-600 dark:text-green-400'
    if (changeType === 'decrease') return 'text-red-600 dark:text-red-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  if (loading) {
    return (
      <div className={cn("rounded-xl border bg-card text-card-foreground shadow", className)}>
        <div className="p-6 animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("rounded-xl border bg-card text-card-foreground shadow hover:shadow-lg transition-shadow", className)}
    >
      <div className="p-6">
        <div className="flex items-center justify-between space-x-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          {icon && (
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              {icon}
            </div>
          )}
        </div>
        <div className="mt-4">
          <h2 className="text-3xl font-bold tracking-tight">
            {loading ? (
              <span className="animate-pulse">...</span>
            ) : (
              value
            )}
          </h2>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
          {change !== undefined && (
            <div className={cn("flex items-center gap-1 mt-2", getTrendColor())}>
              {getTrendIcon()}
              <span className="text-sm font-medium">
                {change > 0 ? '+' : ''}{change}%
              </span>
              <span className="text-xs text-muted-foreground">vs último mês</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}