import React, { useEffect, useRef } from 'react'
import { Edit, Trash2, Copy, Scissors, Clipboard } from 'lucide-react'

interface NodeContextMenuProps {
  nodeId: string
  position: { x: number; y: number }
  onEdit: (nodeId: string) => void
  onDelete: (nodeId: string) => void
  onDuplicate: (nodeId: string) => void
  onClose: () => void
}

export const NodeContextMenu: React.FC<NodeContextMenuProps> = ({
  nodeId,
  position,
  onEdit,
  onDelete,
  onDuplicate,
  onClose,
}) => {
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [onClose])

  const menuItems = [
    {
      label: 'Edit',
      icon: Edit,
      onClick: () => {
        onEdit(nodeId)
        onClose()
      },
      shortcut: 'E',
    },
    {
      label: 'Duplicate',
      icon: Copy,
      onClick: () => {
        onDuplicate(nodeId)
        onClose()
      },
      shortcut: 'Ctrl+D',
    },
    {
      label: 'Delete',
      icon: Trash2,
      onClick: () => {
        onDelete(nodeId)
        onClose()
      },
      shortcut: 'Del',
      danger: true,
    },
  ]

  return (
    <div
      ref={menuRef}
      className="fixed bg-gray-900 border border-gray-600 rounded shadow-xl z-[1000] min-w-[200px]"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      {menuItems.map((item, index) => (
        <button
          key={index}
          onClick={item.onClick}
          className={`w-full flex items-center justify-between px-4 py-2 text-sm transition-colors ${
            item.danger
              ? 'text-red-400 hover:bg-red-900/20'
              : 'text-gray-300 hover:bg-gray-700 hover:text-white'
          } ${index < menuItems.length - 1 ? 'border-b border-gray-700' : ''}`}
        >
          <div className="flex items-center gap-3">
            <item.icon className="h-4 w-4" />
            <span>{item.label}</span>
          </div>
          {item.shortcut && (
            <span className="text-xs text-gray-500">{item.shortcut}</span>
          )}
        </button>
      ))}
    </div>
  )
}
