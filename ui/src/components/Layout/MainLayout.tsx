/**
 * Main layout component wrapper (for future use)
 */

import React from 'react'

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return <>{children}</>
}
