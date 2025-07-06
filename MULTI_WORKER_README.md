# Multi-Worker AI System Documentation

## Overview

This is a distributed AI worker system that allows you to run multiple Grok AI workers simultaneously using Celery and Redis. Each worker specializes in different tasks:

- **Worker 1 (Code Worker)**: File editing, code generation, bug fixes
- **Worker 2 (Quality Worker)**: Code review, linting, security checks
- **Worker 3 (Memory Worker)**: Knowledge indexing, pattern recognition, organization

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Terminal Interface                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │    Edit     │  │   Create    │  │   Review    │       │
│  │  Commands   │  │  Commands   │  │  Commands   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Worker Coordinator                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │    Task     │  │   Queue     │  │   Result    │       │
│  │ Assignment  │  │ Management  │  │  Tracking   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                       Redis Broker                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ code_queue  │  │quality_queue│  │memory_queue │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      Celery Workers                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Worker 1  │  │   Worker 2  │  │   Worker 3  │       │
│  │    Code     │  │   Quality   │  │   Memory    │       │
│  │ Generation  │  │ Assurance   │  │ Management  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                 │                 │             │
│         ▼                 ▼                 ▼             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Grok AI   │  │   Grok AI   │  │   Grok AI   │       │
│  │   Client    │  │   Client    │  │   Client    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- Redis server
- Grok API key

### Quick Setup
```bash
# Run the setup script
./setup_multi_workers.sh

# Configure your API key
nano config/multi_worker.env
# Add your GROK_API_KEY
```

### Manual Setup
```bash
# Install Redis
brew install redis  # macOS
# or
sudo apt install redis-server  # Ubuntu

# Install Python dependencies
pip install celery redis

# Start Redis
redis-server --daemonize yes
```

## Usage

### 1. Start the Workers
```bash
./start_workers.sh
```

This starts:
- 2 Code Workers (for parallel code generation)
- 1 Quality Worker (for code review)
- 1 Memory Worker (for indexing and organization)

### 2. Start the Terminal Interface
```bash
python3 multi_worker_terminal.py
```

### 3. Use Commands

#### File Operations
```bash
# Edit an existing file
edit src/main.py "add error handling to the login function"

# Create a new file
create utils/helpers.py "utility functions for data validation"

# Review code quality
review src/main.py

# Run full pipeline (all workers)
pipeline frontend/app.js "add dark mode toggle feature"
```

#### Worker Management
```bash
# Show worker status
workers

# Real-time dashboard
dashboard

# View active tasks
tasks

# System status
status
```

#### AI Operations
```bash
# Search indexed knowledge
search "authentication patterns"

# General AI request (auto-routed to appropriate worker)
"How do I implement JWT authentication in Python?"
```

## Worker Specializations

### Worker 1: Code Generation & Editing
**Specializes in:**
- Creating new files and functions
- Editing existing code
- Implementing features
- Bug fixes and refactoring
- Code optimization

**Queue:** `code_queue`
**Concurrency:** 2 processes (for parallel code generation)

**Example tasks:**
```bash
edit src/auth.py "implement JWT token validation"
create tests/test_auth.py "unit tests for authentication module"
```

### Worker 2: Quality Assurance & Linting
**Specializes in:**
- Code review and analysis
- Syntax and style checking
- Security vulnerability scanning
- Performance optimization suggestions
- Best practices validation

**Queue:** `quality_queue`
**Concurrency:** 1 process (focused analysis)

**Automatically triggered by:**
- Pipeline operations
- Manual review commands
- Code completion workflows

**Checks performed:**
- Syntax errors
- Style violations (PEP8, etc.)
- Security issues
- Performance bottlenecks
- Code complexity
- Documentation coverage

### Worker 3: Memory Management & Indexing
**Specializes in:**
- Indexing code patterns and solutions
- Learning from previous tasks
- Organizing knowledge base
- Pattern recognition
- Search and retrieval

**Queue:** `memory_queue`
**Concurrency:** 1 process (maintains consistency)

**Operations:**
- `index`: Store new code and patterns
- `search`: Find relevant previous solutions
- `organize`: Clean up and optimize knowledge base
- `learn`: Extract patterns from completed tasks

