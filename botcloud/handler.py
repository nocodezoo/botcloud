#!/usr/bin/env python3
"""
BotCloud Handler for OpenClaw
Connects OpenClaw to BotCloud for task execution
"""

import sys
import os
sys.path.insert(0, '/home/openryanclaw/.openclaw/workspace')

from botcloud.manager import BotCloudManager

# Global manager instance
_manager = None

def get_manager() -> BotCloudManager:
    """Get or create BotCloud manager"""
    global _manager
    if _manager is None:
        _manager = BotCloudManager()
    return _manager


def ensure_running() -> bool:
    """Ensure BotCloud API is running"""
    m = get_manager()
    try:
        stats = m.get_stats()
        if stats['api_status'] == 'healthy':
            return True
    except:
        pass
    
    return m.start_api()


def ensure_worker(worker_name: str = None) -> str:
    """Ensure a worker is available, return worker name"""
    m = get_manager()
    stats = m.get_stats()
    
    if stats['total_workers'] > 0:
        return worker_name or list(stats['workers'].keys())[0]
    
    workers = m.spawn_workers(1)
    return workers[0].name


def send_command(command: str, worker_name: str = None) -> str:
    """
    Send a command to BotCloud and get result.
    
    Usage from OpenClaw:
        from botcloud.handler import send_command
        result = send_command("exec ls -la")
        result = send_command("math 100+200")
        result = send_command("hardware status")
    """
    # Ensure BotCloud is running
    if not ensure_running():
        return "Error: Could not start BotCloud API"
    
    # Ensure worker exists
    worker = worker_name or ensure_worker()
    
    # Get manager and send task
    m = get_manager()
    
    try:
        result = m.submit_task(worker, command, wait_for_result=True, timeout=120)
        
        if result.get('status') == 'completed':
            output = result.get('output', 'OK')
            return output
        elif result.get('status') == 'timeout':
            return f"Timeout: command took too long"
        else:
            return f"Error: {result.get('status')}"
            
    except Exception as e:
        return f"Error: {str(e)}"


def send_command_any(command: str) -> str:
    """Send to any available worker (parallel)"""
    if not ensure_running():
        return "Error: Could not start BotCloud API"
    
    # Ensure we have at least one worker
    stats = get_manager().get_stats()
    if stats['total_workers'] < 1:
        ensure_worker()
    
    m = get_manager()
    
    try:
        result = m.submit_task_any(command, wait_for_result=True, timeout=120)
        
        if result.get('status') == 'completed':
            return result.get('output', 'OK')
        else:
            return f"Error: {result.get('status')}"
    except Exception as e:
        return f"Error: {str(e)}"


def status() -> str:
    """Get BotCloud status"""
    try:
        m = get_manager()
        stats = m.get_stats()
        return f"BotCloud: {stats['api_status']} | Workers: {stats['running_workers']}/{stats['total_workers']}"
    except Exception as e:
        return f"BotCloud: Not connected ({str(e)})"


def stop():
    """Stop BotCloud"""
    global _manager
    if _manager:
        _manager.stop_all()
        _manager = None
    return "BotCloud stopped"


# Quick test
if __name__ == "__main__":
    print("Testing BotCloud handler...")
    print(f"Status: {status()}")
    
    if ensure_running():
        print("API running")
        
        worker = ensure_worker()
        print(f"Worker: {worker}")
        
        print("\nTest: math 50*10")
        print(send_command("math 50*10"))
        
        print("\nTest: hardware status")
        print(send_command("hardware status"))
