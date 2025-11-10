import React, { useState, useRef, useEffect } from 'react'
import { Save, Play, MoreVertical, FileDown, FileUp, Copy, Settings } from 'lucide-react'

interface HeaderProps {
  flowName: string
  flowId: string
  isDirty: boolean
  isSaving: boolean
  isRunning: boolean
  lastSaved?: Date
  onNameChange: (name: string) => void
  onSave: () => void
  onRun: () => void
  onExport?: () => void
  onImport?: () => void
  onClone?: () => void
  onSettings?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  flowName,
  flowId,
  isDirty,
  isSaving,
  isRunning,
  lastSaved,
  onNameChange,
  onSave,
  onRun,
  onExport,
  onImport,
  onClone,
  onSettings,
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedName, setEditedName] = useState(flowName)
  const [showMenu, setShowMenu] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isEditing])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }

    if (showMenu) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showMenu])

  const handleNameSubmit = () => {
    if (editedName.trim() && editedName !== flowName) {
      onNameChange(editedName.trim())
    } else {
      setEditedName(flowName)
    }
    setIsEditing(false)
  }

  const handleNameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleNameSubmit()
    } else if (e.key === 'Escape') {
      setEditedName(flowName)
      setIsEditing(false)
    }
  }

  const formatLastSaved = (date?: Date) => {
    if (!date) return 'Never'
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (seconds < 60) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString()
  }

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left: Logo & Title */}
        <div className="flex items-center gap-4">
          <div className="text-2xl font-bold text-blue-400">🌙</div>
          <div className="flex-1">
            <h1 className="text-sm text-gray-400 uppercase tracking-wide">
              Moon Dev Flow
            </h1>

            {/* Flow Name */}
            <div className="flex items-center gap-2 mt-1">
              {isEditing ? (
                <input
                  ref={inputRef}
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  onBlur={handleNameSubmit}
                  onKeyDown={handleNameKeyDown}
                  className="text-xl font-bold bg-gray-700 border border-blue-500 rounded px-2 py-1 text-white focus:outline-none"
                />
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-2xl font-bold text-white hover:text-blue-400 transition-colors"
                  title="Click to rename"
                >
                  {flowName}
                </button>
              )}

              {/* Dirty Indicator */}
              {isDirty && (
                <span className="inline-block w-2 h-2 bg-yellow-500 rounded-full" title="Unsaved changes" />
              )}
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          {/* Last Saved */}
          <div className="text-xs text-gray-500 mr-4 text-right">
            <p>Last saved: {formatLastSaved(lastSaved)}</p>
            <p className="text-gray-600">{flowId.slice(0, 8)}</p>
          </div>

          {/* Save Button */}
          <button
            onClick={onSave}
            disabled={isSaving || !isDirty}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded transition-colors"
            title="Save flow (Ctrl+S)"
          >
            {isSaving ? (
              <>
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Save</span>
              </>
            )}
          </button>

          {/* Run Button */}
          <button
            onClick={onRun}
            disabled={isRunning || isDirty}
            className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded transition-colors"
            title="Run flow (Ctrl+Enter)"
          >
            {isRunning ? (
              <>
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Running...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Run</span>
              </>
            )}
          </button>

          {/* Menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
              title="More options"
            >
              <MoreVertical className="h-5 w-5" />
            </button>

            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-700 rounded shadow-lg z-50">
                {/* Export */}
                {onExport && (
                  <button
                    onClick={() => {
                      onExport()
                      setShowMenu(false)
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors border-b border-gray-700"
                  >
                    <FileDown className="h-4 w-4" />
                    Export as JSON
                  </button>
                )}

                {/* Import */}
                {onImport && (
                  <button
                    onClick={() => {
                      onImport()
                      setShowMenu(false)
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors border-b border-gray-700"
                  >
                    <FileUp className="h-4 w-4" />
                    Import from JSON
                  </button>
                )}

                {/* Clone */}
                {onClone && (
                  <button
                    onClick={() => {
                      onClone()
                      setShowMenu(false)
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors border-b border-gray-700"
                  >
                    <Copy className="h-4 w-4" />
                    Clone Flow
                  </button>
                )}

                {/* Settings */}
                {onSettings && (
                  <button
                    onClick={() => {
                      onSettings()
                      setShowMenu(false)
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors"
                  >
                    <Settings className="h-4 w-4" />
                    Settings
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Info Bar */}
      <div className="mt-3 text-xs text-gray-500 flex gap-4">
        <span>🔴 Nodes: 0</span>
        <span>🔗 Connections: 0</span>
        <span className="ml-auto">Tip: Drag agents to canvas • Double-click node to configure</span>
      </div>
    </header>
  )
}
