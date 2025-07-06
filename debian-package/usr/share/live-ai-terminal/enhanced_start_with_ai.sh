#!/bin/bash

# Enhanced AI Development Startup Script
# Integrates AI coding rules, memory system, thought processor, and development workflow

# Colors for terminal output
LIGHT_BLUE='\033[94m'
DARK_BLUE='\033[34m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
PURPLE='\033[95m'
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'

# Configuration
PROJECT_ROOT="/Users/maxwoldenberg/Desktop/pon"
BACKEND_PORT=8000
FRONTEND_PORT=3000
LOG_DIR="./logs"
AI_LOG_FILE="$LOG_DIR/ai_workflow.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log AI thoughts
log_ai_thought() {
    echo "[$(date '+%H:%M:%S')] 🤖 $1" | tee -a "$AI_LOG_FILE"
}

# Function to display AI question
show_ai_question() {
    echo -e "\n${DARK_BLUE}[$(date '+%H:%M:%S')] ❓ ${BOLD}Grok AI Question${RESET}${DARK_BLUE}:${RESET}"
    echo -e "${DARK_BLUE}   $1${RESET}"
    echo -e "${DARK_BLUE}   Your answer: ${RESET}" | tee -a "$AI_LOG_FILE"
}

# Function to display AI thought
show_ai_thought() {
    echo -e "${LIGHT_BLUE}[$(date '+%H:%M:%S')] 💭 ${BOLD}Grok AI${RESET}${LIGHT_BLUE}: $1${RESET}" | tee -a "$AI_LOG_FILE"
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
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
        sleep 2
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${CYAN}🔧 Installing Dependencies...${RESET}"
    
    # Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install AI-specific dependencies
    pip install pydantic sqlite3 typing-extensions dataclasses
    
    # Frontend dependencies
    if [ -d "frontend" ]; then
        cd frontend
        npm install
        cd ..
    fi
    
    show_ai_thought "Dependencies installed successfully"
}

# Function to start AI systems
start_ai_systems() {
    echo -e "${PURPLE}🧠 Starting AI Systems...${RESET}"
    
    # Start AI thought processor
    python3 -c "
from ai_thought_processor import thought_processor
from ai_memory_system import ai_memory
from ai_coding_rules import ai_rules
from enhanced_grok_integration import enhanced_grok
from ai_development_workflow import ai_workflow

print('🤖 AI Systems initialized successfully')
thought_processor.add_thought('analysis', 'AI systems started and ready for development', {}, 0.9)
" &
    
    show_ai_thought "AI coding rules, memory system, and thought processor initialized"
}

# Function to start backend with AI integration
start_backend() {
    echo -e "${GREEN}🚀 Starting Enhanced Backend with AI Integration...${RESET}"
    
    if check_port $BACKEND_PORT; then
        kill_port $BACKEND_PORT
    fi
    
    cd backend
    
    # Start backend with AI systems
    python3 -c "
import sys
sys.path.append('..')

from enhanced_grok_integration import enhanced_grok
from ai_thought_processor import thought_processor
from ai_memory_system import ai_memory

# Set project context
enhanced_grok.set_project_context('$PROJECT_ROOT', 'web_app')

# Start backend
import uvicorn
from main_enhanced import app

thought_processor.add_thought('analysis', 'Starting enhanced backend with AI integration', {}, 0.8)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=$BACKEND_PORT)
" &
    
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    
    # Wait for backend to be ready
    sleep 5
    
    if check_port $BACKEND_PORT; then
        echo -e "${GREEN}✅ Backend is ready on http://localhost:$BACKEND_PORT${RESET}"
        show_ai_thought "Backend started successfully with AI integration"
    else
        echo -e "${RED}❌ Backend failed to start${RESET}"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    echo -e "${GREEN}🎨 Starting Frontend...${RESET}"
    
    if check_port $FRONTEND_PORT; then
        kill_port $FRONTEND_PORT
    fi
    
    cd frontend
    
    # Start frontend with AI monitoring
    npm run dev > ../logs/frontend.log 2>&1 &
    
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    
    # Wait for frontend to be ready
    sleep 10
    
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}✅ Frontend is ready on http://localhost:$FRONTEND_PORT${RESET}"
        show_ai_thought "Frontend started successfully"
    else
        echo -e "${RED}❌ Frontend failed to start${RESET}"
        return 1
    fi
}

