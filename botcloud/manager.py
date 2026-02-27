#!/usr/bin/env python3
"""
BotCloud Manager - Integration layer for OpenClaw
Manages BotCloud API and worker processes from OpenClaw
"""

import os
import sys
import subprocess
import time
import requests
import signal
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import threading

# BotCloud paths
BOTCLOUD_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(BOTCLOUD_DIR, "api")
AGENT_DIR = os.path.join(BOTCLOUD_DIR, "agent")
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_POLL_INTERVAL = 2


@dataclass
class BotCloudWorker:
    """Represents a BotCloud worker process"""
    name: str
    agent_id: Optional[str] = None
    process: Optional[subprocess.Popen] = None
    api_key: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    status: str = "stopped"


class BotCloudManager:
    """
    Manages BotCloud API and worker processes for OpenClaw.
    
    Usage:
        manager = BotCloudManager()
        manager.start_api()
        workers = manager.spawn_workers(5)
        task_id = manager.submit_task("worker-0", "do something")
        result = manager.get_result(task_id)
    """
    
    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        workspace: str = None
    ):
        self.api_url = api_url.rstrip('/')
        self.workspace = workspace or os.path.join(os.path.expanduser("~"), "botcloud", "workspace")
        self.api_process: Optional[subprocess.Popen] = None
        self.workers: Dict[str, BotCloudWorker] = {}
        self._running = False
        self._lock = threading.Lock()
        
    def start_api(self, port: int = 8000) -> bool:
        """Start the BotCloud API server"""
        # Update API URL with port
        self.api_url = f"http://localhost:{port}"
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=2)
            if resp.status_code == 200:
                print(f"✓ BotCloud API already running at {self.api_url}")
                return True
        except:
            pass
        
        # Start API server
        print(f"Starting BotCloud API on port {port}...")
        
        env = os.environ.copy()
        env["PORT"] = str(port)
        
        self.api_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=API_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if sys.platform != 'win32' else None
        )
        
        # Wait for API to be ready
        for i in range(30):
            try:
                resp = requests.get(f"{self.api_url}/health", timeout=1)
                if resp.status_code == 200:
                    print(f"✓ BotCloud API running at {self.api_url}")
                    self._running = True
                    return True
            except:
                time.sleep(0.5)
        
        print(f"✗ Failed to start BotCloud API")
        return False
    
    def stop_api(self):
        """Stop the BotCloud API server"""
        if self.api_process:
            try:
                os.killpg(os.getpgid(self.api_process.pid), signal.SIGTERM)
            except:
                self.api_process.terminate()
            self.api_process = None
        self._running = False
        print("✓ BotCloud API stopped")
    
    def register_worker(
        self,
        name: str,
        capabilities: List[str] = None,
        worker_type: str = "worker"
    ) -> BotCloudWorker:
        """Register a new worker with the BotCloud API"""
        capabilities = capabilities or ["general"]
        
        resp = requests.post(
            f"{self.api_url}/agents",
            json={
                "name": name,
                "capabilities": capabilities
            }
        )
        resp.raise_for_status()
        data = resp.json()
        
        worker = BotCloudWorker(
            name=name,
            agent_id=data["id"],
            api_key=data["api_key"],
            capabilities=capabilities,
            status="registered"
        )
        
        with self._lock:
            self.workers[name] = worker
        
        print(f"✓ Registered worker: {name} ({worker.agent_id})")
        return worker
    
    def start_worker(self, worker: BotCloudWorker) -> bool:
        """Start a worker process"""
        if worker.process:
            return True
        
        # Use the external worker.py with real capabilities
        worker_env = os.environ.copy()
        worker_env["BOTCLOUD_API"] = self.api_url
        worker_env["BOTCLOUD_AGENT_ID"] = worker.agent_id
        worker_env["BOTCLOUD_API_KEY"] = worker.api_key
        worker_env["BOTCLOUD_POLL_INTERVAL"] = str(DEFAULT_POLL_INTERVAL)
        worker_env["BOTCLOUD_WORKSPACE"] = self.workspace
        
        worker.process = subprocess.Popen(
            [sys.executable, self.worker_py_path()],
            env=worker_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if sys.platform != 'win32' else None
        )
        worker.status = "running"
        print(f"✓ Started worker process: {worker.name}")
        return True
    
    def worker_py_path(self) -> str:
        """Get path to worker.py"""
        return os.path.join(BOTCLOUD_DIR, "worker.py")
    
    def spawn_workers(
        self,
        count: int,
        worker_type: str = "worker",
        capabilities: List[str] = None
    ) -> List[BotCloudWorker]:
        """Spawn multiple workers"""
        workers = []
        
        for i in range(count):
            name = f"worker-{i}"
            worker = self.register_worker(name, capabilities, worker_type)
            self.start_worker(worker)
            workers.append(worker)
        
        print(f"✓ Spawned {count} workers")
        return workers
    
    def submit_task(
        self,
        worker_name: str,
        task_input: str,
        wait_for_result: bool = True,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Submit a task to a worker"""
        worker = self.workers.get(worker_name)
        if not worker or not worker.agent_id:
            raise ValueError(f"Worker {worker_name} not found")
        
        resp = requests.post(
            f"{self.api_url}/agents/{worker.agent_id}/tasks",
            headers={"X-API-Key": worker.api_key},
            json={"input_data": task_input}
        )
        resp.raise_for_status()
        task_data = resp.json()
        task_id = task_data["id"]
        
        print(f"✓ Submitted task {task_id} to {worker_name}")
        
        if wait_for_result:
            return self._wait_for_result(task_id, timeout)
        
        return task_data
    
    def _wait_for_result(self, task_id: str, timeout: int) -> Dict[str, Any]:
        """Wait for task completion"""
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                resp = requests.get(f"{self.api_url}/tasks/{task_id}", timeout=5)
                if resp.status_code == 200:
                    task = resp.json()
                    if task["status"] == "completed":
                        return task
                    if task["status"] == "failed":
                        return task
            except:
                pass
            time.sleep(0.5)
        
        return {"id": task_id, "status": "timeout", "output": None}
    
    def get_worker_status(self) -> Dict[str, Dict]:
        """Get status of all workers"""
        status = {}
        for name, worker in self.workers.items():
            status[name] = {
                "agent_id": worker.agent_id,
                "status": worker.status,
                "capabilities": worker.capabilities
            }
        return status
    
    def stop_worker(self, name: str):
        """Stop a specific worker"""
        worker = self.workers.get(name)
        if worker and worker.process:
            try:
                os.killpg(os.getpgid(worker.process.pid), signal.SIGTERM)
            except:
                worker.process.terminate()
            worker.process = None
            worker.status = "stopped"
            print(f"✓ Stopped worker: {name}")
    
    def stop_all(self):
        """Stop all workers and API"""
        for name in list(self.workers.keys()):
            self.stop_worker(name)
        self.stop_api()
        print("✓ All BotCloud resources stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get BotCloud network stats"""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=2)
            health = resp.json()
        except:
            health = {"status": "unavailable"}
        
        return {
            "api_url": self.api_url,
            "api_status": health.get("status", "unknown"),
            "total_workers": len(self.workers),
            "running_workers": sum(1 for w in self.workers.values() if w.status == "running"),
            "workers": self.get_worker_status()
        }


# Convenience function for quick testing
def quick_test(workers: int = 3):
    """Quick integration test"""
    print(f"=== BotCloud Quick Test ({workers} workers) ===")
    
    manager = BotCloudManager()
    
    # Start API
    if not manager.start_api():
        print("Failed to start API")
        return
    
    # Spawn workers
    manager.spawn_workers(workers)
    
    # Submit a task
    print("\n--- Submitting test task ---")
    result = manager.submit_task("worker-0", "Hello from OpenClaw!")
    print(f"Result: {result.get('output')}")
    
    # Get stats
    print("\n--- Network Stats ---")
    stats = manager.get_stats()
    print(f"Workers: {stats['running_workers']}/{stats['total_workers']}")
    
    # Cleanup
    print("\n--- Cleanup ---")
    manager.stop_all()
    print("Test complete!")


if __name__ == "__main__":
    quick_test()


# Global singleton for OpenClaw integration
# Use: from botcloud.manager import botcloud_manager
botcloud_manager = None

def get_manager() -> BotCloudManager:
    """Get or create the global BotCloud manager instance"""
    global botcloud_manager
    if botcloud_manager is None:
        botcloud_manager = BotCloudManager()
    return botcloud_manager
