#!/usr/bin/env python3
"""
BotCloud CLI - Command line interface for BotCloud
"""

import argparse
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from botcloud.manager import BotCloudManager

def cmd_status(args):
    """Check BotCloud status"""
    manager = BotCloudManager()
    stats = manager.get_stats()
    
    print(f"BotCloud Status")
    print(f"==============")
    print(f"API: {stats['api_url']}")
    print(f"API Status: {stats['api_status']}")
    print(f"Workers: {stats['running_workers']}/{stats['total_workers']}")
    print()
    
    if stats['workers']:
        print("Worker Details:")
        for name, info in stats['workers'].items():
            print(f"  {name}: {info['status']} ({info['agent_id']})")

def cmd_start(args):
    """Start workers"""
    manager = BotCloudManager()
    manager.start_api(port=args.port)
    
    print(f"Starting {args.count} workers...")
    workers = manager.spawn_workers(args.count, openclaw_url=args.openclaw_url)
    print(f"✓ Started {len(workers)} workers")
    
    if not args.no_wait:
        print("\nWorkers running. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            manager.stop_all()

def cmd_stop(args):
    """Stop all workers and API"""
    manager = BotCloudManager()
    manager.stop_all()
    print("✓ All stopped")

def cmd_task(args):
    """Submit a task"""
    manager = BotCloudManager()
    manager.start_api(port=args.port)
    
    # Ensure worker exists
    if not args.worker:
        # Use any worker
        workers = manager.spawn_workers(1)
        worker_name = "worker-0"
    else:
        worker_name = args.worker
        # Check if worker exists, if not create it
        stats = manager.get_stats()
        if worker_name not in stats['workers']:
            manager.register_worker(worker_name)
            manager.start_worker(manager.workers[worker_name])
    
    print(f"Submitting to {worker_name}: {args.task}")
    result = manager.submit_task(worker_name, args.task)
    
    if result.get('output'):
        print(f"Result: {result['output']}")
    else:
        print(f"Status: {result.get('status')}")
    
    if not args.no_stop:
        manager.stop_all()

def cmd_any(args):
    """Submit task to any worker (parallel)"""
    manager = BotCloudManager()
    manager.start_api(port=args.port)
    
    workers = manager.spawn_workers(args.workers or 3, openclaw_url=args.openclaw_url)
    
    print(f"Submitting to any worker: {args.task}")
    result = manager.submit_task_any(args.task)
    
    if result.get('output'):
        print(f"Result: {result['output']}")
    
    if not args.no_stop:
        manager.stop_all()

def cmd_stats(args):
    """Get detailed stats"""
    manager = BotCloudManager()
    stats = manager.get_stats()
    import json
    print(json.dumps(stats, indent=2))

def main():
    parser = argparse.ArgumentParser(description="BotCloud CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status
    subparsers.add_parser("status", help="Check status")
    
    # Start
    start_parser = subparsers.add_parser("start", help="Start workers")
    start_parser.add_argument("count", type=int, nargs="?", default=3, help="Number of workers")
    start_parser.add_argument("--port", type=int, default=8000, help="API port")
    start_parser.add_argument("--openclaw-url", default=None, help="OpenClaw URL for delegation")
    start_parser.add_argument("--no-wait", action="store_true", help="Don't wait, just start")
    
    # Stop
    subparsers.add_parser("stop", help="Stop all")
    
    # Task
    task_parser = subparsers.add_parser("task", help="Submit task to worker")
    task_parser.add_argument("task", help="Task to execute")
    task_parser.add_argument("--worker", help="Worker name (default: any)")
    task_parser.add_argument("--port", type=int, default=8000, help="API port")
    task_parser.add_argument("--no-stop", action="store_true", help="Don't stop after")
    
    # Any (parallel)
    any_parser = subparsers.add_parser("any", help="Submit to any worker (parallel)")
    any_parser.add_argument("task", help="Task to execute")
    any_parser.add_argument("--workers", type=int, help="Number of workers to spawn")
    any_parser.add_argument("--port", type=int, default=8000, help="API port")
    any_parser.add_argument("--openclaw-url", default=None, help="OpenClaw URL for delegation")
    any_parser.add_argument("--no-stop", action="store_true", help="Don't stop after")
    
    # Stats
    subparsers.add_parser("stats", help="Get detailed stats")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "task":
        cmd_task(args)
    elif args.command == "any":
        cmd_any(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
