import { NextResponse } from 'next/server'

export async function POST() {
  try {
    const fs = require('fs')
    const path = require('path')
    
    // Remove approval request file
    const requestFile = path.join(process.cwd(), '..', 'APPROVAL_REQUESTED')
    if (fs.existsSync(requestFile)) {
      fs.unlinkSync(requestFile)
    }
    
    // Create rejection file for logging
    const rejectionFile = path.join(process.cwd(), '..', 'REJECTED')
    fs.writeFileSync(rejectionFile, JSON.stringify({
      rejected_at: new Date().toISOString(),
      rejected_by: 'user',
      action: 'reject'
    }))
    
    return NextResponse.json({ 
      success: true, 
      message: 'Changes rejected' 
    })
    
  } catch (error) {
    console.error('Error rejecting changes:', error)
    return NextResponse.json(
      { error: 'Failed to reject changes' },
      { status: 500 }
    )
  }
} 