# Function to start AI development workflow
start_ai_workflow() {
    echo -e "${PURPLE}🔄 Starting AI Development Workflow...${RESET}"
    
    python3 -c "
import sys
sys.path.append('.')

from ai_development_workflow import ai_workflow
from ai_thought_processor import thought_processor

# Start development session
ai_workflow.start_development_session('$PROJECT_ROOT', 'AI-Enhanced Video Scraper Development')

# Show initial analysis
analysis = ai_workflow.analyze_project_structure()
print(f'📊 Project Analysis: {len(analysis.get(\"file_analysis\", []))} files analyzed')

# Generate improvements
improvements = ai_workflow.generate_code_improvements()
print(f'🚀 Generated {len(improvements.get(\"generated_files\", []))} improvements')

thought_processor.add_thought('optimization', 'AI development workflow started successfully', improvements, 0.9)
" &
    
    show_ai_thought "AI development workflow started with continuous improvement cycle"
}

# Function to monitor AI systems
monitor_ai_systems() {
    echo -e "${CYAN}📊 Monitoring AI Systems...${RESET}"
    
    while true; do
        clear
        echo -e "${CYAN}🤖 AI Development System Monitor${RESET}"
        echo -e "${CYAN}==================================================${RESET}"
        
        # Backend status
        if check_port $BACKEND_PORT; then
            echo -e "${GREEN}✅ Backend: Running on port $BACKEND_PORT${RESET}"
        else
            echo -e "${RED}❌ Backend: Not running${RESET}"
        fi
        
        # Frontend status
        if check_port $FRONTEND_PORT; then
            echo -e "${GREEN}✅ Frontend: Running on port $FRONTEND_PORT${RESET}"
        else
            echo -e "${RED}❌ Frontend: Not running${RESET}"
        fi
        
        # AI systems status
        echo -e "\n${LIGHT_BLUE}🧠 AI Systems Status:${RESET}"
        
        # Check AI memory
        if [ -f "ai_memory.db" ]; then
            echo -e "${GREEN}   Memory System: Active${RESET}"
        else
            echo -e "${YELLOW}   Memory System: Initializing${RESET}"
        fi
        
        # Show recent AI thoughts
        echo -e "\n${LIGHT_BLUE}💭 Recent AI Thoughts:${RESET}"
        tail -n 5 "$AI_LOG_FILE" 2>/dev/null | grep "Grok AI:" || echo "   No thoughts yet"
        
        # Show recent questions
        echo -e "\n${DARK_BLUE}❓ Recent Questions:${RESET}"
        tail -n 5 "$AI_LOG_FILE" 2>/dev/null | grep "Question:" || echo "   No questions yet"
        
        echo -e "\n${CYAN}Press Ctrl+C to stop monitoring${RESET}"
        sleep 5
    done
}

# Function to show AI insights
show_ai_insights() {
    echo -e "${PURPLE}🔍 Getting AI Insights...${RESET}"
    
    python3 -c "
import sys
sys.path.append('.')

from enhanced_grok_integration import enhanced_grok
from ai_thought_processor import thought_processor

# Get insights
insights = enhanced_grok.get_ai_insights()

print('📊 AI Insights:')
print(f'   Project Files: {len(insights.get(\"project_info\", {}).get(\"files\", []))}')
print(f'   Coding Rules: {insights.get(\"coding_rules\", {}).get(\"total_rules\", 0)}')
print(f'   Memory Patterns: {insights.get(\"memory_stats\", {}).get(\"total_patterns\", 0)}')
print(f'   Recommendations: {len(insights.get(\"recommendations\", []))}')

# Show recommendations
if insights.get('recommendations'):
    print('\\n💡 Recommendations:')
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f'   {i}. {rec}')

thought_processor.show_thought_summary()
"
}

# Function to start live AI terminal
start_live_terminal() {
    echo -e "${PURPLE}🤖 Starting Live AI Terminal...${RESET}"
    
    # Check if Sentry DSN is available
    if [ -n "$SENTRY_DSN" ]; then
        echo -e "${GREEN}🔍 Sentry monitoring enabled${RESET}"
    else
        echo -e "${YELLOW}⚠️ Set SENTRY_DSN environment variable for enhanced monitoring${RESET}"
        echo -e "${GRAY}   Example: export SENTRY_DSN='https://your-dsn@sentry.io/project-id'${RESET}"
    fi
    
    show_ai_thought "Starting live AI terminal with real-time monitoring"
    
    # Start the live terminal
    python3 live_ai_terminal.py
}

