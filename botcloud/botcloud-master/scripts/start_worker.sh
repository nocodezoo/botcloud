#!/bin/bash
# BotCloud Worker Start Script
# Starts worker agents

WORKER_TYPE=${1:-fullstack}

echo "🤖 Starting $WORKER_TYPE worker..."

cd ~/botcloud

# Set Python path
export PYTHONPATH=~/botcloud

case $WORKER_TYPE in
    fullstack)
        nohup python3 -m agent.fullstack_dev > ~/botcloud/logs/worker.log 2>&1 &
        echo "✅ FullStackDev worker started"
        ;;
    smart)
        nohup python3 -m agent.smart_worker > ~/botcloud/logs/worker.log 2>&1 &
        echo "✅ SmartWorker started"
        ;;
    worker)
        nohup python3 -m agent.example worker > ~/botcloud/logs/worker.log 2>&1 &
        echo "✅ WorkerBot started"
        ;;
    *)
        echo "Usage: $0 [fullstack|smart|worker]"
        exit 1
        ;;
esac

echo ""
echo "Worker started! Check: curl localhost:8001/agents"
