import React, { useState, useMemo } from 'react'
import { Search, ChevronDown, ChevronUp } from 'lucide-react'
import { AgentMetadata } from '../../types/agent'

interface NodeLibraryProps {
  agents: AgentMetadata[]
  onNodeDragStart: (agent: AgentMetadata, event: React.DragEvent) => void
}

interface AgentGroup {
  [category: string]: AgentMetadata[]
}

export const NodeLibrary: React.FC<NodeLibraryProps> = ({ agents, onNodeDragStart }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(Object.keys(groupAgentsByCategory(agents)))
  )
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null)

  // Group agents by category
  function groupAgentsByCategory(agentList: AgentMetadata[]): AgentGroup {
    return agentList.reduce((acc, agent) => {
      const category = agent.category || 'Other'
      if (!acc[category]) {
        acc[category] = []
      }
      acc[category].push(agent)
      return acc
    }, {} as AgentGroup)
  }

  // Filter agents by search query
  const filteredAgents = useMemo(() => {
    const query = searchQuery.toLowerCase()
    return agents.filter(
      (agent) =>
        agent.name.toLowerCase().includes(query) ||
        (agent.description?.toLowerCase().includes(query) ?? false)
    )
  }, [agents, searchQuery])

  const groupedAgents = groupAgentsByCategory(filteredAgents)
  const categories = Object.keys(groupedAgents).sort()

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const handleDragStart = (agent: AgentMetadata, event: React.DragEvent) => {
    onNodeDragStart(agent, event)
  }

  return (
    <div className="flex flex-col h-full bg-gray-800 border-r border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold mb-3 text-white">Agents</h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto">
        {categories.length === 0 ? (
          <div className="p-4 text-center text-gray-400 text-sm">
            No agents found
          </div>
        ) : (
          categories.map((category) => (
            <div key={category} className="border-b border-gray-700">
              {/* Category Header */}
              <button
                onClick={() => toggleCategory(category)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-700 transition-colors"
              >
                <span className="font-medium text-sm text-gray-300">
                  {category}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    {groupedAgents[category].length}
                  </span>
                  {expandedCategories.has(category) ? (
                    <ChevronUp className="h-4 w-4 text-gray-500" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                  )}
                </div>
              </button>

              {/* Category Items */}
              {expandedCategories.has(category) && (
                <div className="bg-gray-750">
                  {groupedAgents[category].map((agent) => (
                    <div
                      key={agent.id}
                      className="relative"
                      onMouseEnter={() => setHoveredAgent(agent.id)}
                      onMouseLeave={() => setHoveredAgent(null)}
                    >
                      {/* Agent Item */}
                      <div
                        draggable
                        onDragStart={(e) => handleDragStart(agent, e)}
                        className="px-4 py-3 hover:bg-gray-700 cursor-move transition-colors border-l-2 border-transparent hover:border-blue-500"
                      >
                        <div className="flex items-start gap-2">
                          {/* Icon/Avatar */}
                          <div className="mt-1 flex-shrink-0">
                            <div className="h-6 w-6 rounded bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
                              {agent.name[0].toUpperCase()}
                            </div>
                          </div>

                          {/* Info */}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                              {agent.name}
                            </p>
                            <p className="text-xs text-gray-400 line-clamp-2">
                              {agent.description || 'No description'}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Hover Preview */}
                      {hoveredAgent === agent.id && (
                        <div className="absolute left-full top-0 ml-2 z-50 bg-gray-900 border border-gray-600 rounded shadow-lg p-3 w-64 text-xs">
                          <p className="font-semibold text-white mb-2">
                            {agent.name}
                          </p>
                          <p className="text-gray-300 mb-3">
                            {agent.description}
                          </p>

                          {/* Inputs */}
                          {agent.inputs && agent.inputs.length > 0 && (
                            <div className="mb-3">
                              <p className="font-medium text-gray-200 mb-1">
                                Inputs
                              </p>
                              <ul className="space-y-1">
                                {agent.inputs.map((input, idx) => (
                                  <li key={idx} className="text-gray-400">
                                    • <span className="text-blue-400">{input.name}</span>
                                    <span className="text-gray-500"> ({input.type})</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Outputs */}
                          {agent.outputs && agent.outputs.length > 0 && (
                            <div>
                              <p className="font-medium text-gray-200 mb-1">
                                Outputs
                              </p>
                              <ul className="space-y-1">
                                {agent.outputs.map((output, idx) => (
                                  <li key={idx} className="text-gray-400">
                                    • <span className="text-green-400">{output.name}</span>
                                    <span className="text-gray-500"> ({output.type})</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Drag Hint */}
                          <p className="text-gray-500 mt-3 italic border-t border-gray-700 pt-2">
                            Drag to canvas →
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-gray-700 bg-gray-750 text-xs text-gray-400">
        <p>
          {filteredAgents.length} agent{filteredAgents.length !== 1 ? 's' : ''}{' '}
          available
        </p>
      </div>
    </div>
  )
}
