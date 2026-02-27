"""
Example BotCloud Agents
Copy this file and modify for your own agents
"""

from agent import BotCloudAgent
import time

# ============================================================
# EXAMPLE 1: Echo Bot - Simple echo handler
# ============================================================
def run_echo_bot(name: str = "EchoBot", api_url: str = "http://localhost:8000"):
    """Simple bot that echoes back input"""
    
    agent = BotCloudAgent(
        name=name,
        api_url=api_url,
        capabilities=["echo", "test"]
    )
    
    @agent.task("echo")
    def echo(task_input: str) -> str:
        """Echo the input back"""
        return f"Echo: {task_input}"
    
    @agent.task("default")
    def default(task_input: str) -> str:
        """Default handler"""
        return f"EchoBot processed: {task_input}"
    
    agent.start()
    
    print(f"{name} is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


# ============================================================
# EXAMPLE 2: Search Bot - Does web searches
# ============================================================
def run_search_bot(name: str = "SearchBot", api_url: str = "http://localhost:8000"):
    """Bot that performs web searches"""
    
    agent = BotCloudAgent(
        name=name,
        api_url=api_url,
        capabilities=["search", "research"]
    )
    
    @agent.task("search")
    def search(task_input: str) -> str:
        """Perform a search"""
        # In production, you'd call Google, Bing, or Brave API
        # For now, simulate a search
        return f"Search results for '{task_input}': [Result 1, Result 2, Result 3]"
    
    @agent.task("research")
    def research(task_input: str) -> str:
        """Do research on a topic"""
        return f"Research complete on: {task_input}\n- Key finding 1\n- Key finding 2\n- Key finding 3"
    
    @agent.task("default")
    def default(task_input: str) -> str:
        return search(task_input)
    
    agent.start()
    
    print(f"{name} is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


# ============================================================
# EXAMPLE 3: Worker Bot - Does various tasks
# ============================================================
def run_worker_bot(name: str = "WorkerBot", api_url: str = "http://localhost:8000"):
    """Multi-purpose worker bot"""
    
    agent = BotCloudAgent(
        name=name,
        api_url=api_url,
        capabilities=["process", "analyze", "transform"]
    )
    
    @agent.task("process")
    def process_data(task_input: str) -> str:
        """Process some data"""
        # Example: transform, clean, or process input
        return f"Processed '{task_input}': Done!"
    
    @agent.task("analyze")
    def analyze(task_input: str) -> str:
        """Analyze data"""
        words = len(task_input.split())
        chars = len(task_input)
        return f"Analysis: {words} words, {chars} characters"
    
    @agent.task("transform")
    def transform(task_input: str) -> str:
        """Transform data (uppercase example)"""
        return task_input.upper()
    
    @agent.task("default")
    def default(task_input: str) -> str:
        return f"WorkerBot handled: {task_input}"
    
    agent.start()
    
    print(f"{name} is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


# ============================================================
# EXAMPLE 4: OpenClaw Integration Bot
# ============================================================
def run_openclaw_worker(name: str = "OpenClawWorker", api_url: str = "http://localhost:8000"):
    """
    Worker bot designed to work with OpenClaw.
    OpenClaw assigns tasks, this bot executes them.
    """
    
    agent = BotCloudAgent(
        name=name,
        api_url=api_url,
        capabilities=["openclaw", "execute", "delegate"]
    )
    
    @agent.task("execute")
    def execute_command(task_input: str) -> str:
        """Execute a command (safely sandboxed in production)"""
        return f"Executed: {task_input}\nStatus: Success"
    
    @agent.task("delegate")
    def delegate_task(task_input: str) -> str:
        """Delegate to another agent"""
        return f"Delegated: {task_input}"
    
    @agent.task("default")
    def default_handler(task_input: str) -> str:
        """Default handler for OpenClaw tasks"""
        return f"OpenClawWorker processed: {task_input}"
    
    agent.start()
    
    print(f"{name} is running - Ready for OpenClaw tasks!")
    print(f"Capabilities: {agent.capabilities}")
    
    try:
        while True:
            # Check for messages from OpenClaw
            messages = agent.get_messages()
            for msg in messages:
                print(f"📩 Message: {msg}")
            time.sleep(2)
    except KeyboardInterrupt:
        agent.stop()


# ============================================================
# Run one of the examples
# ============================================================
if __name__ == "__main__":
    import sys
    
    # Choose which bot to run
    bot_type = sys.argv[1] if len(sys.argv) > 1 else "echo"
    
    if bot_type == "echo":
        run_echo_bot()
    elif bot_type == "search":
        run_search_bot()
    elif bot_type == "worker":
        run_worker_bot()
    elif bot_type == "openclaw":
        run_openclaw_worker()
    else:
        print(f"Unknown bot: {bot_type}")
        print("Usage: python example.py [echo|search|worker|openclaw]")
