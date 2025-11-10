/**
 * Execution monitor component - shows real-time execution updates
 */

import React, { useEffect, useState } from 'react'
import { ExecutionResult } from '../../types/flow.types'
import { useWebSocket } from '../../hooks/useWebSocket'

interface ExecutionMonitorProps {
  execution: ExecutionResult | null
  isOpen: boolean
  onClose: () => void
}

export const ExecutionMonitor: React.FC<ExecutionMonitorProps> = ({
  execution,
  isOpen,
  onClose,
}) => {
  const [logs, setLogs] = useState<string[]>([])
  const { isConnected } = useWebSocket(execution?.id || null, {
    onMessage: (data) => {
      if (data.type === 'log') {
        setLogs((prev) => [...prev, `[${data.level}] ${data.message}`])
      }
    },
  })

  // Clear logs when execution changes
  useEffect(() => {
    if (execution) {
      setLogs([])
    }
  }, [execution?.id])

  if (!isOpen || !execution) {
    return null
  }

  const statusColors = {
    pending: 'bg-yellow-600',
    running: 'bg-blue-600',
    completed: 'bg-green-600',
    failed: 'bg-red-600',
  }

  const statusColor = statusColors[execution.status as keyof typeof statusColors] || 'bg-gray-600'

  return (
    <div className="fixed bottom-0 left-64 right-0 h-64 bg-gray-800 border-t border-gray-700 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${statusColor}`}></div>
          <h3 className="font-semibold text-white">Execution Monitor</h3>
          <span className="text-xs text-gray-400">
            {execution.status.toUpperCase()}
            {isConnected && ' (Connected)'}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-2xl leading-none"
        >
          ×
        </button>
      </div>

      {/* Logs */}
      <div className="flex-1 overflow-y-auto p-4 font-mono text-sm bg-gray-900">
        {logs.length === 0 ? (
          <div className="text-gray-500">
            {execution.status === 'pending' && 'Waiting to start...'}
            {execution.status === 'running' && 'Execution in progress...'}
            {execution.status === 'completed' && 'Execution completed'}
            {execution.status === 'failed' && `Failed: ${execution.error || 'Unknown error'}`}
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="text-gray-300 mb-1">
              {log}
            </div>
          ))
        )}
      </div>

      {/* Footer with execution details */}
      <div className="p-3 border-t border-gray-700 bg-gray-800 text-xs text-gray-400 flex justify-between">
        <span>ID: {execution.id.substring(0, 8)}...</span>
        {execution.duration_ms && <span>Duration: {execution.duration_ms}ms</span>}
      </div>
    </div>
  )
}
