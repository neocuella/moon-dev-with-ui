/**
 * Hook for WebSocket connection management
 */

import { useEffect, useRef, useCallback, useState } from 'react'
import { wsAPI } from '../api/client'

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export const useWebSocket = (executionId: string | null, options: UseWebSocketOptions = {}) => {
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  const connect = useCallback(() => {
    if (!executionId || wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const ws = wsAPI.connectExecution(
        executionId,
        (data) => {
          options.onMessage?.(data)
        },
        (error) => {
          options.onError?.(error)
        }
      )

      // Wrap the original onopen
      const originalOnopen = ws.onopen as ((ev: Event) => void) | null
      ws.onopen = (event: Event) => {
        if (originalOnopen) originalOnopen(event)
        setIsConnected(true)
        options.onConnect?.()
      }

      // Wrap the original onclose
      const originalOnclose = ws.onclose as ((ev: CloseEvent) => void) | null
      ws.onclose = (event: CloseEvent) => {
        if (originalOnclose) originalOnclose(event)
        setIsConnected(false)
        options.onDisconnect?.()
        
        // Attempt reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, 3000)
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }, [executionId, options])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
  }, [])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [executionId, connect, disconnect])

  return {
    isConnected,
    send,
    disconnect,
  }
}