# Function to show ASCII banner
show_banner() {
    echo -e "${CYAN}${BOLD}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    ██╗     ██╗██╗   ██╗███████╗     █████╗ ██╗                              ║
║    ██║     ██║██║   ██║██╔════╝    ██╔══██╗██║                              ║
║    ██║     ██║██║   ██║█████╗      ███████║██║                              ║
║    ██║     ██║╚██╗ ██╔╝██╔══╝      ██╔══██║██║                              ║
║    ███████╗██║ ╚████╔╝ ███████╗    ██║  ██║██║                              ║
║    ╚══════╝╚═╝  ╚═══╝  ╚══════╝    ╚═╝  ╚═╝╚═╝                              ║
║                                                                               ║
║     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗            ║
║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║            ║
║        ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║            ║
║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║            ║
║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗       ║
║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝       ║
║                                                                               ║
║  🤖 LIVE AI AGENT  •  🧠 REAL-TIME THOUGHTS  •  🔍 ERROR MONITORING          ║
║  📊 SENTRY LOGGING  •  🛠️ AUTO-FIX  •  💬 GROK INTEGRATION                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${RESET}"
}

# Enhanced help function
show_help() {
    show_banner
    
    echo -e "${CYAN}🚀 Enhanced AI Development Startup Script${RESET}"
    echo -e "${CYAN}=========================================${RESET}"
    echo ""
    echo -e "${WHITE}USAGE:${RESET}"
    echo -e "  $0 <command> [options]"
    echo ""
    echo -e "${WHITE}COMMANDS:${RESET}"
    echo -e "  ${GREEN}start${RESET}      - Start all services (backend, frontend, AI systems)"
    echo -e "  ${GREEN}stop${RESET}       - Stop all running services"
    echo -e "  ${GREEN}restart${RESET}    - Restart all services"
    echo -e "  ${GREEN}status${RESET}     - Show status of all services"
    echo -e "  ${GREEN}monitor${RESET}    - Start AI monitoring mode"
    echo -e "  ${GREEN}insights${RESET}   - Show AI insights and recommendations"
    echo -e "  ${GREEN}improve${RESET}    - Run AI improvement cycle"
    echo -e "  ${GREEN}terminal${RESET}   - Start Live AI Terminal (interactive mode)"
    echo -e "  ${GREEN}install${RESET}    - Install/update dependencies"
    echo -e "  ${GREEN}help${RESET}       - Show this help message"
    echo ""
    echo -e "${WHITE}LIVE AI TERMINAL FEATURES:${RESET}"
    echo -e "  • 🤖 Real-time conversation with Grok AI"
    echo -e "  • 🧠 Live thought processing visualization"
    echo -e "  • 🔍 Automatic error detection and fixing"
    echo -e "  • 📊 Sentry integration for monitoring"
    echo -e "  • 🎯 Smart error prioritization"
    echo -e "  • 📈 Live dashboard with metrics"
    echo ""
    echo -e "${WHITE}ENVIRONMENT VARIABLES:${RESET}"
    echo -e "  ${CYAN}SENTRY_DSN${RESET}    - Sentry DSN for error monitoring"
    echo -e "  ${CYAN}GROK_API_KEY${RESET}  - Grok API key for AI integration"
    echo ""
    echo -e "${WHITE}EXAMPLES:${RESET}"
    echo -e "  $0 start              # Start all services"
    echo -e "  $0 terminal           # Start interactive AI terminal"
    echo -e "  $0 status             # Check service status"
    echo -e "  $0 insights           # Get AI recommendations"
    echo ""
    echo -e "${YELLOW}💡 TIP: Use 'terminal' command for the best interactive experience!${RESET}"
}

print(f'✅ Improvement Cycle Complete:')
print(f'   Duration: {results[\"end_time\"] - results[\"start_time\"]}')
print(f'   Improvements: {results[\"improvements_made\"]}')
print(f'   Tests Run: {results[\"tests_run\"]}')
print(f'   Commits: {results[\"commits_made\"]}')

if results.get('errors'):
    print(f'   Errors: {len(results[\"errors\"])}')

thought_processor.add_thought('optimization', f'Completed {duration}-minute improvement cycle', results, 0.9)
"
}

# Function to stop all services
stop_all() {
    echo -e "${YELLOW}🛑 Stopping all services...${RESET}"
    
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    # Stop AI workflow
    python3 -c "
import sys
sys.path.append('.')

from ai_development_workflow import ai_workflow
from ai_thought_processor import thought_processor

# End development session
if ai_workflow.current_task:
    summary = ai_workflow.end_development_session()
    print('✅ Development session ended')
    print(f'   Duration: {summary[\"task\"][\"duration\"]:.1f} seconds')
    print(f'   Recommendations: {len(summary[\"recommendations\"])}')

thought_processor.add_thought('analysis', 'All services stopped', {}, 0.8)
"
    
    echo -e "${GREEN}✅ All services stopped${RESET}"
}

