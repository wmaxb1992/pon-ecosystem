#!/bin/bash

# Enhanced Video Scraper with Continuous Improvement Engine
# PostgreSQL Database + Grok AI Integration

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
BACKEND_PORT=8000
FRONTEND_PORT=3000
IMPROVEMENT_ENGINE_PORT=5000
LOG_DIR="./logs"
PID_DIR="./pids"

# Create directories
mkdir -p $LOG_DIR $PID_DIR

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')]${NC} ⚠️  $1"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')]${NC} ❌ $1"
}

print_info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} ℹ️  $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} ✅ $1"
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
        print_warning "Killing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    # Python dependencies
    if [ ! -f "requirements.txt" ]; then
        print_warning "Creating requirements.txt..."
        cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-multipart==0.0.6
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
yt-dlp==2023.11.16
schedule==1.2.0
python-dotenv==1.0.0
aiofiles==23.2.1
pydantic==2.5.0
httpx==0.25.2
free-proxy==1.0.0
EOF
    fi
    
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Node.js dependencies
    if [ -d "frontend" ]; then
        print_info "Installing Node.js dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    print_success "Dependencies installed!"
}

# Function to setup PostgreSQL database
setup_database() {
    print_info "Setting up PostgreSQL database..."
    
    # Check if database config exists
    if [ ! -f "database_config.py" ]; then
        print_error "database_config.py not found!"
        return 1
    fi
    
    # Initialize database tables
    print_info "Initializing database tables..."
    python -c "
from database_config import init_db
from improvement_tracker import tracker
init_db()
tracker.init_database()
print('Database initialized successfully!')
"
    
    print_success "Database setup complete!"
}

# Function to start backend
start_backend() {
    print_info "Starting Enhanced Backend..."
    
    if check_port $BACKEND_PORT; then
        kill_port $BACKEND_PORT
    fi
    
    cd backend
    nohup python main_enhanced.py > ../$LOG_DIR/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../$PID_DIR/backend.pid
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    if check_port $BACKEND_PORT; then
        print_success "Backend started with PID: $BACKEND_PID"
        print_success "Backend is ready on http://localhost:$BACKEND_PORT"
    else
        print_error "Backend failed to start!"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_info "Starting Frontend..."
    
    if check_port $FRONTEND_PORT; then
        kill_port $FRONTEND_PORT
    fi
    
    cd frontend
    nohup npm run dev > ../$LOG_DIR/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../$PID_DIR/frontend.pid
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    if check_port $FRONTEND_PORT; then
        print_success "Frontend started with PID: $FRONTEND_PID"
        print_success "Frontend is ready on http://localhost:$FRONTEND_PORT"
    else
        print_warning "Frontend may still be starting..."
    fi
}

# Function to start continuous improvement engine
start_improvement_engine() {
    print_info "Starting Continuous Improvement Engine..."
    
    if check_port $IMPROVEMENT_ENGINE_PORT; then
        kill_port $IMPROVEMENT_ENGINE_PORT
    fi
    
    nohup python continuous_improvement_engine.py > $LOG_DIR/improvement_engine.log 2>&1 &
    ENGINE_PID=$!
    echo $ENGINE_PID > $PID_DIR/improvement_engine.pid
    
    print_success "Continuous Improvement Engine started with PID: $ENGINE_PID"
    print_info "Engine will monitor for improvements every 15 minutes"
    print_info "Codebase analysis every 30 minutes"
    print_info "Milestone generation every hour"
}

# Function to start all services
start_all() {
    print_status "🚀 Enhanced Video Scraper Startup Script"
    print_status "========================================"
    
    # Check if GROK_API_KEY is set
    if [ -z "$GROK_API_KEY" ]; then
        print_warning "GROK_API_KEY not set. Some AI features may be limited."
        print_info "Set GROK_API_KEY environment variable for full AI integration."
    else
        print_success "Grok API key detected - AI integration enabled!"
    fi
    
    # Install dependencies if needed
    if [ "$1" = "--install" ]; then
        install_dependencies
    fi
    
    # Setup database
    setup_database
    
    # Start services
    start_backend
    start_frontend
    start_improvement_engine
    
    # Start log monitoring
    print_info "Starting log monitoring..."
    print_info "Monitoring logs (Press Ctrl+C to stop)..."
    print_info "Frontend: http://localhost:$FRONTEND_PORT"
    print_info "Backend API: http://localhost:$BACKEND_PORT"
    print_info "Backend Docs: http://localhost:$BACKEND_PORT/docs"
    print_info "Improvement Engine: Running in background"
    
    # Monitor logs
    tail -f $LOG_DIR/backend.log $LOG_DIR/frontend.log $LOG_DIR/improvement_engine.log
}

