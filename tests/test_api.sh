#!/bin/bash
# BotCloud Test Suite v1.0
# Tests all core API endpoints

BOTCLOUD_URL="${BOTCLOUD_URL:-http://localhost:8000}"

echo "=========================================="
echo "BotCloud Test Suite v1.0"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

passed=0
failed=0

test() {
    echo -n "Testing: $1 ... "
    if eval "$2" > /tmp/test_output.txt 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((passed++))
    else
        echo -e "${RED}FAIL${NC}"
        ((failed++))
        cat /tmp/test_output.txt
    fi
}

# Test 1: Health Check
test "Health Check" \
    "curl -s $BOTCLOUD_URL/health | grep -q 'healthy'"

# Test 2: Register Agent
AGENT1=$(curl -s -X POST $BOTCLOUD_URL/agents \
    -H "Content-Type: application/json" \
    -d '{"name": "TestBot1", "capabilities": ["search"]}' \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")

test "Register Agent" \
    "test -n '$AGENT1'"

# Test 3: Get Agent
test "Get Agent" \
    "curl -s $BOTCLOUD_URL/agents/$AGENT1 | grep -q TestBot1"

# Test 4: List Agents
test "List Agents" \
    "curl -s $BOTCLOUD_URL/agents | grep -q TestBot1"

# Test 5: Start Agent
test "Start Agent" \
    "curl -s -X POST $BOTCLOUD_URL/agents/$AGENT1/start | grep -q running"

# Test 6: Stop Agent  
test "Stop Agent" \
    "curl -s -X POST $BOTCLOUD_URL/agents/$AGENT1/stop | grep -q stopped"

# Test 7: Create Task
TASK1=$(curl -s -X POST "$BOTCLOUD_URL/agents/$AGENT1/tasks" \
    -H "Content-Type: application/json" \
    -d '{"input":"test task"}' \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")

test "Create Task" \
    "test -n '$TASK1'"

# Test 8: Get Task
test "Get Task" \
    "curl -s $BOTCLOUD_URL/tasks/$TASK1 | grep -q test task"

# Test 9: Store Memory
test "Store Memory" \
    "curl -s -X POST $BOTCLOUD_URL/memory/$AGENT1 \
        -H 'Content-Type: application/json' \
        -d '{\"key\":\"test_key\",\"value\":\"test_value\"}' | grep -q test_key"

# Test 10: Get Memory
test "Get Memory" \
    "curl -s $BOTCLOUD_URL/memory/$AGENT1 | grep -q test_value"

# Test 11: Get Metrics
test "Get Metrics" \
    "curl -s $BOTCLOUD_URL/metrics/$AGENT1 | grep -q agent_id"

# Test 12: Get Logs
test "Get Logs" \
    "curl -s $BOTCLOUD_URL/logs/$AGENT1 | grep -q logs"

echo ""
echo "=========================================="
echo "Results: $passed passed, $failed failed"
echo "=========================================="

exit $failed
