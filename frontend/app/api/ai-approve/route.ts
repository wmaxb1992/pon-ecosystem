import { NextResponse } from 'next/server'

export async function POST() {
  try {
    const fs = require('fs')
    const path = require('path')
    
    // Create approval file
    const approvalFile = path.join(process.cwd(), '..', 'APPROVED')
    fs.writeFileSync(approvalFile, JSON.stringify({
      approved_at: new Date().toISOString(),
      approved_by: 'user',
      action: 'approve'
    }))
    
    // Remove approval request file if it exists
    const requestFile = path.join(process.cwd(), '..', 'APPROVAL_REQUESTED')
    if (fs.existsSync(requestFile)) {
      fs.unlinkSync(requestFile)
    }
    
    return NextResponse.json({ 
      success: true, 
      message: 'Changes approved and deployment initiated' 
    })
    
  } catch (error) {
    console.error('Error approving changes:', error)
    return NextResponse.json(
      { error: 'Failed to approve changes' },
      { status: 500 }
    )
  }
} 