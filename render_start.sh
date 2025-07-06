#!/bin/bash
# CEO AI Terminal - Render.com startup

echo "🚀 Starting CEO AI Terminal System on Render.com"
redis-server --daemonize yes
python render_server.py
