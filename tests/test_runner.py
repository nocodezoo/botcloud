#!/usr/bin/env python3
"""
BotCloud Test Runner
v1.3.0
Tests all BotCloud endpoints
"""

import requests
import json
import sys
import time

BOTCLOUD_URL = "http://localhost:8000"

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        
    def pass_test(self, name):
        print(f"✓ PASS: {name}")
        self.passed += 1
        
    def fail_test(self, name, error=""):
        print(f"✗ FAIL: {name}")
        if error:
            print(f"  Error: {error}")
        self.failed += 1
        
    def skip_test(self, name):
        print(f"⊘ SKIP: {name}")
        self.skipped += 1
        
    def summary(self):
        print(f"\n{'='*50}")
        print(f"Results: {self.passed} passed, {self.failed} failed, {self.skipped} skipped")
        print(f"{'='*50}")
        return self.failed == 0


def test_health(result):
    """Test 1: Health check"""
    try:
        r = requests.get(f"{BOTCLOUD_URL}/health", timeout=5)
        if "healthy" in r.text or "status" in r.text:
            result.pass_test("Health check")
        else:
            result.fail_test("Health check", r.text)
    except Exception as e:
        result.fail_test("Health check", str(e))


def test_register_agent(result):
    """Test 2: Register agent"""
    try:
        data = {
            "name": "TestBot",
            "capabilities": ["test", "demo"]
        }
        r = requests.post(f"{BOTCLOUD_URL}/agents", json=data, timeout=5)
        if r.status_code == 200:
            agent_id = r.json().get("id", "")
            result.pass_test(f"Register agent: {agent_id}")
            return agent_id
        else:
            result.fail_test("Register agent", r.text)
            return None
    except Exception as e:
        result.fail_test("Register agent", str(e))
        return None


def test_list_agents(result):
    """Test 3: List agents"""
    try:
        r = requests.get(f"{BOTCLOUD_URL}/agents", timeout=5)
        if r.status_code == 200:
            agents = r.json().get("agents", [])
            result.pass_test(f"List agents ({len(agents)} found)")
        else:
            result.fail_test("List agents", r.text)
    except Exception as e:
        result.fail_test("List agents", str(e))


def test_get_agent(result, agent_id):
    """Test 4: Get agent"""
    if not agent_id:
        result.skip_test("Get agent")
        return
    try:
        r = requests.get(f"{BOTCLOUD_URL}/agents/{agent_id}", timeout=5)
        if r.status_code == 200:
            result.pass_test("Get agent details")
        else:
            result.fail_test("Get agent", r.text)
    except Exception as e:
        result.fail_test("Get agent", str(e))


def test_start_agent(result, agent_id):
    """Test 5: Start agent"""
    if not agent_id:
        result.skip_test("Start agent")
        return
    try:
        r = requests.post(f"{BOTCLOUD_URL}/agents/{agent_id}/start", timeout=5)
        if r.status_code == 200:
            result.pass_test("Start agent")
        else:
            result.fail_test("Start agent", r.text)
    except Exception as e:
        result.fail_test("Start agent", str(e))


def test_stop_agent(result, agent_id):
    """Test 6: Stop agent"""
    if not agent_id:
        result.skip_test("Stop agent")
        return
    try:
        r = requests.post(f"{BOTCLOUD_URL}/agents/{agent_id}/stop", timeout=5)
        if r.status_code == 200:
            result.pass_test("Stop agent")
        else:
            result.fail_test("Stop agent", r.text)
    except Exception as e:
        result.fail_test("Stop agent", str(e))


def test_create_task(result, agent_id):
    """Test 7: Create task"""
    if not agent_id:
        result.skip_test("Create task")
        return None
    try:
        r = requests.post(
            f"{BOTCLOUD_URL}/agents/{agent_id}/tasks",
            json="Test task input",
            timeout=5
        )
        if r.status_code == 200:
            task_id = r.json().get("id", "")
            result.pass_test(f"Create task: {task_id}")
            return task_id
        else:
            result.fail_test("Create task", r.text)
            return None
    except Exception as e:
        result.fail_test("Create task", str(e))
        return None


def test_get_task(result, task_id):
    """Test 8: Get task"""
    if not task_id:
        result.skip_test("Get task")
        return
    try:
        r = requests.get(f"{BOTCLOUD_URL}/tasks/{task_id}", timeout=5)
        if r.status_code == 200:
            result.pass_test("Get task")
        else:
            result.fail_test("Get task", r.text)
    except Exception as e:
        result.fail_test("Get task", str(e))


def test_store_memory(result, agent_id):
    """Test 9: Store memory"""
    if not agent_id:
        result.skip_test("Store memory")
        return
    try:
        r = requests.post(
            f"{BOTCLOUD_URL}/memory/{agent_id}",
            json={"key": "test_key", "value": "test_value"},
            timeout=5
        )
        if r.status_code == 200:
            result.pass_test("Store memory")
        else:
            result.fail_test("Store memory", r.text)
    except Exception as e:
        result.fail_test("Store memory", str(e))


def test_get_memory(result, agent_id):
    """Test 10: Get memory"""
    if not agent_id:
        result.skip_test("Get memory")
        return
    try:
        r = requests.get(f"{BOTCLOUD_URL}/memory/{agent_id}", timeout=5)
        if r.status_code == 200:
            result.pass_test("Get memory")
        else:
            result.fail_test("Get memory", r.text)
    except Exception as e:
        result.fail_test("Get memory", str(e))


def test_metrics(result, agent_id):
    """Test 11: Get metrics"""
    if not agent_id:
        result.skip_test("Get metrics")
        return
    try:
        r = requests.get(f"{BOTCLOUD_URL}/metrics/{agent_id}", timeout=5)
        if r.status_code == 200:
            result.pass_test("Get metrics")
        else:
            result.fail_test("Get metrics", r.text)
    except Exception as e:
        result.fail_test("Get metrics", str(e))


def test_logs(result, agent_id):
    """Test 12: Get logs"""
    if not agent_id:
        result.skip_test("Get logs")
        return
    try:
        r = requests.get(f"{BOTCLOUD_URL}/logs/{agent_id}", timeout=5)
        if r.status_code == 200:
            result.pass_test("Get logs")
        else:
            result.fail_test("Get logs", r.text)
    except Exception as e:
        result.fail_test("Get logs", str(e))


def test_delegate(result, from_agent, to_agent):
    """Test 13: Delegate task"""
    if not from_agent or not to_agent:
        result.skip_test("Delegate task")
        return
    try:
        r = requests.post(
            f"{BOTCLOUD_URL}/agents/{from_agent}/delegate",
            json={"to_agent": to_agent, "task": "Delegated task"},
            timeout=5
        )
        if r.status_code == 200:
            result.pass_test("Delegate task")
        else:
            result.fail_test("Delegate task", r.text)
    except Exception as e:
        result.fail_test("Delegate task", str(e))


def main():
    print("="*50)
    print("BotCloud Test Runner v1.3.0")
    print("="*50)
    
    result = TestResult()
    
    # Run tests
    test_health(result)
    agent_id = test_register_agent(result)
    test_list_agents(result)
    test_get_agent(result, agent_id)
    test_start_agent(result, agent_id)
    test_stop_agent(result, agent_id)
    task_id = test_create_task(result, agent_id)
    test_get_task(result, task_id)
    test_store_memory(result, agent_id)
    test_get_memory(result, agent_id)
    test_metrics(result, agent_id)
    test_logs(result, agent_id)
    
    # Summary
    success = result.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
