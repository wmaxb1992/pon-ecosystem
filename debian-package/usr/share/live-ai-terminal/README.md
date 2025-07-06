# Live AI Terminal - Debian Package

## Overview
Live AI Terminal is a self-improving, AI-powered terminal interface that provides:
- Real-time conversation with Grok AI
- Automatic error detection and fixing
- System monitoring and log analysis
- Self-improvement capabilities
- Orchestration of multi-service applications

## Installation

### From Debian Package
```bash
sudo dpkg -i live-ai-terminal_1.0.0_all.deb
sudo apt-get install -f  # Install dependencies if needed
```

### Manual Setup
```bash
# Clone or extract the package contents
sudo cp -r usr/share/live-ai-terminal /usr/share/
sudo cp usr/local/bin/live-ai-terminal /usr/local/bin/
sudo cp etc/systemd/system/live-ai-terminal.service /etc/systemd/system/
sudo chmod +x /usr/local/bin/live-ai-terminal
sudo systemctl daemon-reload
```

## Configuration

1. Create configuration directory:
   ```bash
   mkdir -p ~/.config/live-ai-terminal
   ```

2. Copy and customize configuration:
   ```bash
   cp /usr/share/live-ai-terminal/config.template.env ~/.config/live-ai-terminal/config.env
   ```

3. Edit `~/.config/live-ai-terminal/config.env` with your settings:
   - Add your Grok API key
   - Configure Sentry DSN (optional)
   - Adjust system paths and settings

## Usage

### Start the Terminal
```bash
live-ai-terminal
```

### As a System Service
```bash
sudo systemctl enable live-ai-terminal
sudo systemctl start live-ai-terminal
```

### Available Commands
- `help` - Show available commands
- `status` - System status overview
- `improve` - Trigger self-improvement
- `auto-improve` - Toggle auto-improvement
- `logs` - View system logs
- `metrics` - Show session metrics
- `chat <message>` - Chat with Grok AI
- `exit` - Exit terminal

## Architecture

### AI Model Boundaries

**Terminal AI Model (This Package):**
- System-wide orchestration and monitoring
- Process management (backend, frontend, databases)
- Log analysis and error detection
- Infrastructure-level decisions
- Self-improvement of the overall system
- Cross-service communication

**VS Code AI Model (Separate):**
- Code editing and completion within IDE
- File and project management
- Workspace-specific development tasks
- Code analysis and refactoring

### Directory Structure
```
/usr/share/live-ai-terminal/     # Application files
├── live_ai_terminal.py          # Main terminal interface
├── ai_*.py                      # AI system modules
├── enhanced_grok_integration.py # Grok AI integration
├── requirements.txt             # Python dependencies
└── config.template.env          # Configuration template

/usr/local/bin/live-ai-terminal  # Main executable
/etc/systemd/system/             # System service
~/.config/live-ai-terminal/      # User configuration
/var/log/live-ai-terminal/       # Application logs
/var/lib/live-ai-terminal/       # Application data
```

## Extending for Other Projects

This package can be adapted for other AI-powered applications:

1. **Replace AI Modules**: Swap out `ai_*.py` modules with project-specific logic
2. **Update Configuration**: Modify `config.template.env` for your needs
3. **Customize Terminal**: Edit `live_ai_terminal.py` for project-specific commands
4. **Service Integration**: Update `enhanced_start_with_ai.sh` for your services

### Example Adaptation
```bash
# Copy package structure
cp -r /usr/share/live-ai-terminal /usr/share/my-ai-app
# Customize modules
vim /usr/share/my-ai-app/live_ai_terminal.py
# Update service
sudo cp /etc/systemd/system/live-ai-terminal.service /etc/systemd/system/my-ai-app.service
# Edit service file paths
sudo vim /etc/systemd/system/my-ai-app.service
```

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status live-ai-terminal
journalctl -u live-ai-terminal -f
```

### Check Logs
```bash
tail -f /var/log/live-ai-terminal/ai_workflow.log
```

### Permissions Issues
```bash
sudo chown -R $USER:$USER ~/.config/live-ai-terminal
sudo chmod -R 755 /usr/share/live-ai-terminal
```

## Uninstallation
```bash
sudo dpkg -r live-ai-terminal
```

This will stop the service, remove files, but preserve user configuration.
