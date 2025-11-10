/**
 * Hook for managing flow execution
 */

import { useState, useCallback } from 'react'
import { ExecutionResult } from '../types/flow.types'
import { executionAPI, agentAPI } from '../api/client'
import { useFlowStore } from '../store/flowStore'

export const useFlowExecution = () => {
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { currentFlowId, setCurrentExecution } = useFlowStore()

  const runFlow = useCallback(async () => {
    if (!currentFlowId) {
      setError('No flow selected')
      return null
    }

    setIsRunning(true)
    setError(null)

    try {
      const execution = await executionAPI.run(currentFlowId)
      setCurrentExecution(execution)
      return execution
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Failed to run flow'
      setError(message)
      return null
    } finally {
      setIsRunning(false)
    }
  }, [currentFlowId, setCurrentExecution])

  const getExecutionStatus = useCallback(async (executionId: string) => {
    try {
      const execution = await executionAPI.getStatus(executionId)
      setCurrentExecution(execution)
      return execution
    } catch (err: any) {
      setError(err.message || 'Failed to get execution status')
      return null
    }
  }, [setCurrentExecution])

  const getExecutionHistory = useCallback(
    async (flowId: string) => {
      try {
        return await executionAPI.getHistory(flowId)
      } catch (err: any) {
        setError(err.message || 'Failed to get execution history')
        return null
      }
    },
    []
  )

  const getAgentSchema = useCallback(async (agentType: string) => {
    try {
      return await agentAPI.getAgent(agentType)
    } catch (err: any) {
      console.warn(`Failed to get schema for ${agentType}:`, err.message)
      return null
    }
  }, [])

  return {
    isRunning,
    error,
    runFlow,
    getExecutionStatus,
    getExecutionHistory,
    getAgentSchema,
  }
}
