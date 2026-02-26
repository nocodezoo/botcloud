#!/bin/bash
# BotCloud Integration Tests
# Run these after starting the server

BOTCLOUD_URL="${BOTCLOUD_URL:-http://localhost:8000}"
WEBSOCKET_URL="${WEBSOCKET_URL:-ws://localhost:8001}"
DISCOVERY_URL="${DISCOVERY_URL:-http://localhost:8002}"
TASK_URL="${TASK_URL:-http://localhost:8003}"

echo "========================================"
echo "BotCloud Integration Tests v1.3.0"
echo "========================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

pass() { echo -e "${GREEN}✓ PASS${NC}: $1"; ((TESTS_PASSED++)); }
fail() { echo -e "${RED}✗ FAIL${NC}: $1"; ((TESTS_FAILED++)); }
skip() { echo -e "${YELLOW}⊘ SKIP${NC}: $1"; ((TESTS_SKIPPED++)); }

# Check if server is running
echo ""
echo "Checking services..."

curl -s "$BOTCLOUD_URL/health" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "BotCloud API not running on $BOTCLOUD_URL"
    echo "Start with: cd botcloud/api && python3 main.py"
    skip "All tests - server not running"
    exit 1
fi

pass "Server is running"

# ========== CORE API TESTS ==========
echo ""
echo "=== Core API Tests ==="

# Test 1: Root endpoint
result=$(curl -s "$BOTCLOUD_URL/" | grep -o "BotCloud")
if [ -n "$result" ]; then
    pass "Root endpoint returns BotCloud"
else
    fail "Root endpoint"
fi

# Test 2: Health check
result=$(curl -s "$BOTCLOUD_URL/health" | grep -o "healthy")
if [ -n "$result" ]; then
    pass "Health check"
else
    fail "Health check"
fi

# Test 3: Register first agent
AGENT1=$(curl -s -X POST "$BOTCLOUD_URL/agents" \
    -H "Content-Type: application/json" \
    -d '{"name":"ResearcherBot","capabilities":["search","browse"]}')
AGENT1_ID=$(echo "$AGENT1" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
if [ -n "$AGENT1_ID" ]; then
    pass "Register Agent 1 (ResearcherBot): $AGENT1_ID"
else
    fail "Register Agent 1"
    AGENT1_ID="agent_test_1"
fi

# Test 4: Register second agent
AGENT2=$(curl -s -X POST "$BOTCLOUD_URL/agents" \
    -H "Content-Type: application/json" \
    -d '{"name":"CoderBot","capabilities":["code","write"]}')
AGENT2_ID=$(echo "$AGENT2" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
if [ -n "$AGENT2_ID" ]; then
    pass "Register Agent 2 (CoderBot): $AGENT2_ID"
else
    fail "Register Agent 2"
    AGENT2_ID="agent_test_2"
fi

# Test 5: List agents
result=$(curl -s "$BOTCLOUD_URL/agents" | grep -c "agent_")
if [ "$result" -ge 2 ]; then
    pass "List agents"
else
    fail "List agents"
fi

# Test 6: Get specific agent
result=$(curl -s "$BOTCLOUD_URL/agents/$AGENT1_ID" | grep -o "ResearcherBot")
if [ -n "$result" ]; then
    pass "Get agent details"
else
    fail "Get agent details"
fi

# Test 7: Start agent
result=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1_ID/start" | grep -o "running")
if [ -n "$result" ]; then
    pass "Start agent"
else
    fail "Start agent"
fi

# Test 8: Stop agent
result=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1_ID/stop" | grep -o "stopped")
if [ -n "$result" ]; then
    pass "Stop agent"
else
    fail "Stop agent"
fi

# Test 9: Create task
TASK1=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1_ID/tasks" \
    -H "Content-Type: application/json" \
    -d '{"input":"Research AI agents"}')
TASK1_ID=$(echo "$TASK1" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TASK1_ID" ]; then
    pass "Create task: $TASK1_ID"
else
    fail "Create task"
    TASK1_ID="task_test_1"
fi

# Test 10: Get task
result=$(curl -s "$BOTCLOUD_URL/tasks/$TASK1_ID" | grep -o "Research AI agents")
if [ -n "$result" ]; then
    pass "Get task"
else
    fail "Get task"
fi

# Test 11: Store memory
result=$(curl -s -X POST "$BOTCLOUD_URL/memory/$AGENT1_ID" \
    -H "Content-Type: application/json" \
    -d '{"key":"project","value":"Building SaaS"}' | grep -o "project")
if [ -n "$result" ]; then
    pass "Store memory"
else
    fail "Store memory"
fi

# Test 12: Get memory
result=$(curl -s "$BOTCLOUD_URL/memory/$AGENT1_ID" | grep -o "Building SaaS")
if [ -n "$result" ]; then
    pass "Get memory"
else
    fail "Get memory"
fi

# Test 13: Get metrics
result=$(curl -s "$BOTCLOUD_URL/metrics/$AGENT1_ID" | grep -o "agent_id")
if [ -n "$result" ]; then
    pass "Get metrics"
else
    fail "Get metrics"
fi

# Test 14: Get logs
result=$(curl -s "$BOTCLOUD_URL/logs/$AGENT1_ID" | grep -o "logs")
if [ -n "$result" ]; then
    pass "Get logs"
else
    fail "Get logs"
fi

# Test 15: Configure agent
result=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1_ID/configure" \
    -H "Content-Type: application/json" \
    -d '{"temperature":0.7,"max_tokens":1000}' | grep -o "temperature")
if [ -n "$result" ]; then
    pass "Configure agent"
else
    fail "Configure agent"
fi

# ========== COLLABORATION TESTS ==========
echo ""
echo "=== Collaboration Tests ==="

# Test 16: Send message between agents
result=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1_ID/message" \
    -H "Content-Type: application/json" \
    -d '{"to_agent":"'"$AGENT2_ID"'","content":"Hello from Researcher"}' | grep -o "message")
if [ -n "$result" ]; then
    pass "Send message between agents"
else
    fail "Send message between agents"
fi

# Test 17: Get messages
result=$(curl -s "$BOTCLOUD_URL/agents/$AGENT1_ID/messages" | grep -o "message")
if [ -n "$result" ]; then
    pass "Get messages"
else
    fail "Get messages"
fi

# Test 18: Delegate task
result=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1_ID/delegate" \
    -H "Content-Type: application/json" \
    -d '{"to_agent":"'"$AGENT2_ID"'","task":"Write a function"}' | grep -o "delegated")
if [ -n "$result" ]; then
    pass "Delegate task to another agent"
else
    fail "Delegate task"
fi

# Test 19: List agent tasks
result=$(curl -s "$BOTCLOUD_URL/agents/$AGENT1_ID/tasks" | grep -o "tasks")
if [ -n "$result" ]; then
    pass "List agent tasks"
else
    fail "List agent tasks"
fi

# Test 20: Delete memory
result=$(curl -s -X DELETE "$BOTCLOUD_URL/memory/$AGENT1_ID/project" | grep -o "deleted")
if [ -n "$result" ]; then
    pass "Delete memory"
else
    fail "Delete memory"
fi

# ========== SUMMARY ==========
echo ""
echo "========================================"
echo "Test Results"
echo "========================================"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Skipped: ${YELLOW}$TESTS_SKIPPED${NC}"
echo "========================================"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi
