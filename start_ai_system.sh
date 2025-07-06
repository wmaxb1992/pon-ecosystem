#!/bin/bash

# AI-Driven Video Scraper with Continuous Improvement System
# ===========================================================
# This script starts the complete system including:
# - Live site (protected, never disrupted)
# - AI improvement system (runs in background)
# - Development environment for testing
# - Comprehensive logging and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIVE_FRONTEND_PORT=3000
LIVE_BACKEND_PORT=8000
DEV_FRONTEND_PORT=3002
DEV_BACKEND_PORT=8001
AI_SYSTEM_PORT=8002

# Logging
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# PID files
LIVE_FRONTEND_PID="$LOG_DIR/live_frontend.pid"
LIVE_BACKEND_PID="$LOG_DIR/live_backend.pid"
DEV_FRONTEND_PID="$LOG_DIR/dev_frontend.pid"
DEV_BACKEND_PID="$LOG_DIR/dev_backend.pid"
AI_SYSTEM_PID="$LOG_DIR/ai_system.pid"

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')]${NC} ⚠️  $1"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')]${NC} ❌ $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} ✅ $1"
}

log_info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} ℹ️  $1"
}

log_ai() {
    echo -e "${PURPLE}[$(date +'%H:%M:%S')]${NC} 🤖 $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        log_warning "Killing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check if process is running
is_process_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to start live backend
start_live_backend() {
    log_info "Starting Live Backend..."
    cd "$PROJECT_ROOT/backend"
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
    fi
    
    # Start backend
    nohup python main_enhanced.py > "$LOG_DIR/live_backend.log" 2>&1 &
    echo $! > "$LIVE_BACKEND_PID"
    
    # Wait for backend to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if check_port $LIVE_BACKEND_PORT; then
            log_success "Live Backend started on port $LIVE_BACKEND_PORT"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    log_error "Failed to start Live Backend"
    return 1
}

# Function to start live frontend
start_live_frontend() {
    log_info "Starting Live Frontend..."
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
    fi
    
    # Start frontend
    PORT=$LIVE_FRONTEND_PORT nohup npm run dev > "$LOG_DIR/live_frontend.log" 2>&1 &
    echo $! > "$LIVE_FRONTEND_PID"
    
    # Wait for frontend to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if check_port $LIVE_FRONTEND_PORT; then
            log_success "Live Frontend started on port $LIVE_FRONTEND_PORT"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    log_error "Failed to start Live Frontend"
    return 1
}

# Function to start development backend
start_dev_backend() {
    log_info "Starting Development Backend..."
    cd "$PROJECT_ROOT/backend"
    
    source venv/bin/activate
    
    # Start backend on different port
    PORT=$DEV_BACKEND_PORT nohup python main_enhanced.py > "$LOG_DIR/dev_backend.log" 2>&1 &
    echo $! > "$DEV_BACKEND_PID"
    
    # Wait for backend to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if check_port $DEV_BACKEND_PORT; then
            log_success "Development Backend started on port $DEV_BACKEND_PORT"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    log_error "Failed to start Development Backend"
    return 1
}

# Function to start development frontend
start_dev_frontend() {
    log_info "Starting Development Frontend..."
    cd "$PROJECT_ROOT/frontend"
    
    # Start frontend on different port
    PORT=$DEV_FRONTEND_PORT nohup npm run dev > "$LOG_DIR/dev_frontend.log" 2>&1 &
    echo $! > "$DEV_FRONTEND_PID"
    
    # Wait for frontend to start
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if check_port $DEV_FRONTEND_PORT; then
            log_success "Development Frontend started on port $DEV_FRONTEND_PORT"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    log_error "Failed to start Development Frontend"
    return 1
}

# Function to start AI improvement system
start_ai_system() {
    log_ai "Starting AI Improvement System..."
    cd "$PROJECT_ROOT"
    
    # Install AI system dependencies
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment for AI system..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install AI system requirements
    pip install gitpython psutil requests
    
    # Start AI system
    nohup python ai_improvement_system.py > "$LOG_DIR/ai_system.log" 2>&1 &
    echo $! > "$AI_SYSTEM_PID"
    
    # Wait for AI system to start
    sleep 5
    
    if is_process_running "$AI_SYSTEM_PID"; then
        log_success "AI Improvement System started"
        return 0
    else
        log_error "Failed to start AI Improvement System"
        return 1
    fi
}

# Function to stop all services
stop_all_services() {
    log_info "Stopping all services..."
    
    # Stop AI system
    if is_process_running "$AI_SYSTEM_PID"; then
        local pid=$(cat "$AI_SYSTEM_PID")
        kill $pid 2>/dev/null || true
        rm -f "$AI_SYSTEM_PID"
        log_info "AI System stopped"
    fi
    
    # Stop development services
    if is_process_running "$DEV_FRONTEND_PID"; then
        local pid=$(cat "$DEV_FRONTEND_PID")
        kill $pid 2>/dev/null || true
        rm -f "$DEV_FRONTEND_PID"
        log_info "Development Frontend stopped"
    fi
    
    if is_process_running "$DEV_BACKEND_PID"; then
        local pid=$(cat "$DEV_BACKEND_PID")
        kill $pid 2>/dev/null || true
        rm -f "$DEV_BACKEND_PID"
        log_info "Development Backend stopped"
    fi
    
    # Stop live services
    if is_process_running "$LIVE_FRONTEND_PID"; then
        local pid=$(cat "$LIVE_FRONTEND_PID")
        kill $pid 2>/dev/null || true
        rm -f "$LIVE_FRONTEND_PID"
        log_info "Live Frontend stopped"
    fi
    
    if is_process_running "$LIVE_BACKEND_PID"; then
        local pid=$(cat "$LIVE_BACKEND_PID")
        kill $pid 2>/dev/null || true
        rm -f "$LIVE_BACKEND_PID"
        log_info "Live Backend stopped"
    fi
    
    # Kill any remaining processes on our ports
    kill_port $LIVE_FRONTEND_PORT
    kill_port $LIVE_BACKEND_PORT
    kill_port $DEV_FRONTEND_PORT
    kill_port $DEV_BACKEND_PORT
    
    log_success "All services stopped"
}

# Function to show status
show_status() {
    echo -e "\n${CYAN}=== AI-Driven Video Scraper Status ===${NC}"
    echo
    
    # Live services
    echo -e "${GREEN}Live Services:${NC}"
    if is_process_running "$LIVE_BACKEND_PID"; then
        echo -e "  ✅ Backend: http://localhost:$LIVE_BACKEND_PORT"
    else
        echo -e "  ❌ Backend: Not running"
    fi
    
    if is_process_running "$LIVE_FRONTEND_PID"; then
        echo -e "  ✅ Frontend: http://localhost:$LIVE_FRONTEND_PORT"
    else
        echo -e "  ❌ Frontend: Not running"
    fi
    
    echo
    
    # Development services
    echo -e "${YELLOW}Development Services:${NC}"
    if is_process_running "$DEV_BACKEND_PID"; then
        echo -e "  ✅ Backend: http://localhost:$DEV_BACKEND_PORT"
    else
        echo -e "  ❌ Backend: Not running"
    fi
    
    if is_process_running "$DEV_FRONTEND_PID"; then
        echo -e "  ✅ Frontend: http://localhost:$DEV_FRONTEND_PORT"
    else
        echo -e "  ❌ Frontend: Not running"
    fi
    
    echo
    
    # AI system
    echo -e "${PURPLE}AI Improvement System:${NC}"
    if is_process_running "$AI_SYSTEM_PID"; then
        echo -e "  ✅ AI System: Running"
        if [ -f "$PROJECT_ROOT/APPROVAL_REQUESTED" ]; then
            echo -e "  🔔 Approval Requested: Yes"
        else
            echo -e "  🔔 Approval Requested: No"
        fi
    else
        echo -e "  ❌ AI System: Not running"
    fi
    
    echo
    
    # System health
    if [ -f "$PROJECT_ROOT/ai_system_status.json" ]; then
        echo -e "${BLUE}System Health:${NC}"
        cat "$PROJECT_ROOT/ai_system_status.json" | python3 -m json.tool 2>/dev/null || echo "  Unable to read health data"
    fi
}

# Function to show logs
show_logs() {
    echo -e "\n${CYAN}=== Recent Logs ===${NC}"
    echo
    
    if [ -f "$LOG_DIR/ai_system.log" ]; then
        echo -e "${PURPLE}AI System Logs (last 10 lines):${NC}"
        tail -10 "$LOG_DIR/ai_system.log"
        echo
    fi
    
    if [ -f "$LOG_DIR/live_backend.log" ]; then
        echo -e "${GREEN}Live Backend Logs (last 10 lines):${NC}"
        tail -10 "$LOG_DIR/live_backend.log"
        echo
    fi
    
    if [ -f "$LOG_DIR/live_frontend.log" ]; then
        echo -e "${GREEN}Live Frontend Logs (last 10 lines):${NC}"
        tail -10 "$LOG_DIR/live_frontend.log"
        echo
    fi
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            log_info "🚀 Starting AI-Driven Video Scraper with Continuous Improvement"
            log_info "================================================================"
            
            # Stop any existing services
            stop_all_services
            
            # Start live services first (protected)
            start_live_backend
            start_live_frontend
            
            # Start development environment
            start_dev_backend
            start_dev_frontend
            
            # Start AI improvement system
            start_ai_system
            
            log_success "🎉 All systems started successfully!"
            echo
            log_info "Live Site (Protected): http://localhost:$LIVE_FRONTEND_PORT"
            log_info "Development Site: http://localhost:$DEV_FRONTEND_PORT"
            log_info "Backend API: http://localhost:$LIVE_BACKEND_PORT/docs"
            log_info "AI System: Running in background"
            echo
            log_info "🤖 AI is continuously improving the application..."
            log_info "🔔 Approval button will appear when improvements are ready"
            echo
            log_info "Commands:"
            log_info "  ./start_ai_system.sh status  - Show system status"
            log_info "  ./start_ai_system.sh logs    - Show recent logs"
            log_info "  ./start_ai_system.sh stop    - Stop all services"
            echo
            ;;
        
        "stop")
            log_info "🛑 Stopping all services..."
            stop_all_services
            log_success "All services stopped"
            ;;
        
        "restart")
            log_info "🔄 Restarting all services..."
            stop_all_services
            sleep 2
            $0 start
            ;;
        
        "status")
            show_status
            ;;
        
        "logs")
            show_logs
            ;;
        
        "ai-status")
            if [ -f "$PROJECT_ROOT/ai_system_status.json" ]; then
                cat "$PROJECT_ROOT/ai_system_status.json" | python3 -m json.tool
            else
                echo "AI system status not available"
            fi
            ;;
        
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|ai-status}"
            echo
            echo "Commands:"
            echo "  start      - Start all services (default)"
            echo "  stop       - Stop all services"
            echo "  restart    - Restart all services"
            echo "  status     - Show system status"
            echo "  logs       - Show recent logs"
            echo "  ai-status  - Show AI system status"
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'log_info "Received interrupt signal"; stop_all_services; exit 0' INT TERM

# Run main function
main "$@" 