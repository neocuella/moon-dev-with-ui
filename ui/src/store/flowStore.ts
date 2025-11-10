/**
 * Zustand store for flow state management
 */

import { create } from 'zustand'
import { Node, Edge } from '@xyflow/react'
import { FlowDefinition, ExecutionResult } from '../types/flow.types'
import { flowAPI, executionAPI } from '../api/client'

interface FlowState {
  // Current flow being edited
  currentFlowId: string | null
  currentFlowName: string
  currentFlowDescription: string
  nodes: Node[]
  edges: Edge[]

  // Available flows
  flows: Array<{ id: string; name: string; description?: string }>
  isLoadingFlows: boolean

  // Flow management actions
  setFlowName: (name: string) => void
  setFlowDescription: (description: string) => void
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
  updateNodeConfig: (nodeId: string, config: Record<string, any>) => void
  createNewFlow: (name: string, description?: string) => void
  loadFlow: (flowId: string) => Promise<void>
  saveFlow: () => Promise<string | null>
  deleteFlow: (flowId: string) => Promise<void>
  loadFlowsList: () => Promise<void>

  // Execution state
  currentExecution: ExecutionResult | null
  executionHistory: ExecutionResult[]
  setCurrentExecution: (execution: ExecutionResult | null) => void
}

export const useFlowStore = create<FlowState>((set, get) => ({
  // Initial state
  currentFlowId: null,
  currentFlowName: 'Untitled Flow',
  currentFlowDescription: '',
  nodes: [],
  edges: [],
  flows: [],
  isLoadingFlows: false,
  currentExecution: null,
  executionHistory: [],

  // Flow management actions
  setFlowName: (name: string) => set({ currentFlowName: name }),

  setFlowDescription: (description: string) => set({ currentFlowDescription: description }),

  setNodes: (nodes: Node[]) => set({ nodes }),

  setEdges: (edges: Edge[]) => set({ edges }),

  updateNodeConfig: (nodeId: string, config: Record<string, any>) => {
    const state = get()
    const updatedNodes = state.nodes.map((node) => {
      if (node.id === nodeId) {
        return {
          ...node,
          data: {
            ...node.data,
            config,
          },
        }
      }
      return node
    })
    set({ nodes: updatedNodes })
  },

  createNewFlow: (name: string, description?: string) => {
    set({
      currentFlowId: null,
      currentFlowName: name,
      currentFlowDescription: description || '',
      nodes: [],
      edges: [],
    })
  },

  loadFlow: async (flowId: string) => {
    try {
      const flow = await flowAPI.get(flowId)
      set({
        currentFlowId: flow.id,
        currentFlowName: flow.name,
        currentFlowDescription: flow.description || '',
        nodes: flow.definition.nodes || [],
        edges: flow.definition.edges || [],
      })
    } catch (error) {
      console.error('Failed to load flow:', error)
      throw error
    }
  },

  saveFlow: async () => {
    try {
      const state = get()
      const flowData = {
        name: state.currentFlowName,
        description: state.currentFlowDescription,
        nodes: state.nodes as any,
        edges: state.edges as any,
      }

      let flowId: string
      if (state.currentFlowId) {
        // Update existing flow
        const updated = await flowAPI.update(state.currentFlowId, flowData as Partial<FlowDefinition>)
        flowId = updated.id
      } else {
        // Create new flow
        const created = await flowAPI.create({
          name: flowData.name,
          description: flowData.description,
          nodes: flowData.nodes,
          edges: flowData.edges,
          definition: flowData,
        })
        flowId = created.id
        set({ currentFlowId: flowId })
      }

      // Refresh flows list
      get().loadFlowsList()
      return flowId
    } catch (error) {
      console.error('Failed to save flow:', error)
      throw error
    }
  },

  deleteFlow: async (flowId: string) => {
    try {
      await flowAPI.delete(flowId)
      // Refresh flows list
      get().loadFlowsList()
    } catch (error) {
      console.error('Failed to delete flow:', error)
      throw error
    }
  },

  loadFlowsList: async () => {
    set({ isLoadingFlows: true })
    try {
      const result = await flowAPI.list(100, 0)
      set({
        flows: result.flows.map((f: any) => ({
          id: f.id,
          name: f.name,
          description: f.description,
        })),
      })
    } catch (error) {
      console.error('Failed to load flows:', error)
    } finally {
      set({ isLoadingFlows: false })
    }
  },

  setCurrentExecution: (execution: ExecutionResult | null) => set({ currentExecution: execution }),
}))
