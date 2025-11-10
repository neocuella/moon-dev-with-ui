/**
 * API client for communicating with the Moon Dev Flow UI backend
 */

import axios, { AxiosInstance } from 'axios'
import { FlowDefinition, ExecutionResult, AgentType } from '../types/flow.types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with base config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Flow API endpoints
 */
export const flowAPI = {
  /**
   * Create a new flow
   */
  create: async (flow: FlowDefinition & { definition: any }) => {
    const response = await apiClient.post('/api/flows', {
      name: flow.name,
      description: flow.description,
      tags: flow.tags,
      definition: {
        nodes: flow.definition.nodes || flow.nodes || [],
        edges: flow.definition.edges || flow.edges || [],
      },
    })
    return response.data
  },

  /**
   * Get all flows with pagination
   */
  list: async (limit = 20, offset = 0) => {
    const response = await apiClient.get('/api/flows', {
      params: { limit, offset },
    })
    return response.data
  },

  /**
   * Get a specific flow by ID
   */
  get: async (flowId: string) => {
    const response = await apiClient.get(`/api/flows/${flowId}`)
    return response.data
  },

  /**
   * Update a flow
   */
  update: async (flowId: string, updates: Partial<FlowDefinition>) => {
    const response = await apiClient.put(`/api/flows/${flowId}`, {
      name: updates.name,
      description: updates.description,
      tags: updates.tags,
      definition: updates.nodes && updates.edges ? {
        nodes: updates.nodes,
        edges: updates.edges,
      } : undefined,
    })
    return response.data
  },

  /**
   * Delete a flow
   */
  delete: async (flowId: string) => {
    await apiClient.delete(`/api/flows/${flowId}`)
  },
}

/**
 * Execution API endpoints
 */
export const executionAPI = {
  /**
   * Start executing a flow
   */
  run: async (flowId: string) => {
    const response = await apiClient.post(`/api/execution/${flowId}/run`)
    return response.data
  },

  /**
   * Get execution status
   */
  getStatus: async (executionId: string) => {
    const response = await apiClient.get(`/api/execution/${executionId}`)
    return response.data
  },

  /**
   * Get execution history for a flow
   */
  getHistory: async (flowId: string, limit = 20, offset = 0) => {
    const response = await apiClient.get(`/api/execution/${flowId}/history`, {
      params: { limit, offset },
    })
    return response.data
  },
}

/**
 * Agent API endpoints
 */
export const agentAPI = {
  /**
   * Get all available agents
   */
  listAgents: async (): Promise<{ agents: AgentType[]; total: number }> => {
    const response = await apiClient.get('/api/agents')
    return response.data
  },

  /**
   * Get a specific agent schema
   */
  getAgent: async (agentType: string): Promise<AgentType> => {
    const response = await apiClient.get(`/api/agents/${agentType}`)
    return response.data
  },
}

/**
 * WebSocket utilities
 */
export const wsAPI = {
  /**
   * Connect to execution WebSocket stream
   */
  connectExecution: (
    executionId: string,
    onMessage: (data: any) => void,
    onError?: (error: Event) => void
  ): WebSocket => {
    const protocol = API_BASE.startsWith('https') ? 'wss' : 'ws'
    const wsUrl = `${protocol}://${API_BASE.replace(/^https?:\/\//, '')}/ws/execution/${executionId}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log(`✅ Connected to execution ${executionId}`)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    ws.onclose = () => {
      console.log(`❌ Disconnected from execution ${executionId}`)
    }

    return ws
  },
}

export default apiClient
