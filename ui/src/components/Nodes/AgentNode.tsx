/**
 * AgentNode component - represents an agent in the flow
 */

import React from 'react'
import { Handle, Position, NodeProps } from '@xyflow/react'

type AgentNodeData = {
  label?: string
  type?: string
  description?: string
  config?: Record<string, any>
}

export const AgentNode: React.FC<NodeProps<any>> = ({ 
  data, 
  selected, 
  isConnectable 
}) => {
  const nodeData = (data || {}) as AgentNodeData
  const hasConfig = nodeData.config && Object.keys(nodeData.config).length > 0

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 transition-all cursor-pointer
        ${selected ? 'border-blue-500 bg-blue-900/20' : 'border-gray-600 bg-gray-800'}
        shadow-lg min-w-[200px] hover:border-blue-400
      `}
    >
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} />
      
      <div className="flex items-start justify-between">
        <div>
          <div className="font-semibold text-white mb-1">{nodeData.label || 'Agent'}</div>
          <div className="text-xs text-gray-300 mb-2">{nodeData.type || 'unknown'}</div>
        </div>
        {hasConfig && (
          <div className="ml-2 px-2 py-1 bg-green-900/30 border border-green-600 rounded text-xs text-green-300">
            ✓ Config
          </div>
        )}
      </div>
      
      {nodeData.description && (
        <div className="text-xs text-gray-400 italic">{nodeData.description}</div>
      )}

      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />
    </div>
  )
}
