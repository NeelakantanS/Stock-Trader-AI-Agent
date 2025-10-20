
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Try to import real AgentX orchestrator or fallback to mock
try:
    from agentx import AgentXOrchestrator
except ImportError:
    from mock_agentx_orchestrator import AgentXOrchestrator

def main():
    load_dotenv()
    workflow_path = Path("workflows/stock_trader_workflow.json")
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    print("🚀 Starting AgentX Stock Trader Workflow...")

    with open(workflow_path, "r") as f:
        workflow_data = json.load(f)

    orchestrator = AgentXOrchestrator(workflow_data)
    results = orchestrator.run()

    print("\n✅ Workflow execution completed.")
    print("📊 Results Summary:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
