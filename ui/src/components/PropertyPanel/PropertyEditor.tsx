import React, { useState, useEffect } from 'react'
import { RotateCcw, Check } from 'lucide-react'
import { FormField } from './FormField'

export interface FormFieldConfig {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'toggle' | 'textarea'
  required?: boolean
  description?: string
  defaultValue?: any
  options?: { label: string; value: any }[]
  placeholder?: string
  min?: number
  max?: number
}

interface PropertyEditorProps {
  nodeId: string
  nodeType: string
  config: Record<string, any>
  schema: FormFieldConfig[]
  onConfigChange: (nodeId: string, config: Record<string, any>) => void
}

export const PropertyEditor: React.FC<PropertyEditorProps> = ({
  nodeId,
  nodeType,
  config,
  schema,
  onConfigChange,
}) => {
  const [formData, setFormData] = useState<Record<string, any>>(config)
  const [isDirty, setIsDirty] = useState(false)

  useEffect(() => {
    setFormData(config)
    setIsDirty(false)
  }, [nodeId, config])

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }))
    setIsDirty(true)
  }

  const handleApply = () => {
    onConfigChange(nodeId, formData)
    setIsDirty(false)
  }

  const handleReset = () => {
    setFormData(config)
    setIsDirty(false)
  }

  return (
    <div className="flex flex-col h-full bg-gray-800 border-l border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wide">
          Properties
        </h2>
        <p className="text-xs text-gray-400 mt-1">{nodeType}</p>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {schema.length === 0 ? (
          <div className="text-center text-gray-400 text-sm py-8">
            <p>No configurable properties</p>
          </div>
        ) : (
          schema.map((field) => (
            <div key={field.name}>
              <FormField
                field={field}
                value={formData[field.name] ?? field.defaultValue}
                onChange={(value) => handleFieldChange(field.name, value)}
              />
            </div>
          ))
        )}
      </div>

      {/* Footer: Buttons */}
      {schema.length > 0 && (
        <div className="border-t border-gray-700 p-4 flex gap-3 bg-gray-750">
          <button
            onClick={handleApply}
            disabled={!isDirty}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:text-gray-400 text-white rounded transition-colors text-sm font-medium"
          >
            <Check className="h-4 w-4" />
            Apply
          </button>
          <button
            onClick={handleReset}
            disabled={!isDirty}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-700 disabled:text-gray-500 text-gray-300 rounded transition-colors text-sm font-medium"
          >
            <RotateCcw className="h-4 w-4" />
            Reset
          </button>
        </div>
      )}
    </div>
  )
}
