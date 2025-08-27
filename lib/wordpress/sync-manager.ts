import { WordPressAPIClient } from './client'
import { Site } from '../hooks/use-sites'
import { WPPost, WPPage, WPUser, WPSettings, WPPlugin, WPTheme } from './types'

export interface SyncManagerConfig {
  client: WordPressAPIClient
  siteId: number
  syncInterval?: number // in minutes
  enabledSyncTypes?: SyncType[]
}

export type SyncType = 'posts' | 'pages' | 'users' | 'settings' | 'plugins' | 'themes' | 'media' | 'comments'

export interface SyncStatus {
  type: SyncType
  status: 'idle' | 'syncing' | 'completed' | 'failed'
  last_sync: string | null
  next_sync: string | null
  progress?: number
  error?: string
  items_synced?: number
  total_items?: number
}

export interface SyncConflict {
  id: string
  type: SyncType
  item_id: string | number
  local_data: any
  remote_data: any
  timestamp: string
  resolved: boolean
  resolution?: 'local' | 'remote' | 'merge'
}

export interface SyncMapping {
  local_id: string | number
  remote_id: string | number
  type: SyncType
  last_synced: string
  checksum: string
}

export interface SyncLog {
  id: string
  type: SyncType
  action: 'create' | 'update' | 'delete' | 'sync'
  direction: 'local_to_remote' | 'remote_to_local' | 'bidirectional'
  status: 'success' | 'failed' | 'conflict'
  timestamp: string
  details: {
    item_id?: string | number
    changes?: Record<string, any>
    error?: string
    conflict_id?: string
  }
}

export class WordPressSyncManager {
  private client: WordPressAPIClient
  private siteId: number
  private syncInterval: number
  private enabledSyncTypes: SyncType[]
  private syncStatuses: Map<SyncType, SyncStatus> = new Map()
  private mappings: Map<string, SyncMapping> = new Map()
  private conflicts: Map<string, SyncConflict> = new Map()
  private syncLogs: SyncLog[] = []
  private syncIntervalId?: NodeJS.Timeout

  constructor(config: SyncManagerConfig) {
    this.client = config.client
    this.siteId = config.siteId
    this.syncInterval = config.syncInterval || 30 // 30 minutes default
    this.enabledSyncTypes = config.enabledSyncTypes || [
      'posts', 'pages', 'users', 'settings', 'plugins', 'themes'
    ]

    this.initializeSyncStatuses()
  }

  /**
   * Start automatic synchronization
   */
  startAutoSync(): void {
    if (this.syncIntervalId) {
      this.stopAutoSync()
    }

    this.syncIntervalId = setInterval(() => {
      this.performFullSync()
    }, this.syncInterval * 60 * 1000)

    this.logSync('posts', 'bidirectional', 'success', 'Auto-sync started')
  }

  /**
   * Stop automatic synchronization
   */
  stopAutoSync(): void {
    if (this.syncIntervalId) {
      clearInterval(this.syncIntervalId)
      this.syncIntervalId = undefined
    }

    this.logSync('posts', 'bidirectional', 'success', 'Auto-sync stopped')
  }

  /**
   * Perform full sync of all enabled types
   */
  async performFullSync(): Promise<{ success: boolean; results: Record<SyncType, any> }> {
    const results: Record<SyncType, any> = {} as any

    for (const syncType of this.enabledSyncTypes) {
      try {
        results[syncType] = await this.syncByType(syncType)
      } catch (error) {
        results[syncType] = { 
          success: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }
      }
    }

    const success = Object.values(results).every(result => result.success !== false)
    return { success, results }
  }

  /**
   * Sync specific data type
   */
  async syncByType(type: SyncType): Promise<{ success: boolean; synced: number; conflicts: number; error?: string }> {
    const status = this.syncStatuses.get(type)
    if (!status) {
      return { success: false, synced: 0, conflicts: 0, error: 'Sync type not enabled' }
    }

    status.status = 'syncing'
    status.progress = 0
    this.syncStatuses.set(type, status)

    try {
      let result: { synced: number; conflicts: number }

      switch (type) {
        case 'posts':
          result = await this.syncPosts()
          break
        case 'pages':
          result = await this.syncPages()
          break
        case 'users':
          result = await this.syncUsers()
          break
        case 'settings':
          result = await this.syncSettings()
          break
        case 'plugins':
          result = await this.syncPlugins()
          break
        case 'themes':
          result = await this.syncThemes()
          break
        case 'media':
          result = await this.syncMedia()
          break
        case 'comments':
          result = await this.syncComments()
          break
        default:
          throw new Error(`Unsupported sync type: ${type}`)
      }

      status.status = 'completed'
      status.last_sync = new Date().toISOString()
      status.next_sync = new Date(Date.now() + this.syncInterval * 60 * 1000).toISOString()
      status.items_synced = result.synced
      status.progress = 100
      this.syncStatuses.set(type, status)

      this.logSync(type, 'bidirectional', 'success', `Synced ${result.synced} items`, {
        item_id: result.synced.toString(),
        changes: { conflicts: result.conflicts }
      })

      return { success: true, synced: result.synced, conflicts: result.conflicts }
    } catch (error) {
      status.status = 'failed'
      status.error = error instanceof Error ? error.message : 'Unknown error'
      this.syncStatuses.set(type, status)

      this.logSync(type, 'bidirectional', 'failed', 'Sync failed', {
        error: status.error
      })

      return { 
        success: false, 
        synced: 0, 
        conflicts: 0, 
        error: status.error 
      }
    }
  }

  /**
   * Get sync status for all types
   */
  getSyncStatuses(): Record<SyncType, SyncStatus> {
    const statuses: Record<SyncType, SyncStatus> = {} as any
    for (const [type, status] of this.syncStatuses) {
      statuses[type] = { ...status }
    }
    return statuses
  }

  /**
   * Get sync conflicts
   */
  getSyncConflicts(resolved?: boolean): SyncConflict[] {
    const conflicts = Array.from(this.conflicts.values())
    
    if (resolved !== undefined) {
      return conflicts.filter(conflict => conflict.resolved === resolved)
    }
    
    return conflicts
  }

  /**
   * Resolve sync conflict
   */
  async resolveSyncConflict(
    conflictId: string, 
    resolution: 'local' | 'remote' | 'merge'
  ): Promise<{ success: boolean; message?: string }> {
    const conflict = this.conflicts.get(conflictId)
    if (!conflict) {
      return { success: false, message: 'Conflict not found' }
    }

    try {
      switch (resolution) {
        case 'local':
          await this.pushLocalData(conflict.type, conflict.item_id, conflict.local_data)
          break
        case 'remote':
          await this.pullRemoteData(conflict.type, conflict.item_id, conflict.remote_data)
          break
        case 'merge':
          const mergedData = this.mergeConflictData(conflict.local_data, conflict.remote_data)
          await this.pushLocalData(conflict.type, conflict.item_id, mergedData)
          break
      }

      conflict.resolved = true
      conflict.resolution = resolution
      this.conflicts.set(conflictId, conflict)

      this.logSync(conflict.type, 'bidirectional', 'success', 'Conflict resolved', {
        conflict_id: conflictId,
        changes: { resolution }
      })

      return { success: true, message: 'Conflict resolved successfully' }
    } catch (error) {
      this.logSync(conflict.type, 'bidirectional', 'failed', 'Failed to resolve conflict', {
        conflict_id: conflictId,
        error: error instanceof Error ? error.message : 'Unknown error'
      })

      return { 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to resolve conflict' 
      }
    }
  }

  /**
   * Get sync logs
   */
  getSyncLogs(filters?: {
    type?: SyncType
    status?: 'success' | 'failed' | 'conflict'
    limit?: number
  }): SyncLog[] {
    let logs = [...this.syncLogs]

    if (filters?.type) {
      logs = logs.filter(log => log.type === filters.type)
    }
    if (filters?.status) {
      logs = logs.filter(log => log.status === filters.status)
    }

    // Sort by timestamp (newest first)
    logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

    if (filters?.limit) {
      logs = logs.slice(0, filters.limit)
    }

    return logs
  }

  /**
   * Force sync specific item
   */
  async forceSyncItem(
    type: SyncType, 
    itemId: string | number, 
    direction: 'local_to_remote' | 'remote_to_local' = 'local_to_remote'
  ): Promise<{ success: boolean; message?: string }> {
    try {
      switch (direction) {
        case 'local_to_remote':
          await this.pushItemToRemote(type, itemId)
          break
        case 'remote_to_local':
          await this.pullItemFromRemote(type, itemId)
          break
        default:
          // Bidirectional sync - compare and sync
          await this.syncSingleItem(type, itemId)
      }

      this.logSync(type, direction, 'success', 'Item force synced', {
        item_id: itemId.toString()
      })

      return { success: true, message: 'Item synced successfully' }
    } catch (error) {
      this.logSync(type, direction, 'failed', 'Force sync failed', {
        item_id: itemId.toString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      })

      return { 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to sync item' 
      }
    }
  }

  /**
   * Clear sync logs
   */
  clearSyncLogs(): void {
    this.syncLogs = []
    this.logSync('posts', 'bidirectional', 'success', 'Sync logs cleared')
  }

  /**
   * Export sync configuration
   */
  exportSyncConfig(): {
    siteId: number
    syncInterval: number
    enabledSyncTypes: SyncType[]
    mappings: SyncMapping[]
  } {
    return {
      siteId: this.siteId,
      syncInterval: this.syncInterval,
      enabledSyncTypes: this.enabledSyncTypes,
      mappings: Array.from(this.mappings.values())
    }
  }

  /**
   * Initialize sync statuses for all enabled types
   */
  private initializeSyncStatuses(): void {
    for (const type of this.enabledSyncTypes) {
      this.syncStatuses.set(type, {
        type,
        status: 'idle',
        last_sync: null,
        next_sync: null
      })
    }
  }

  /**
   * Sync posts between local and remote
   */
  private async syncPosts(): Promise<{ synced: number; conflicts: number }> {
    // Get remote posts
    const remotePosts = await this.client.getPosts({ per_page: 100 })
    
    // Mock local posts (in real implementation, would fetch from local database)
    const localPosts = this.getMockLocalPosts()
    
    let synced = 0
    let conflicts = 0

    // Sync each post
    for (const remotePost of remotePosts) {
      const mapping = this.findMapping('posts', remotePost.id)
      if (mapping) {
        // Check for conflicts
        const localPost = localPosts.find(p => p.id === mapping.local_id)
        if (localPost && this.hasChanges(localPost, remotePost)) {
          conflicts++
          this.createConflict('posts', remotePost.id, localPost, remotePost)
        } else {
          synced++
          this.updateMapping(mapping, remotePost)
        }
      } else {
        // New remote post, create locally
        synced++
        this.createMapping('posts', `local_${Date.now()}`, remotePost.id, remotePost)
      }
    }

    return { synced, conflicts }
  }

  /**
   * Sync pages between local and remote
   */
  private async syncPages(): Promise<{ synced: number; conflicts: number }> {
    const remotePages = await this.client.getPages({ per_page: 100 })
    const localPages = this.getMockLocalPages()
    
    let synced = 0
    let conflicts = 0

    for (const remotePage of remotePages) {
      const mapping = this.findMapping('pages', remotePage.id)
      if (mapping) {
        const localPage = localPages.find(p => p.id === mapping.local_id)
        if (localPage && this.hasChanges(localPage, remotePage)) {
          conflicts++
          this.createConflict('pages', remotePage.id, localPage, remotePage)
        } else {
          synced++
          this.updateMapping(mapping, remotePage)
        }
      } else {
        synced++
        this.createMapping('pages', `local_${Date.now()}`, remotePage.id, remotePage)
      }
    }

    return { synced, conflicts }
  }

  /**
   * Sync users between local and remote
   */
  private async syncUsers(): Promise<{ synced: number; conflicts: number }> {
    const remoteUsers = await this.client.getUsers({ per_page: 100 })
    return { synced: remoteUsers.length, conflicts: 0 }
  }

  /**
   * Sync settings between local and remote
   */
  private async syncSettings(): Promise<{ synced: number; conflicts: number }> {
    const remoteSettings = await this.client.getSettings()
    return { synced: 1, conflicts: 0 }
  }

  /**
   * Sync plugins between local and remote
   */
  private async syncPlugins(): Promise<{ synced: number; conflicts: number }> {
    const remotePlugins = await this.client.getPlugins()
    return { synced: remotePlugins.length, conflicts: 0 }
  }

  /**
   * Sync themes between local and remote
   */
  private async syncThemes(): Promise<{ synced: number; conflicts: number }> {
    const remoteThemes = await this.client.getThemes()
    return { synced: remoteThemes.length, conflicts: 0 }
  }

  /**
   * Sync media between local and remote
   */
  private async syncMedia(): Promise<{ synced: number; conflicts: number }> {
    const remoteMedia = await this.client.getMedia({ per_page: 100 })
    return { synced: remoteMedia.length, conflicts: 0 }
  }

  /**
   * Sync comments between local and remote
   */
  private async syncComments(): Promise<{ synced: number; conflicts: number }> {
    const remoteComments = await this.client.getComments({ per_page: 100 })
    return { synced: remoteComments.length, conflicts: 0 }
  }

