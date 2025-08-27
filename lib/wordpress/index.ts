// WordPress Integration - Main Export File

import { WordPressAPIClient } from './client'
import { WordPressProvisioningService } from './provisioning'
import { WordPressHealthCheckService } from './health-check'
import { WordPressThemeManager } from './theme-manager'
import { WordPressPluginManager } from './plugin-manager'
import { WordPressBackupManager } from './backup-manager'
import { WordPressSyncManager } from './sync-manager'

export { WordPressAPIClient } from './client'
export { WordPressProvisioningService } from './provisioning'
export { WordPressHealthCheckService } from './health-check'
export { WordPressThemeManager } from './theme-manager'
export { WordPressPluginManager } from './plugin-manager'
export { WordPressBackupManager } from './backup-manager'
export { WordPressSyncManager } from './sync-manager'

import type {
  WPSiteConfig,
  WPSiteInfo,
  WPUser,
  WPPost,
  WPPage,
  WPTheme,
  WPPlugin,
  WPCategory,
  WPTag,
  WPMedia,
  WPComment,
  WPSettings,
  WPAPIResponse,
  WPAPIError,
  WPQueryParams,
  WPBackup,
  WPHealthCheck,
  WPProvisioningRequest,
  WPProvisioningResponse,
} from './types'

export type {
  // Core Types
  WPSiteConfig,
  WPSiteInfo,
  WPUser,
  WPPost,
  WPPage,
  WPTheme,
  WPPlugin,
  WPCategory,
  WPTag,
  WPMedia,
  WPComment,
  WPSettings,
  WPAPIResponse,
  WPAPIError,
  WPQueryParams,
  WPBackup,
  WPHealthCheck,
  WPProvisioningRequest,
  WPProvisioningResponse,
} from './types'

import type {
  ThemeManagerConfig,
  ThemeMetadata,
  ThemePreview,
} from './theme-manager'

import type {
  PluginManagerConfig,
  PluginMetadata,
} from './plugin-manager'

import type {
  BackupManagerConfig,
  BackupSchedule,
  BackupStatistics,
  RestorePoint,
} from './backup-manager'

import type {
  SyncManagerConfig,
  SyncStatus,
  SyncConflict,
  SyncMapping,
  SyncLog,
  SyncType,
} from './sync-manager'

export type {
  ThemeManagerConfig,
  ThemeMetadata,
  ThemePreview,
} from './theme-manager'

export type {
  PluginManagerConfig,
  PluginMetadata,
} from './plugin-manager'

export type {
  BackupManagerConfig,
  BackupSchedule,
  BackupStatistics,
  RestorePoint,
} from './backup-manager'

export type {
  SyncManagerConfig,
  SyncStatus,
  SyncConflict,
  SyncMapping,
  SyncLog,
  SyncType,
} from './sync-manager'

// WordPress Integration Factory
export class WordPressIntegration {
  public client: WordPressAPIClient
  public provisioning: WordPressProvisioningService
  public healthCheck: WordPressHealthCheckService
  public themeManager: WordPressThemeManager
  public pluginManager: WordPressPluginManager
  public backupManager: WordPressBackupManager
  public syncManager: WordPressSyncManager

  constructor(config: {
    siteConfig: WPSiteConfig
    siteId: number
    storageProvider?: 'local' | 'aws' | 'google' | 'dropbox'
    storageConfig?: any
    syncInterval?: number
    enabledSyncTypes?: SyncType[]
  }) {
    // Initialize API client
    this.client = new WordPressAPIClient(config.siteConfig)

    // Initialize provisioning service
    this.provisioning = new WordPressProvisioningService()

    // Initialize health check service
    this.healthCheck = new WordPressHealthCheckService(this.client)

    // Initialize theme manager
    this.themeManager = new WordPressThemeManager({
      client: this.client
    })

    // Initialize plugin manager
    this.pluginManager = new WordPressPluginManager({
      client: this.client
    })

    // Initialize backup manager
    this.backupManager = new WordPressBackupManager({
      client: this.client,
      storageProvider: config.storageProvider,
      storageConfig: config.storageConfig
    })

    // Initialize sync manager
    this.syncManager = new WordPressSyncManager({
      client: this.client,
      siteId: config.siteId,
      syncInterval: config.syncInterval,
      enabledSyncTypes: config.enabledSyncTypes
    })
  }

