export interface AgentInput {
  name: string
  type: string
  required?: boolean
  description?: string
}

export interface AgentOutput {
  name: string
  type: string
  description?: string
}

export interface AgentMetadata {
  id: string
  name: string
  type: string
  category?: string
  description?: string
  inputs?: AgentInput[]
  outputs?: AgentOutput[]
  config?: Record<string, any>
}
