#!/bin/bash

# Enhanced Video Scraper Startup Script
# Manages frontend and backend with logging and error handling

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8000
LOG_DIR="./logs"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_LOG="$LOG_DIR/backend.log"
PID_FILE="$LOG_DIR/pids.txt"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} $1"
}

# Function to kill existing processes
kill_existing() {
    print_status "Checking for existing processes..."
    
    # Kill processes on our ports
    if lsof -ti:$FRONTEND_PORT >/dev/null 2>&1; then
        print_warning "Killing process on port $FRONTEND_PORT"
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    if lsof -ti:$BACKEND_PORT >/dev/null 2>&1; then
        print_warning "Killing process on port $BACKEND_PORT"
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any existing Next.js processes
    if pgrep -f "next dev" >/dev/null 2>&1; then
        print_warning "Killing existing Next.js processes"
        pkill -f "next dev" 2>/dev/null || true
    fi
    
    # Kill any existing Python backend processes
    if pgrep -f "main_enhanced.py" >/dev/null 2>&1; then
        print_warning "Killing existing backend processes"
        pkill -f "main_enhanced.py" 2>/dev/null || true
    fi
    
    # Clear PID file
    rm -f "$PID_FILE"
    
    # Wait a moment for processes to fully terminate
    sleep 2
}

# Function to check if a port is available
check_port() {
    local port=$1
    local service=$2
    
    if lsof -ti:$port >/dev/null 2>&1; then
        print_error "Port $port is still in use by $service"
        return 1
    fi
    return 0
}

# Function to start backend
start_backend() {
    print_status "Starting Enhanced Backend..."
    
    if [ ! -f "backend/main_enhanced.py" ]; then
        print_error "Backend file not found: backend/main_enhanced.py"
        return 1
    fi
    
    # Check if required Python packages are installed
    if ! python -c "import fastapi, uvicorn, sqlite3" 2>/dev/null; then
        print_warning "Some Python packages may be missing. Installing dependencies..."
        pip install fastapi uvicorn sqlite3 yt-dlp requests aiofiles
    fi
    
    # Start backend in background with logging
    cd backend
    python main_enhanced.py > "../$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "$BACKEND_PID" >> "$PID_FILE"
    print_success "Backend started with PID: $BACKEND_PID"
    
    # Wait for backend to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if curl -s http://localhost:$BACKEND_PORT/docs >/dev/null 2>&1; then
            print_success "Backend is ready on http://localhost:$BACKEND_PORT"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    print_error "Backend failed to start within 30 seconds"
    return 1
}

# Function to start frontend
start_frontend() {
    print_status "Starting Frontend..."
    
    if [ ! -f "frontend/package.json" ]; then
        print_error "Frontend package.json not found"
        return 1
    fi
    
    # Check if node_modules exists, install if not
    if [ ! -d "frontend/node_modules" ]; then
        print_warning "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    # Start frontend in background with logging
    cd frontend
    npm run dev > "../$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo "$FRONTEND_PID" >> "$PID_FILE"
    print_success "Frontend started with PID: $FRONTEND_PID"
    
    # Wait for frontend to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
            print_success "Frontend is ready on http://localhost:$FRONTEND_PORT"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    print_error "Frontend failed to start within 30 seconds"
    return 1
}

# Function to monitor logs
monitor_logs() {
    print_status "Starting log monitoring..."
    
    # Function to handle cleanup on exit
    cleanup() {
        print_warning "Shutting down services..."
        
        # Kill processes from PID file
        if [ -f "$PID_FILE" ]; then
            while read -r pid; do
                if kill -0 "$pid" 2>/dev/null; then
                    print_warning "Killing process $pid"
                    kill -9 "$pid" 2>/dev/null || true
                fi
            done < "$PID_FILE"
        fi
        
        # Additional cleanup
        kill_existing
        
        print_success "Cleanup completed"
        exit 0
    }
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM EXIT
    
    # Monitor logs in real-time
    print_status "Monitoring logs (Press Ctrl+C to stop)..."
    print_status "Frontend: http://localhost:$FRONTEND_PORT"
    print_status "Backend API: http://localhost:$BACKEND_PORT"
    print_status "Backend Docs: http://localhost:$BACKEND_PORT/docs"
    echo ""
    
    # Use tail to follow both log files
    tail -f "$FRONTEND_LOG" "$BACKEND_LOG" 2>/dev/null | while read -r line; do
        # Color code different log sources
        if echo "$line" | grep -q "$FRONTEND_LOG"; then
            echo -e "${GREEN}[FRONTEND]${NC} $line"
        elif echo "$line" | grep -q "$BACKEND_LOG"; then
            echo -e "${BLUE}[BACKEND]${NC} $line"
        else
            echo "$line"
        fi
    done
}

# Function to check system status
check_status() {
    print_status "System Status:"
    
    if lsof -ti:$FRONTEND_PORT >/dev/null 2>&1; then
        print_success "Frontend: Running on port $FRONTEND_PORT"
    else
        print_error "Frontend: Not running"
    fi
    
    if lsof -ti:$BACKEND_PORT >/dev/null 2>&1; then
        print_success "Backend: Running on port $BACKEND_PORT"
    else
        print_error "Backend: Not running"
    fi
    
    if [ -f "$PID_FILE" ]; then
        print_status "PIDs: $(cat "$PID_FILE" | tr '\n' ' ')"
    fi
}

# Function to show logs
show_logs() {
    print_status "Recent logs:"
    echo ""
    echo "=== Frontend Log ==="
    tail -20 "$FRONTEND_LOG" 2>/dev/null || echo "No frontend log found"
    echo ""
    echo "=== Backend Log ==="
    tail -20 "$BACKEND_LOG" 2>/dev/null || echo "No backend log found"
}

# Main script logic
main() {
    print_status "🚀 Enhanced Video Scraper Startup Script"
    print_status "========================================"
    
    case "${1:-start}" in
        "start")
            kill_existing
            start_backend
            start_frontend
            monitor_logs
            ;;
        "stop")
            print_status "Stopping all services..."
            kill_existing
            print_success "All services stopped"
            ;;
        "restart")
            print_status "Restarting all services..."
            kill_existing
            start_backend
            start_frontend
            monitor_logs
            ;;
        "status")
            check_status
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            print_status "Cleaning up..."
            kill_existing
            rm -rf "$LOG_DIR"
            print_success "Cleanup completed"
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|clean}"
            echo ""
            echo "Commands:"
            echo "  start   - Start frontend and backend (default)"
            echo "  stop    - Stop all services"
            echo "  restart - Restart all services"
            echo "  status  - Show system status"
            echo "  logs    - Show recent logs"
            echo "  clean   - Stop services and clean logs"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 