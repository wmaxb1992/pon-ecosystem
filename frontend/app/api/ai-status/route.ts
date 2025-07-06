import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check if AI system is running by looking for the system file
    const fs = require('fs')
    const path = require('path')
    
    // Check for AI system status file
    const statusFile = path.join(process.cwd(), '..', 'ai_system_status.json')
    
    if (fs.existsSync(statusFile)) {
      const statusData = JSON.parse(fs.readFileSync(statusFile, 'utf8'))
      return NextResponse.json(statusData)
    }
    
    // Default status if no AI system is running
    return NextResponse.json({
      is_running: false,
      approval_pending: false,
      total_tasks: 0,
      ready_tasks: 0,
      testing_tasks: 0,
      in_progress_tasks: 0,
      system_health: {
        performance_score: 0,
        error_count: 0,
        live_site_status: 'unknown'
      }
    })
    
  } catch (error) {
    console.error('Error checking AI status:', error)
    return NextResponse.json(
      { error: 'Failed to check AI status' },
      { status: 500 }
    )
  }
} 