  /**
   * Find mapping by type and remote ID
   */
  private findMapping(type: SyncType, remoteId: string | number): SyncMapping | undefined {
    const key = `${type}_${remoteId}`
    return this.mappings.get(key)
  }

  /**
   * Create new mapping
   */
  private createMapping(
    type: SyncType, 
    localId: string | number, 
    remoteId: string | number, 
    data: any
  ): void {
    const key = `${type}_${remoteId}`
    const mapping: SyncMapping = {
      local_id: localId,
      remote_id: remoteId,
      type,
      last_synced: new Date().toISOString(),
      checksum: this.generateChecksum(data)
    }
    this.mappings.set(key, mapping)
  }

  /**
   * Update existing mapping
   */
  private updateMapping(mapping: SyncMapping, data: any): void {
    mapping.last_synced = new Date().toISOString()
    mapping.checksum = this.generateChecksum(data)
    const key = `${mapping.type}_${mapping.remote_id}`
    this.mappings.set(key, mapping)
  }

  /**
   * Create conflict record
   */
  private createConflict(
    type: SyncType, 
    itemId: string | number, 
    localData: any, 
    remoteData: any
  ): void {
    const conflictId = `conflict_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`
    const conflict: SyncConflict = {
      id: conflictId,
      type,
      item_id: itemId,
      local_data: localData,
      remote_data: remoteData,
      timestamp: new Date().toISOString(),
      resolved: false
    }
    this.conflicts.set(conflictId, conflict)
  }

  /**
   * Check if data has changes
   */
  private hasChanges(localData: any, remoteData: any): boolean {
    const localChecksum = this.generateChecksum(localData)
    const remoteChecksum = this.generateChecksum(remoteData)
    return localChecksum !== remoteChecksum
  }

  /**
   * Generate checksum for data
   */
  private generateChecksum(data: any): string {
    const str = JSON.stringify(data, Object.keys(data).sort())
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return hash.toString()
  }

  /**
   * Merge conflict data (simplified merge strategy)
   */
  private mergeConflictData(localData: any, remoteData: any): any {
    return {
      ...localData,
      ...remoteData,
      modified: new Date().toISOString() // Add merge timestamp
    }
  }

  /**
   * Push local data to remote
   */
  private async pushLocalData(type: SyncType, itemId: string | number, data: any): Promise<void> {
    // Implementation would depend on the data type
    // For example, for posts: await this.client.updatePost(itemId, data)
  }

  /**
   * Pull remote data to local
   */
  private async pullRemoteData(type: SyncType, itemId: string | number, data: any): Promise<void> {
    // Implementation would update local database with remote data
  }

  /**
   * Push item to remote
   */
  private async pushItemToRemote(type: SyncType, itemId: string | number): Promise<void> {
    // Implementation would push specific item to remote
  }

  /**
   * Pull item from remote
   */
  private async pullItemFromRemote(type: SyncType, itemId: string | number): Promise<void> {
    // Implementation would pull specific item from remote
  }

  /**
   * Sync single item bidirectionally
   */
  private async syncSingleItem(type: SyncType, itemId: string | number): Promise<void> {
    // Implementation would compare local and remote versions and sync
  }

  /**
   * Log sync activity
   */
  private logSync(
    type: SyncType, 
    direction: 'local_to_remote' | 'remote_to_local' | 'bidirectional',
    status: 'success' | 'failed' | 'conflict',
    action: string,
    details?: any
  ): void {
    const log: SyncLog = {
      id: `log_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`,
      type,
      action: 'sync',
      direction,
      status,
      timestamp: new Date().toISOString(),
      details: details || {}
    }
    
    this.syncLogs.push(log)
    
    // Keep only last 1000 logs
    if (this.syncLogs.length > 1000) {
      this.syncLogs = this.syncLogs.slice(-1000)
    }
  }

  /**
   * Get mock local posts for development
   */
  private getMockLocalPosts(): any[] {
    return [
      {
        id: 'local_1',
        title: 'Local Post 1',
        content: 'Local content 1',
        modified: new Date().toISOString()
      }
    ]
  }

  /**
   * Get mock local pages for development
   */
  private getMockLocalPages(): any[] {
    return [
      {
        id: 'local_page_1',
        title: 'Local Page 1',
        content: 'Local page content 1',
        modified: new Date().toISOString()
      }
    ]
  }
}