/**
 * Sidebar with node library and flow controls
 */

import React, { useEffect, useState } from 'react'
import { useFlowStore } from '../../store/flowStore'
import { agentAPI } from '../../api/client'
import { AgentType } from '../../types/flow.types'
import { validateFlow } from '../../utils/flowValidation'

interface SidebarProps {
  onRunFlow: () => void
  isRunning: boolean
  onSaveFlow: () => Promise<void>
}

export const Sidebar: React.FC<SidebarProps> = ({ onRunFlow, isRunning, onSaveFlow }) => {
  const [agents, setAgents] = useState<AgentType[]>([])
  const [isLoadingAgents, setIsLoadingAgents] = useState(false)
  const [validationMessage, setValidationMessage] = useState<string>('')
  const { currentFlowName, setFlowName, setFlowDescription, nodes, edges } = useFlowStore()

  // Load available agents
  useEffect(() => {
    const loadAgents = async () => {
      setIsLoadingAgents(true)
      try {
        const result = await agentAPI.listAgents()
        setAgents(result.agents)
      } catch (error) {
        console.error('Failed to load agents:', error)
      } finally {
        setIsLoadingAgents(false)
      }
    }
    loadAgents()
  }, [])

  // Handle drag start for node creation
  const handleDragStart = (agent: AgentType) => (e: React.DragEvent) => {
    const nodeData = {
      type: agent.type,
      label: agent.name,
      description: agent.description,
    }
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData))
  }

  // Handle run flow with validation
  const handleRunFlow = () => {
    const validation = validateFlow(nodes, edges)
    if (!validation.isValid) {
      const errorMsg = validation.errors
        .filter((e) => e.type === 'error')
        .map((e) => e.message)
        .join('\n')
      setValidationMessage(`❌ Flow validation failed:\n${errorMsg}`)
      setTimeout(() => setValidationMessage(''), 5000)
      return
    }
    setValidationMessage('')
    onRunFlow()
  }

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-bold text-white mb-4">Flow Editor</h2>

        {/* Flow name input */}
        <input
          type="text"
          value={currentFlowName}
          onChange={(e) => setFlowName(e.target.value)}
          placeholder="Flow name"
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-2 text-sm"
        />

        {/* Validation message */}
        {validationMessage && (
          <div className="mb-3 p-2 bg-red-900/30 border border-red-600 rounded text-xs text-red-300 whitespace-pre-wrap">
            {validationMessage}
          </div>
        )}

        {/* Save and Run buttons */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={onSaveFlow}
            className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition"
          >
            💾 Save
          </button>
          <button
            onClick={handleRunFlow}
            disabled={isRunning}
            className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm font-medium transition"
          >
            {isRunning ? '⏳ Running...' : '▶️ Run'}
          </button>
        </div>
      </div>

      {/* Node Library */}
      <div className="p-4 flex-1">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Available Agents</h3>

        {isLoadingAgents ? (
          <div className="text-gray-400 text-sm">Loading agents...</div>
        ) : agents.length === 0 ? (
          <div className="text-gray-400 text-sm">No agents available</div>
        ) : (
          <div className="space-y-2">
            {agents.map((agent) => (
              <div
                key={agent.type}
                draggable
                onDragStart={handleDragStart(agent)}
                className="p-3 bg-gray-700 hover:bg-gray-600 rounded cursor-move transition border border-gray-600 hover:border-blue-500"
              >
                <div className="font-sm text-white font-medium">{agent.name}</div>
                <div className="text-xs text-gray-400">{agent.type}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 text-xs text-gray-400">
        <p>Drag agents onto canvas to create nodes</p>
      </div>
    </div>
  )
}
