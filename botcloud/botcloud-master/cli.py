#!/usr/bin/env python3
"""
BotCloud CLI - Control BotCloud from command line
Can be used by OpenClaw to delegate tasks
"""

import argparse
import json
import sys
from botcloud_client import BotCloudClient

def main():
    parser = argparse.ArgumentParser(description="BotCloud CLI")
    parser.add_argument("--url", default="http://localhost:8000", help="BotCloud API URL")
    parser.add_argument("command", choices=["health", "list", "find", "assign", "task", "stats"])
    parser.add_argument("--agent", help="Agent name or ID")
    parser.add_argument("--caps", nargs="+", help="Capabilities to find")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--input", "-i", help="Task input")
    parser.add_argument("--wait", "-w", action="store_true", help="Wait for result")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    client = BotCloudClient(args.url)
    
    if args.command == "health":
        result = client.health_check()
        print(json.dumps(result, indent=2))
        
    elif args.command == "list":
        agents = client.list_agents()
        if not agents:
            print("No agents found")
            return
            
        for a in agents:
            status = a.get("status", "unknown")
            caps = ", ".join(a.get("capabilities", []))
            print(f"{a.get('name')} ({a.get('id')}): {status} [{caps}]")
    
    elif args.command == "find":
        agents = client.find_agents(capabilities=args.caps, status=args.status)
        if not agents:
            print("No matching agents found")
            return
            
        for a in agents:
            print(f"{a.get('name')}: {a.get('status')}")
    
    elif args.command == "assign":
        if not args.agent or not args.input:
            print("Error: --agent and --input required")
            sys.exit(1)
            
        result = client.assign_task(agent_name=args.agent, task_input=args.input)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
            
        print(json.dumps(result, indent=2))
        
        if args.wait:
            task_id = result.get("id")
            print(f"Waiting for task {task_id}...")
            result = client.wait_for_task(task_id, timeout=args.timeout)
            print(json.dumps(result, indent=2))
    
    elif args.command == "task":
        if not args.agent or not args.input:
            print("Error: --agent and --input required")
            sys.exit(1)
            
        result = client.run_task_and_wait(
            agent_name=args.agent,
            task_input=args.input,
            timeout=args.timeout
        )
        
        if result.get("status") == "completed":
            print(result.get("output", ""))
        else:
            print(f"Error: {result.get('status')} - {result.get('output', '')}")
            sys.exit(1)
    
    elif args.command == "stats":
        stats = client.get_worker_stats()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