## Pipeline Workflow

When you run a pipeline command, here's what happens:

```bash
pipeline src/app.py "add user authentication"
```

1. **Worker 1** generates/modifies the code
2. **Worker 2** reviews the code for quality and issues
3. **Worker 2** suggests fixes if issues are found
4. **Worker 1** applies fixes if needed
5. **Worker 3** indexes the new knowledge and patterns
6. **Result** is returned with quality score and completion status

## Monitoring

### Real-time Monitoring
```bash
# Worker dashboard
dashboard

# Monitor script
./monitor_workers.sh

# Celery monitoring (web interface)
celery -A ai_multi_worker flower
```

### Queue Status
```bash
# Active workers
celery -A ai_multi_worker status

# Queue lengths
celery -A ai_multi_worker inspect active_queues

# Active tasks
celery -A ai_multi_worker inspect active
```

## Configuration

Edit `config/multi_worker.env` to customize:

- **API Settings**: Grok API key and model configuration
- **Worker Settings**: Concurrency and timeout settings
- **Queue Settings**: Queue names and routing
- **Quality Settings**: Review thresholds and auto-fix behavior
- **Memory Settings**: Indexing and learning parameters

## Advanced Usage

### Custom Worker Assignment
```python
# In Python code
from ai_multi_worker import coordinator

# Assign specific tasks
code_task = coordinator.assign_code_task('edit_file', 'description', 'file.py')
quality_task = coordinator.assign_quality_task(code_content, 'file.py', code_task)
memory_task = coordinator.assign_memory_task('index', data)

# Wait for results
result = coordinator.wait_for_task(code_task, timeout=120)
```

### Batch Processing
```bash
# Process multiple files
for file in src/*.py; do
    pipeline "$file" "optimize for performance"
done
```

### Integration with Existing Workflows
```bash
# Git hook integration
git diff --name-only | while read file; do
    review "$file"
done
```

## Troubleshooting

### Workers Not Starting
```bash
# Check Redis
redis-cli ping

# Check Python dependencies
pip list | grep celery

# Check for port conflicts
lsof -i :6379
```

### Tasks Hanging
```bash
# Restart workers
./stop_workers.sh
./start_workers.sh

# Clear Redis queues
redis-cli flushdb
```

### Quality Issues
```bash
# Check worker logs
tail -f celery.log

# Verify Grok API key
echo $GROK_API_KEY
```

## Performance Tuning

### Worker Concurrency
Adjust in `config/multi_worker.env`:
```bash
CODE_WORKER_CONCURRENCY=4    # More parallel code generation
QUALITY_WORKER_CONCURRENCY=2 # Parallel quality checks
```

### Memory Management
```bash
MEMORY_MAX_ENTRIES=50000     # Larger knowledge base
MEMORY_CLEANUP_INTERVAL=1800 # More frequent cleanup
```

### Task Optimization
```bash
WORKER_PREFETCH_MULTIPLIER=2 # Process more tasks in advance
WORKER_MAX_TASKS_PER_CHILD=500 # Restart workers more frequently
```

## Security

The system includes several security features:

- **API Key Protection**: Stored in environment variables
- **Code Scanning**: Automatic security vulnerability detection
- **Input Validation**: File type and size restrictions
- **Process Isolation**: Each worker runs in separate process

## Integration with VS Code

The multi-worker system complements VS Code AI:

- **Terminal AI (This System)**: Handles system-level tasks, orchestration, and bulk operations
- **VS Code AI**: Handles real-time coding assistance within the IDE

Use the terminal for:
- Batch file processing
- System-wide refactoring
- Quality assurance workflows
- Knowledge management

Use VS Code AI for:
- Real-time code completion
- Interactive debugging
- Single-file editing
- Immediate coding assistance

## Future Enhancements

- **Web Dashboard**: Browser-based monitoring interface
- **Plugin System**: Custom worker types and tasks
- **Auto-scaling**: Dynamic worker allocation based on load
- **Machine Learning**: Improved pattern recognition and suggestions
- **Integration APIs**: REST/GraphQL APIs for external integration