# Function to stop all services
stop_all() {
    print_status "🛑 Stopping all services..."
    
    # Kill processes by PID files
    for pid_file in $PID_DIR/*.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            if ps -p $PID > /dev/null 2>&1; then
                print_info "Killing process $PID"
                kill -9 $PID 2>/dev/null || true
            fi
            rm -f "$pid_file"
        fi
    done
    
    # Kill processes by port
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    kill_port $IMPROVEMENT_ENGINE_PORT
    
    print_success "All services stopped"
}

# Function to restart all services
restart_all() {
    print_status "🔄 Restarting all services..."
    stop_all
    sleep 2
    start_all
}

# Function to show status
show_status() {
    print_status "📊 Service Status"
    print_status "================="
    
    # Backend status
    if check_port $BACKEND_PORT; then
        print_success "Backend: Running on port $BACKEND_PORT"
    else
        print_error "Backend: Not running"
    fi
    
    # Frontend status
    if check_port $FRONTEND_PORT; then
        print_success "Frontend: Running on port $FRONTEND_PORT"
    else
        print_error "Frontend: Not running"
    fi
    
    # Improvement engine status
    if [ -f "$PID_DIR/improvement_engine.pid" ]; then
        PID=$(cat "$PID_DIR/improvement_engine.pid")
        if ps -p $PID > /dev/null 2>&1; then
            print_success "Improvement Engine: Running (PID: $PID)"
        else
            print_error "Improvement Engine: Not running"
        fi
    else
        print_error "Improvement Engine: Not running"
    fi
    
    # Show recent logs
    echo ""
    print_info "Recent Backend Logs:"
    tail -n 5 $LOG_DIR/backend.log 2>/dev/null || echo "No backend logs"
    
    echo ""
    print_info "Recent Frontend Logs:"
    tail -n 5 $LOG_DIR/frontend.log 2>/dev/null || echo "No frontend logs"
    
    echo ""
    print_info "Recent Improvement Engine Logs:"
    tail -n 5 $LOG_DIR/improvement_engine.log 2>/dev/null || echo "No engine logs"
}

# Function to show improvement status
show_improvements() {
    print_status "📋 Improvement Status"
    print_status "====================="
    
    python -c "
from improvement_tracker import tracker
tracker.print_master_checklist()
"
}

# Function to run improvement engine in interactive mode
run_improvement_engine() {
    print_status "🎮 Starting Improvement Engine in Interactive Mode"
    python continuous_improvement_engine.py
}

# Function to analyze codebase
analyze_codebase() {
    print_status "🔍 Analyzing Codebase"
    print_status "===================="
    
    python -c "
from codebase_analyzer import analyzer
report = analyzer.generate_codebase_report()
print(report)
"
}

# Function to show help
show_help() {
    echo "Enhanced Video Scraper Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start [--install]    Start all services (with optional dependency installation)"
    echo "  stop                 Stop all services"
    echo "  restart              Restart all services"
    echo "  status               Show service status"
    echo "  improvements         Show improvement status"
    echo "  engine               Run improvement engine in interactive mode"
    echo "  analyze              Analyze codebase"
    echo "  install              Install dependencies"
    echo "  help                 Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GROK_API_KEY         Grok API key for AI integration"
    echo ""
    echo "Examples:"
    echo "  $0 start --install   Start with dependency installation"
    echo "  $0 status            Check service status"
    echo "  $0 improvements      View improvement checklist"
}

# Main script logic
case "${1:-start}" in
    start)
        start_all $2
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        show_status
        ;;
    improvements)
        show_improvements
        ;;
    engine)
        run_improvement_engine
        ;;
    analyze)
        analyze_codebase
        ;;
    install)
        install_dependencies
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 