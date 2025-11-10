/**
 * Node Configuration Dialog - Configure agent parameters
 */

import React, { useState, useEffect } from 'react'
import { useFlowStore } from '../../store/flowStore'
import { useFlowExecution } from '../../hooks/useFlowExecution'

interface NodeConfigDialogProps {
  nodeId: string
  onClose: () => void
}

export const NodeConfigDialog: React.FC<NodeConfigDialogProps> = ({ nodeId, onClose }) => {
  const { nodes, updateNodeConfig } = useFlowStore()
  const { getAgentSchema } = useFlowExecution()

  const node = nodes.find((n) => n.id === nodeId)
  const [config, setConfig] = useState<Record<string, any>>(node?.data?.config || {})
  const [schema, setSchema] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!node?.data?.type) return

    // Fetch schema for the agent type
    const fetchSchema = async () => {
      try {
        setLoading(true)
        const agentType = node.data.type as string
        const agentData = await getAgentSchema(agentType)

        if (agentData?.configSchema?.parameters) {
          setSchema({ parameters: agentData.configSchema.parameters })
        } else {
          setSchema({ parameters: [] })
        }
      } catch (error) {
        console.error('Failed to fetch schema:', error)
        // Fallback to empty schema
        setSchema({ parameters: [] })
      } finally {
        setLoading(false)
      }
    }

    fetchSchema()
  }, [node?.data?.type, getAgentSchema])

  const handleConfigChange = (paramName: string, value: any) => {
    setConfig((prev) => ({
      ...prev,
      [paramName]: value,
    }))
  }

  const handleSave = () => {
    updateNodeConfig(nodeId, config)
    onClose()
  }

  if (!node) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-900 rounded-lg p-6 w-96 border border-gray-700">
          <p className="text-gray-400">Node not found</p>
          <button
            onClick={onClose}
            className="mt-4 w-full px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg p-6 w-96 max-h-96 overflow-y-auto border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">
      Configure {(node.data?.type as string) || 'Agent'}
      </h2>

        {loading ? (
          <div className="text-gray-400">Loading schema...</div>
        ) : (
          <div className="space-y-4">
            {schema?.parameters && schema.parameters.length > 0 ? (
              schema.parameters.map((param: any) => (
                <div key={param.name} className="space-y-1">
                  <label className="block text-sm font-medium text-gray-300">
                    {param.name}
                    {param.required && <span className="text-red-400">*</span>}
                  </label>
                  <p className="text-xs text-gray-500">{param.description}</p>
                  <input
                    type={param.type === 'number' ? 'number' : 'text'}
                    value={config[param.name] || ''}
                    onChange={(e) =>
                      handleConfigChange(
                        param.name,
                        param.type === 'number' ? parseFloat(e.target.value) : e.target.value
                      )
                    }
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                    placeholder={param.required ? 'Required' : 'Optional'}
                  />
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No configuration parameters for this agent</p>
            )}
          </div>
        )}

        <div className="mt-6 flex gap-3">
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Save
          </button>
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
