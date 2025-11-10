import React, { useState, useCallback, useEffect } from 'react'
import { FlowEditor } from './components/FlowEditor/FlowEditor'
import { NodeLibrary } from './components/Sidebar/NodeLibrary'
import { RightSidebar } from './components/Sidebar/RightSidebar'
import { Header } from './components/Header/Header'
import { ExecutionMonitor } from './components/ExecutionMonitor/ExecutionMonitor'
import { NodeConfigDialog } from './components/Dialogs/NodeConfigDialog'
import { NodeContextMenu } from './components/FlowEditor/NodeContextMenu'
import { useFlowStore } from './store/flowStore'
import { useFlowExecution } from './hooks/useFlowExecution'
import { agentAPI } from './api/client'
import { AgentMetadata } from './types/agent'

export default function App() {
  const [showExecutionMonitor, setShowExecutionMonitor] = useState(false)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [contextMenu, setContextMenu] = useState<{ nodeId: string; x: number; y: number } | null>(null)
  const [agents, setAgents] = useState<AgentMetadata[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [isDirty, setIsDirty] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date>()

  const {
    currentFlowId,
    currentFlowName,
    currentExecution,
    nodes,
    edges,
    setFlowName,
    saveFlow,
    updateNodeConfig,
    setNodes,
  } = useFlowStore()

  const { isRunning, runFlow } = useFlowExecution()

  // Load agents on mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const response = await agentAPI.listAgents()
        // Map backend AgentType to frontend AgentMetadata
        const mappedAgents: AgentMetadata[] = response.agents.map((agent) => ({
          id: agent.type,
          name: agent.name,
          type: agent.type,
          category: agent.type.includes('trading') ? 'Trading' : agent.type.includes('risk') ? 'Risk Management' : 'Analysis',
          description: agent.description,
          inputs: agent.inputs.map((input) => ({ name: input, type: 'any', required: false })),
          outputs: agent.outputs.map((output) => ({ name: output, type: 'any' })),
        }))
        setAgents(mappedAgents)
      } catch (error) {
        console.error('Failed to load agents:', error)
      }
    }
    loadAgents()
  }, [])

  // Track dirty state
  useEffect(() => {
    setIsDirty(true)
  }, [nodes, edges, currentFlowName])

  const handleRunFlow = useCallback(async () => {
    const execution = await runFlow()
    if (execution) {
      setShowExecutionMonitor(true)
    }
  }, [runFlow])

  const handleSaveFlow = useCallback(async () => {
    setIsSaving(true)
    try {
      await saveFlow()
      setLastSaved(new Date())
      setIsDirty(false)
    } catch (error) {
      console.error('Failed to save flow:', error)
      alert('Failed to save flow')
    } finally {
      setIsSaving(false)
    }
  }, [saveFlow])

  const handleNodeContextMenu = useCallback((event: React.MouseEvent, nodeId: string) => {
    event.preventDefault()
    setContextMenu({
      nodeId,
      x: event.clientX,
      y: event.clientY,
    })
  }, [])

  const handleDeleteNode = useCallback(
    (nodeId: string) => {
      setNodes(nodes.filter((node) => node.id !== nodeId))
      if (selectedNodeId === nodeId) {
        setSelectedNodeId(null)
      }
    },
    [nodes, selectedNodeId, setNodes]
  )

  const handleDuplicateNode = useCallback(
    (nodeId: string) => {
      const nodeToDuplicate = nodes.find((node) => node.id === nodeId)
      if (nodeToDuplicate) {
        const newNode = {
          ...nodeToDuplicate,
          id: `${nodeToDuplicate.type}-${Date.now()}`,
          position: {
            x: nodeToDuplicate.position.x + 50,
            y: nodeToDuplicate.position.y + 50,
          },
        }
        setNodes([...nodes, newNode])
      }
    },
    [nodes, setNodes]
  )

  const handleNodeDragStart = (agent: AgentMetadata, event: React.DragEvent) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(agent))
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <Header
        flowName={currentFlowName}
        flowId={currentFlowId || 'unsaved'}
        isDirty={isDirty}
        isSaving={isSaving}
        isRunning={isRunning}
        lastSaved={lastSaved}
        onNameChange={setFlowName}
        onSave={handleSaveFlow}
        onRun={handleRunFlow}
        onExport={() => console.log('Export')}
        onImport={() => console.log('Import')}
        onClone={() => console.log('Clone')}
        onSettings={() => console.log('Settings')}
      />

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Node Library */}
        <div className="w-64">
          <NodeLibrary agents={agents} onNodeDragStart={handleNodeDragStart} />
        </div>

        {/* Flow Editor */}
        <div className="flex-1 flex flex-col">
          <FlowEditor
            onNodeDoubleClick={setSelectedNodeId}
            onNodeContextMenu={handleNodeContextMenu}
          />
        </div>

        {/* Right Sidebar - Properties Panel */}
        <RightSidebar selectedNodeId={selectedNodeId} onConfigChange={updateNodeConfig} />
      </div>

      {/* Execution Monitor */}
      <ExecutionMonitor
        execution={currentExecution}
        isOpen={showExecutionMonitor}
        onClose={() => setShowExecutionMonitor(false)}
      />

      {/* Node Config Dialog */}
      {selectedNodeId && (
        <NodeConfigDialog nodeId={selectedNodeId} onClose={() => setSelectedNodeId(null)} />
      )}

      {/* Context Menu */}
      {contextMenu && (
        <NodeContextMenu
          nodeId={contextMenu.nodeId}
          position={{ x: contextMenu.x, y: contextMenu.y }}
          onEdit={setSelectedNodeId}
          onDelete={handleDeleteNode}
          onDuplicate={handleDuplicateNode}
          onClose={() => setContextMenu(null)}
        />
      )}
    </div>
  )
}
