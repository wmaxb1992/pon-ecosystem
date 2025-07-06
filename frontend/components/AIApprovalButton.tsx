'use client'

import React, { useState, useEffect } from 'react'
import { CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react'

interface AIApprovalButtonProps {
  onApprove: () => void
  onReject: () => void
}

interface SystemStatus {
  is_running: boolean
  approval_pending: boolean
  total_tasks: number
  ready_tasks: number
  testing_tasks: number
  in_progress_tasks: number
  system_health?: {
    performance_score: number
    error_count: number
    live_site_status: string
  }
}

export default function AIApprovalButton({ onApprove, onReject }: AIApprovalButtonProps) {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch('/api/ai-status')
        if (response.ok) {
          const data = await response.json()
          setStatus(data)
          setIsVisible(data.approval_pending || data.ready_tasks > 0)
        }
      } catch (error) {
        console.error('Error checking AI status:', error)
      }
    }

    // Check status every 30 seconds
    checkStatus()
    const interval = setInterval(checkStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  const handleApprove = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/ai-approve', { method: 'POST' })
      if (response.ok) {
        onApprove()
        setIsVisible(false)
      }
    } catch (error) {
      console.error('Error approving changes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReject = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/ai-reject', { method: 'POST' })
      if (response.ok) {
        onReject()
        setIsVisible(false)
      }
    } catch (error) {
      console.error('Error rejecting changes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isVisible) return null

  return (
    <div className="fixed top-4 right-4 z-50">
      {/* Main Button */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg p-4 min-w-[300px]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-yellow-300" />
            <span className="font-semibold">AI Improvements Ready</span>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-white hover:text-gray-200 transition-colors"
          >
            {showDetails ? '−' : '+'}
          </button>
        </div>

        {showDetails && status && (
          <div className="mb-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Ready Tasks:</span>
              <span className="font-semibold text-green-300">{status.ready_tasks}</span>
            </div>
            <div className="flex justify-between">
              <span>Testing Tasks:</span>
              <span className="font-semibold text-yellow-300">{status.testing_tasks}</span>
            </div>
            <div className="flex justify-between">
              <span>In Progress:</span>
              <span className="font-semibold text-blue-300">{status.in_progress_tasks}</span>
            </div>
            {status.system_health && (
              <>
                <div className="flex justify-between">
                  <span>Performance Score:</span>
                  <span className={`font-semibold ${
                    status.system_health.performance_score >= 90 ? 'text-green-300' :
                    status.system_health.performance_score >= 70 ? 'text-yellow-300' : 'text-red-300'
                  }`}>
                    {status.system_health.performance_score.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Live Site Status:</span>
                  <span className={`font-semibold ${
                    status.system_health.live_site_status === 'healthy' ? 'text-green-300' :
                    status.system_health.live_site_status === 'warning' ? 'text-yellow-300' : 'text-red-300'
                  }`}>
                    {status.system_health.live_site_status.toUpperCase()}
                  </span>
                </div>
              </>
            )}
          </div>
        )}

        <div className="flex space-x-2">
          <button
            onClick={handleApprove}
            disabled={isLoading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white py-2 px-4 rounded-md transition-colors flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <CheckCircle className="h-4 w-4" />
            )}
            <span>Approve & Deploy</span>
          </button>
          <button
            onClick={handleReject}
            disabled={isLoading}
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-800 text-white py-2 px-4 rounded-md transition-colors flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
            <span>Reject</span>
          </button>
        </div>

        <div className="mt-3 text-xs text-gray-300">
          🤖 AI has tested all improvements on development server
        </div>
      </div>
    </div>
  )
} 