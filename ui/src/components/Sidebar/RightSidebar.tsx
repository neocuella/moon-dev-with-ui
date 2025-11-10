import React, { useState } from 'react'
import { Settings, Activity, Clock } from 'lucide-react'
import { PropertyEditor, FormFieldConfig } from '../PropertyPanel/PropertyEditor'
import { useFlowStore } from '../../store/flowStore'

interface RightSidebarProps {
  selectedNodeId: string | null
  onConfigChange: (nodeId: string, config: Record<string, any>) => void
}

type Tab = 'properties' | 'monitor' | 'history'

export const RightSidebar: React.FC<RightSidebarProps> = ({
  selectedNodeId,
  onConfigChange,
}) => {
  const [activeTab, setActiveTab] = useState<Tab>('properties')
  const { nodes, currentExecution } = useFlowStore()

  const selectedNode = nodes.find((node) => node.id === selectedNodeId)

  // Mock schema - in real app, this would come from agent metadata
  const getNodeSchema = (nodeType: string): FormFieldConfig[] => {
    const baseSchema: FormFieldConfig[] = [
      {
        name: 'enabled',
        label: 'Enabled',
        type: 'toggle',
        description: 'Enable or disable this node',
        defaultValue: true,
      },
      {
        name: 'timeout',
        label: 'Timeout (seconds)',
        type: 'number',
        description: 'Maximum execution time',
        defaultValue: 30,
        min: 1,
        max: 300,
      },
    ]

    // Add type-specific fields
    if (nodeType?.includes('trading')) {
      return [
        ...baseSchema,
        {
          name: 'symbol',
          label: 'Trading Symbol',
          type: 'text',
          placeholder: 'e.g., BTC/USD',
          required: true,
        },
        {
          name: 'strategy',
          label: 'Strategy',
          type: 'select',
          options: [
            { label: 'Momentum', value: 'momentum' },
            { label: 'Mean Reversion', value: 'mean_reversion' },
            { label: 'Breakout', value: 'breakout' },
          ],
          defaultValue: 'momentum',
        },
      ]
    }

    if (nodeType?.includes('risk')) {
      return [
        ...baseSchema,
        {
          name: 'max_position_size',
          label: 'Max Position Size',
          type: 'number',
          defaultValue: 1000,
          min: 0,
        },
        {
          name: 'stop_loss_pct',
          label: 'Stop Loss %',
          type: 'number',
          defaultValue: 2,
          min: 0.1,
          max: 10,
        },
      ]
    }

    return baseSchema
  }

  const tabs = [
    { id: 'properties' as Tab, label: 'Properties', icon: Settings },
    { id: 'monitor' as Tab, label: 'Monitor', icon: Activity },
    { id: 'history' as Tab, label: 'History', icon: Clock },
  ]

  return (
    <div className="w-80 flex flex-col bg-gray-800 border-l border-gray-700">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-gray-700 text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white hover:bg-gray-750'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'properties' && (
          <>
            {selectedNode ? (
              <PropertyEditor
                nodeId={selectedNode.id}
                nodeType={selectedNode.type || 'Unknown'}
                config={selectedNode.data.config || {}}
                schema={getNodeSchema(selectedNode.type || '')}
                onConfigChange={onConfigChange}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-400 text-sm p-8 text-center">
                <Settings className="h-12 w-12 mb-4 text-gray-600" />
                <p className="mb-2">No node selected</p>
                <p className="text-xs text-gray-500">
                  Select a node to view and edit its properties
                </p>
              </div>
            )}
          </>
        )}

        {activeTab === 'monitor' && (
          <div className="p-4">
            <div className="bg-gray-750 rounded p-4 border border-gray-600">
              <h3 className="text-sm font-semibold mb-3 text-white">
                Execution Status
              </h3>
              {currentExecution ? (
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status:</span>
                    <span
                      className={`font-medium ${
                        currentExecution.status === 'completed'
                          ? 'text-green-400'
                          : currentExecution.status === 'running'
                          ? 'text-blue-400'
                          : currentExecution.status === 'failed'
                          ? 'text-red-400'
                          : 'text-yellow-400'
                      }`}
                    >
                      {currentExecution.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Execution ID:</span>
                    <span className="text-gray-300 font-mono text-xs">
                      {currentExecution.id.slice(0, 8)}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-gray-400 text-xs">No active execution</p>
              )}
            </div>

            {selectedNode && (
              <div className="mt-4 bg-gray-750 rounded p-4 border border-gray-600">
                <h3 className="text-sm font-semibold mb-3 text-white">
                  Node Status
                </h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Node:</span>
                    <span className="text-white">{selectedNode.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">ID:</span>
                    <span className="text-gray-300 font-mono">
                      {selectedNode.id.slice(0, 8)}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="p-4">
            <div className="bg-gray-750 rounded p-4 border border-gray-600">
              <h3 className="text-sm font-semibold mb-3 text-white">
                Execution History
              </h3>
              <div className="space-y-3">
                <div className="text-xs text-gray-400 text-center py-8">
                  No execution history available
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
