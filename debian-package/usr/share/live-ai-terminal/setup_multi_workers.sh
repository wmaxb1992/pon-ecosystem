#!/bin/bash
set -e

# Multi-Worker AI System Setup
# ============================

echo "🚀 Setting up Multi-Worker AI System"
echo "===================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "📦 Installing Redis..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install redis
        else
            echo "❌ Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y redis-server
    else
        echo "❌ Unsupported OS. Please install Redis manually."
        exit 1
    fi
else
    echo "✅ Redis already installed"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install celery redis

# Add to existing requirements.txt
echo "
# Multi-Worker AI System
celery>=5.3.0
redis>=4.5.0
kombu>=5.3.0
billiard>=4.1.0
" >> requirements.txt

echo "✅ Dependencies installed"

# Create configuration directory
mkdir -p config

# Create Celery configuration
cat > config/celery_config.py << 'EOF'
"""
Celery Configuration for Multi-Worker AI System
"""

# Broker settings
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Worker settings
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 1000

# Queue routing
task_routes = {
    'ai_workers.code_worker': {'queue': 'code_queue'},
    'ai_workers.quality_worker': {'queue': 'quality_queue'},
    'ai_workers.memory_worker': {'queue': 'memory_queue'},
}

# Queue definitions
task_default_queue = 'default'
task_queues = {
    'code_queue': {
        'exchange': 'code',
        'exchange_type': 'direct',
        'routing_key': 'code',
    },
    'quality_queue': {
        'exchange': 'quality',
        'exchange_type': 'direct',
        'routing_key': 'quality',
    },
    'memory_queue': {
        'exchange': 'memory',
        'exchange_type': 'direct',
        'routing_key': 'memory',
    },
}

# Monitoring
worker_send_task_events = True
task_send_sent_event = True

# Security
worker_hijack_root_logger = False
worker_log_color = True
EOF

# Create worker startup scripts
cat > start_workers.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Multi-Worker AI System"
echo "================================="

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    echo "🔴 Starting Redis server..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis is running"

# Start Celery workers
echo "🤖 Starting AI Workers..."

# Worker 1: Code Generation (2 processes)
echo "Starting Code Workers..."
celery -A ai_multi_worker worker --loglevel=info --queues=code_queue --concurrency=2 --hostname=code_worker@%h &
CODE_WORKER_PID=$!

# Worker 2: Quality Assurance (1 process)
echo "Starting Quality Worker..."
celery -A ai_multi_worker worker --loglevel=info --queues=quality_queue --concurrency=1 --hostname=quality_worker@%h &
QUALITY_WORKER_PID=$!

# Worker 3: Memory Management (1 process)
echo "Starting Memory Worker..."
celery -A ai_multi_worker worker --loglevel=info --queues=memory_queue --concurrency=1 --hostname=memory_worker@%h &
MEMORY_WORKER_PID=$!

# Save PIDs for later cleanup
echo $CODE_WORKER_PID > .code_worker.pid
echo $QUALITY_WORKER_PID > .quality_worker.pid
echo $MEMORY_WORKER_PID > .memory_worker.pid

echo ""
echo "✅ All workers started!"
echo "🖥️  Monitor with: celery -A ai_multi_worker flower"
echo "🔍 View status: celery -A ai_multi_worker status"
echo "🛑 Stop workers: ./stop_workers.sh"
echo ""
echo "🚀 Start terminal: python3 multi_worker_terminal.py"

# Keep script running
wait
EOF

cat > stop_workers.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Multi-Worker AI System"
echo "================================="

# Stop workers using PIDs
if [ -f .code_worker.pid ]; then
    kill $(cat .code_worker.pid) 2>/dev/null || true
    rm .code_worker.pid
fi

if [ -f .quality_worker.pid ]; then
    kill $(cat .quality_worker.pid) 2>/dev/null || true
    rm .quality_worker.pid
fi

if [ -f .memory_worker.pid ]; then
    kill $(cat .memory_worker.pid) 2>/dev/null || true
    rm .memory_worker.pid
fi

# Kill any remaining Celery processes
pkill -f "celery.*ai_multi_worker" || true

echo "✅ All workers stopped"
EOF

# Make scripts executable
chmod +x start_workers.sh stop_workers.sh

# Create monitoring script
cat > monitor_workers.sh << 'EOF'
#!/bin/bash

echo "📊 Multi-Worker AI System Monitor"
echo "================================"

# Check Redis
if pgrep redis-server > /dev/null; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Not running"
fi

# Check Celery workers
echo ""
echo "🤖 Worker Status:"
celery -A ai_multi_worker status 2>/dev/null || echo "❌ No workers found"

echo ""
echo "📈 Queue Status:"
celery -A ai_multi_worker inspect active_queues 2>/dev/null || echo "❌ Cannot get queue status"

echo ""
echo "📋 Active Tasks:"
celery -A ai_multi_worker inspect active 2>/dev/null || echo "❌ Cannot get active tasks"
EOF

chmod +x monitor_workers.sh

# Create systemd service file (optional)
cat > multi-worker-ai.service << 'EOF'
[Unit]
Description=Multi-Worker AI System
After=network.target redis.service

[Service]
Type=forking
User=root
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/start_workers.sh
ExecStop=/path/to/your/project/stop_workers.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Multi-Worker AI System setup complete!"
echo "========================================"
echo ""
echo "📋 Next steps:"
echo "  1. Start the system: ./start_workers.sh"
echo "  2. Open new terminal and run: python3 multi_worker_terminal.py"
echo "  3. Monitor workers: ./monitor_workers.sh"
echo ""
echo "📖 Available commands in terminal:"
echo "  - edit <file> <description>     # Edit files with AI"
echo "  - create <file> <description>   # Create new files"
echo "  - review <file>                 # Quality review"
echo "  - pipeline <file> <description> # Full AI pipeline"
echo "  - search <query>                # Search knowledge"
echo "  - workers                       # Show worker status"
echo ""
echo "🎯 Example usage:"
echo "  edit src/main.py 'add error handling'"
echo "  create utils/helpers.py 'utility functions'"
echo "  pipeline app.js 'add dark mode feature'"
echo ""
