/**
 * Flow validation utilities
 */

import { Node, Edge } from '@xyflow/react'

export interface ValidationError {
  type: 'error' | 'warning'
  message: string
  nodeId?: string
}

export interface ValidationResult {
  isValid: boolean
  errors: ValidationError[]
}

/**
 * Validate a flow before execution
 */
export function validateFlow(nodes: Node[], edges: Edge[]): ValidationResult {
  const errors: ValidationError[] = []

  // Check if there are nodes
  if (nodes.length === 0) {
    errors.push({
      type: 'error',
      message: 'Flow must contain at least one node',
    })
    return { isValid: false, errors }
  }

  // Check each node
  for (const node of nodes) {
    // Check if node has required configuration
    const nodeType = node.data?.type
    if (!nodeType) {
      errors.push({
        type: 'error',
        message: `Node ${node.id} has no agent type`,
        nodeId: node.id,
      })
    }

    // Check if node has configuration (optional but recommended)
    const hasConfig = node.data?.config && Object.keys(node.data.config).length > 0
    if (!hasConfig) {
      errors.push({
        type: 'warning',
        message: `Node ${node.id} (${nodeType}) has no configuration`,
        nodeId: node.id,
      })
    }
  }

  // Check for disconnected nodes (optional)
  const connectedNodeIds = new Set<string>()
  for (const edge of edges) {
    connectedNodeIds.add(edge.source)
    connectedNodeIds.add(edge.target)
  }

  // Allow single node flows or disconnected nodes (for parallel execution)
  if (nodes.length > 1 && connectedNodeIds.size < nodes.length) {
    const disconnectedNodes = nodes.filter((n) => !connectedNodeIds.has(n.id))
    disconnectedNodes.forEach((node) => {
      errors.push({
        type: 'warning',
        message: `Node ${node.id} (${node.data?.type}) is not connected to any other nodes`,
        nodeId: node.id,
      })
    })
  }

  // Check for cycles (optional - flows with cycles might be intentional)
  // Skipping for now as cycles might be valid for certain use cases

  const hasErrors = errors.some((e) => e.type === 'error')
  return {
    isValid: !hasErrors,
    errors,
  }
}

/**
 * Get a human-readable validation message
 */
export function getValidationMessage(result: ValidationResult): string {
  if (result.isValid) {
    return 'Flow is valid and ready to run'
  }

  const errorMessages = result.errors
    .filter((e) => e.type === 'error')
    .map((e) => e.message)

  return errorMessages.join('\n')
}
