/**
 * Main flow editor component using xyflow
 */

import React, { useCallback, useEffect, useRef } from 'react'
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  useReactFlow,
  NodeTypes,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useFlowStore } from '../../store/flowStore'
import { AgentNode } from '../Nodes/AgentNode'

const nodeTypes: NodeTypes = {
  agent: AgentNode as any,
}

const FlowEditorContent: React.FC<{
  onNodeDoubleClick?: (nodeId: string) => void
  onNodeContextMenu?: (event: React.MouseEvent, nodeId: string) => void
}> = ({ onNodeDoubleClick, onNodeContextMenu }) => {
  const {
    nodes: storeNodes,
    edges: storeEdges,
    setNodes: setStoreNodes,
    setEdges: setStoreEdges,
  } = useFlowStore()

  const [nodes, setNodes, onNodesChange] = useNodesState(storeNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges)
  const { screenToFlowPosition } = useReactFlow()
  const reactFlowWrapperRef = useRef<HTMLDivElement>(null)

  // Sync store with local state
  useEffect(() => {
    setNodes(storeNodes)
  }, [storeNodes, setNodes])

  useEffect(() => {
    setEdges(storeEdges)
  }, [storeEdges, setEdges])

  // Handle connection
  const onConnect = useCallback(
    (connection: Connection) => {
      const newEdges = addEdge(connection, edges)
      setEdges(newEdges)
      setStoreEdges(newEdges)
    },
    [edges, setEdges, setStoreEdges]
  )

  // Handle node double-click
  const handleNodeDoubleClick = useCallback(
    (_event: React.MouseEvent, node: any) => {
      onNodeDoubleClick?.(node.id)
    },
    [onNodeDoubleClick]
  )

  // Handle node context menu
  const handleNodeContextMenu = useCallback(
    (event: React.MouseEvent, node: any) => {
      onNodeContextMenu?.(event, node.id)
    },
    [onNodeContextMenu]
  )

  // Sync to store when nodes change
  useEffect(() => {
    setStoreNodes(nodes)
  }, [nodes, setStoreNodes])

  // Handle drag over
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  // Handle drop to create new node
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      if (!reactFlowWrapperRef.current) return

      const data = event.dataTransfer.getData('application/reactflow')
      if (!data) return

      try {
        const nodeData = JSON.parse(data)

        // Get position relative to the canvas
        const reactFlowBounds = reactFlowWrapperRef.current.getBoundingClientRect()
        const position = screenToFlowPosition({
          x: event.clientX - reactFlowBounds.left,
          y: event.clientY - reactFlowBounds.top,
        })

        const newNode = {
          id: `${nodeData.type}-${Date.now()}`,
          data: nodeData,
          position,
          type: 'agent',
        }

        setNodes((nds) => nds.concat(newNode))
      } catch (error) {
        console.error('Failed to create node:', error)
      }
    },
    [screenToFlowPosition, setNodes]
  )

  return (
    <div ref={reactFlowWrapperRef} className="w-full h-full bg-gray-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeDoubleClick={handleNodeDoubleClick}
        onNodeContextMenu={handleNodeContextMenu}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}

export const FlowEditor: React.FC<{
  onNodeDoubleClick?: (nodeId: string) => void
  onNodeContextMenu?: (event: React.MouseEvent, nodeId: string) => void
}> = ({ onNodeDoubleClick, onNodeContextMenu }) => {
  return (
    <ReactFlowProvider>
      <FlowEditorContent onNodeDoubleClick={onNodeDoubleClick} onNodeContextMenu={onNodeContextMenu} />
    </ReactFlowProvider>
  )
}