  /**
   * Test all connections and return status
   */
  async testConnections(): Promise<{
    api: boolean
    storage: boolean
    overall: boolean
    details: Record<string, any>
  }> {
    const results = {
      api: false,
      storage: false,
      overall: false,
      details: {} as Record<string, any>
    }

    try {
      // Test API connection
      results.api = await this.client.testConnection()
      results.details.api = results.api ? 'Connected' : 'Failed to connect'

      // Test storage connection
      const storageTest = await this.backupManager.testStorageConnection()
      results.storage = storageTest.success
      results.details.storage = storageTest.message

      results.overall = results.api && results.storage
      
      return results
    } catch (error) {
      results.details.error = error instanceof Error ? error.message : 'Unknown error'
      return results
    }
  }

  /**
   * Get comprehensive site overview
   */
  async getSiteOverview(): Promise<{
    info: WPSiteInfo
    health: WPHealthCheck
    backupStats: BackupStatistics
    syncStatuses: Record<SyncType, SyncStatus>
    activePlugins: number
    activeTheme: WPTheme | null
  }> {
    const [
      info,
      health,
      backupStats,
      syncStatuses,
      plugins,
      activeTheme
    ] = await Promise.allSettled([
      this.client.getSiteInfo(),
      this.healthCheck.performHealthCheck(),
      this.backupManager.getBackupStatistics(),
      this.syncManager.getSyncStatuses(),
      this.pluginManager.getActivePlugins(),
      this.themeManager.getActiveTheme()
    ])

    return {
      info: info.status === 'fulfilled' ? info.value : {} as WPSiteInfo,
      health: health.status === 'fulfilled' ? health.value : {} as WPHealthCheck,
      backupStats: backupStats.status === 'fulfilled' ? backupStats.value : {} as BackupStatistics,
      syncStatuses: syncStatuses.status === 'fulfilled' ? syncStatuses.value : {} as Record<SyncType, SyncStatus>,
      activePlugins: plugins.status === 'fulfilled' ? plugins.value.length : 0,
      activeTheme: activeTheme.status === 'fulfilled' ? activeTheme.value : null
    }
  }

