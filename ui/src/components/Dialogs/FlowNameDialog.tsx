/**
 * Dialog for naming flows (for future use)
 */

import React from 'react'

interface FlowNameDialogProps {
  isOpen: boolean
  onClose: () => void
  onSave: (name: string) => void
}

export const FlowNameDialog: React.FC<FlowNameDialogProps> = ({
  isOpen,
  onClose,
  onSave,
}) => {
  // Placeholder for future implementation
  return null
}