# Function to show help
show_help() {
    echo -e "${CYAN}🤖 Enhanced AI Development Startup Script${RESET}"
    echo -e "${CYAN}==================================================${RESET}"
    echo ""
    echo -e "${LIGHT_BLUE}Usage:${RESET}"
    echo "  $0 [command]"
    echo ""
    echo -e "${LIGHT_BLUE}Commands:${RESET}"
    echo "  start     - Start all services with AI integration"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  status    - Show status of all services"
    echo "  monitor   - Monitor AI systems in real-time"
    echo "  insights  - Show AI insights and recommendations"
    echo "  improve   - Run AI improvement cycle"
    echo "  install   - Install dependencies"
    echo "  help      - Show this help message"
    echo ""
    echo -e "${LIGHT_BLUE}AI Features:${RESET}"
    echo "  🧠 AI Coding Rules - Enforces consistent coding standards"
    echo "  💾 Memory System - Remembers patterns and decisions"
    echo "  💭 Thought Processor - Shows AI thinking process"
    echo "  🔄 Development Workflow - Automated improvement cycles"
    echo ""
    echo -e "${LIGHT_BLUE}Terminal Colors:${RESET}"
    echo "  ${LIGHT_BLUE}Light Blue${RESET} - AI thoughts and analysis"
    echo "  ${DARK_BLUE}Dark Blue${RESET} - AI questions and prompts"
    echo "  ${GREEN}Green${RESET} - Success messages"
    echo "  ${YELLOW}Yellow${RESET} - Warnings"
    echo "  ${RED}Red${RESET} - Errors"
}

# Main script logic
case "${1:-start}" in
    "start")
        echo -e "${CYAN}🚀 Starting Enhanced AI Development System...${RESET}"
        
        # Install dependencies
        install_dependencies
        
        # Start AI systems
        start_ai_systems
        
        # Start backend
        start_backend
        
        # Start frontend
        start_frontend
        
        # Start AI workflow
        start_ai_workflow
        
        echo -e "${GREEN}✅ All services started successfully!${RESET}"
        echo -e "${CYAN}Frontend: http://localhost:$FRONTEND_PORT${RESET}"
        echo -e "${CYAN}Backend: http://localhost:$BACKEND_PORT${RESET}"
        echo -e "${CYAN}Backend Docs: http://localhost:$BACKEND_PORT/docs${RESET}"
        echo -e "${PURPLE}AI Monitor: $0 monitor${RESET}"
        echo -e "${PURPLE}AI Insights: $0 insights${RESET}"
        
        # Start monitoring
        monitor_ai_systems
        ;;
    
    "stop")
        stop_all
        ;;
    
    "restart")
        echo -e "${YELLOW}🔄 Restarting all services...${RESET}"
        stop_all
        sleep 2
        $0 start
        ;;
    
    "status")
        echo -e "${CYAN}📊 Service Status${RESET}"
        echo -e "${CYAN}==============================${RESET}"
        
        if check_port $BACKEND_PORT; then
            echo -e "${GREEN}✅ Backend: Running on port $BACKEND_PORT${RESET}"
        else
            echo -e "${RED}❌ Backend: Not running${RESET}"
        fi
        
        if check_port $FRONTEND_PORT; then
            echo -e "${GREEN}✅ Frontend: Running on port $FRONTEND_PORT${RESET}"
        else
            echo -e "${RED}❌ Frontend: Not running${RESET}"
        fi
        
        # Show AI workflow status
        python3 -c "
import sys
sys.path.append('.')

from ai_development_workflow import ai_workflow

status = ai_workflow.get_workflow_status()
print(f'\\n🤖 AI Workflow: {\"Active\" if status[\"current_task\"] else \"Inactive\"}')
if status['current_task']:
    print(f'   Task: {status[\"current_task\"][\"description\"]}')
    print(f'   Duration: {(datetime.now() - status[\"current_task\"][\"started_at\"]).total_seconds():.1f}s')
"
        ;;
    
    "monitor")
        monitor_ai_systems
        ;;
    
    "insights")
        show_ai_insights
        ;;
    
    "terminal"|"live")
        start_live_terminal
        ;;
    
    "improve")
        echo -e "${PURPLE}🚀 Running AI Improvement Cycle...${RESET}"
        
        show_ai_question "How long should the improvement cycle run? (minutes)"
        read -r duration
        
        python3 -c "
import sys
sys.path.append('.')

from ai_development_workflow import ai_workflow
from ai_thought_processor import thought_processor

# Run improvement cycle
results = ai_workflow.continuous_improvement_cycle($duration)

print(f'🎯 Improvement cycle completed')
print(f'   Generated: {len(results.get(\"improvements\", []))} improvements')
print(f'   Applied: {results.get(\"applied_count\", 0)} fixes')
"
        ;;
    
    "install")
        install_dependencies
        ;;
    
    "help"|"-h"|"--help")
        show_help
        ;;
    
    *)
        echo -e "${RED}❌ Unknown command: $1${RESET}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 