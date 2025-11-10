/**
 * Flow types and interfaces
 */

import { Node as XYFlowNode, Edge as XYFlowEdge } from '@xyflow/react'

// Use xyflow types directly
export type Node = XYFlowNode
export type Edge = XYFlowEdge

export interface FlowDefinition {
  name: string
  description?: string
  nodes: Node[]
  edges: Edge[]
  tags?: string[]
}

export interface ExecutionResult {
  id: string
  flow_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: Record<string, any>
  error?: string
  logs?: string
  duration_ms?: number
  created_at: string
  started_at?: string
  ended_at?: string
}

export interface AgentType {
  type: string
  name: string
  description: string
  configSchema: Record<string, any>
  inputs: string[]
  outputs: string[]
}