  /**
   * Perform maintenance tasks
   */
  async performMaintenance(tasks: {
    healthCheck?: boolean
    backupCleanup?: boolean
    syncConflicts?: boolean
    updateCheck?: boolean
  } = {}): Promise<{
    success: boolean
    results: Record<string, any>
    errors: string[]
  }> {
    const results: Record<string, any> = {}
    const errors: string[] = []
    let overallSuccess = true

    try {
      // Health check
      if (tasks.healthCheck !== false) {
        try {
          results.healthCheck = await this.healthCheck.performHealthCheck()
        } catch (error) {
          errors.push(`Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
          overallSuccess = false
        }
      }

      // Backup cleanup
      if (tasks.backupCleanup) {
        try {
          results.backupCleanup = await this.backupManager.cleanupOldBackups()
        } catch (error) {
          errors.push(`Backup cleanup failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
          overallSuccess = false
        }
      }

      // Resolve sync conflicts
      if (tasks.syncConflicts) {
        try {
          const conflicts = this.syncManager.getSyncConflicts(false) // unresolved conflicts
          results.syncConflicts = { unresolvedCount: conflicts.length }
        } catch (error) {
          errors.push(`Sync conflict check failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
          overallSuccess = false
        }
      }

      // Check for updates
      if (tasks.updateCheck) {
        try {
          const pluginUpdates = await this.pluginManager.checkForUpdates()
          results.updateCheck = { 
            pluginUpdates: pluginUpdates.length,
            updates: pluginUpdates 
          }
        } catch (error) {
          errors.push(`Update check failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
          overallSuccess = false
        }
      }

      return {
        success: overallSuccess,
        results,
        errors
      }
    } catch (error) {
      return {
        success: false,
        results,
        errors: [...errors, error instanceof Error ? error.message : 'Unknown error']
      }
    }
  }

  /**
   * Quick setup for new WordPress site
   */
  async quickSetup(options: {
    installEssentialPlugins?: boolean
    enableBackups?: boolean
    startSync?: boolean
    performHealthCheck?: boolean
  } = {}): Promise<{
    success: boolean
    completedTasks: string[]
    failedTasks: string[]
    details: Record<string, any>
  }> {
    const completedTasks: string[] = []
    const failedTasks: string[] = []
    const details: Record<string, any> = {}

    // Install essential plugins
    if (options.installEssentialPlugins !== false) {
      try {
        const essentialPlugins = await this.pluginManager.getEssentialPlugins()
        const installPromises = essentialPlugins.slice(0, 3).map(plugin => 
          this.pluginManager.installPlugin(plugin.slug)
        )
        const results = await Promise.allSettled(installPromises)
        
        const successful = results.filter(r => r.status === 'fulfilled').length
        details.pluginInstallation = { successful, total: installPromises.length }
        
        if (successful > 0) {
          completedTasks.push('Essential plugins installed')
        } else {
          failedTasks.push('Essential plugins installation')
        }
      } catch (error) {
        failedTasks.push('Essential plugins installation')
        details.pluginInstallationError = error instanceof Error ? error.message : 'Unknown error'
      }
    }

    // Enable automatic backups
    if (options.enableBackups !== false) {
      try {
        const schedule = await this.backupManager.scheduleBackup({
          site_url: this.client['config'].url,
          frequency: 'daily',
          time: '02:00',
          type: 'full',
          retention: 30,
          enabled: true,
          next_run: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
        })
        
        if (schedule.success) {
          completedTasks.push('Automatic backups enabled')
          details.backupSchedule = schedule.scheduleId
        } else {
          failedTasks.push('Automatic backups setup')
          details.backupError = schedule.message
        }
      } catch (error) {
        failedTasks.push('Automatic backups setup')
        details.backupError = error instanceof Error ? error.message : 'Unknown error'
      }
    }

    // Start sync
    if (options.startSync !== false) {
      try {
        this.syncManager.startAutoSync()
        completedTasks.push('Automatic sync started')
      } catch (error) {
        failedTasks.push('Automatic sync setup')
        details.syncError = error instanceof Error ? error.message : 'Unknown error'
      }
    }

    // Perform initial health check
    if (options.performHealthCheck !== false) {
      try {
        const healthCheck = await this.healthCheck.performHealthCheck()
        completedTasks.push('Initial health check completed')
        details.healthCheck = healthCheck.status
      } catch (error) {
        failedTasks.push('Initial health check')
        details.healthCheckError = error instanceof Error ? error.message : 'Unknown error'
      }
    }

    return {
      success: failedTasks.length === 0,
      completedTasks,
      failedTasks,
      details
    }
  }

  /**
   * Cleanup and disconnect
   */
  async cleanup(): Promise<void> {
    // Stop auto sync
    this.syncManager.stopAutoSync()
    
    // Clear any pending operations
    this.syncManager.clearSyncLogs()
  }
}

// Utility function to create WordPress integration instance
export function createWordPressIntegration(config: {
  url: string
  username: string
  password?: string
  applicationPassword?: string
  authMethod?: 'basic' | 'application_password' | 'jwt'
  siteId: number
  storageProvider?: 'local' | 'aws' | 'google' | 'dropbox'
  storageConfig?: any
  syncInterval?: number
  enabledSyncTypes?: SyncType[]
}): WordPressIntegration {
  const siteConfig: WPSiteConfig = {
    url: config.url,
    username: config.username,
    password: config.password,
    applicationPassword: config.applicationPassword,
    authMethod: config.authMethod || 'application_password'
  }

  return new WordPressIntegration({
    siteConfig,
    siteId: config.siteId,
    storageProvider: config.storageProvider,
    storageConfig: config.storageConfig,
    syncInterval: config.syncInterval,
    enabledSyncTypes: config.enabledSyncTypes
  })
}