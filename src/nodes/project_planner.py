from langchain_core.runnables import Runnable
from agent.state import AgentState
from agent.llm import get_project_planner_llm
from core.prompts import PLANNER_PROMPT
from core.parsers import ProjectPlan


def run_project_planner(state: AgentState) -> dict:
    """
    This node takes the initial user query and generates the high-level
    project plan (title, description, tech stack, file structure).
    """

    # Get existing global logs or start new list
    logs = state.get("logs", [])
    logs.append("✅ Starting Project Planning...")

    # Get the necessary state component
    query = state["query"]
    logs.append("✅ Starting Project Planning...")

    # Get the structured LLM
    planner_llm: Runnable = get_project_planner_llm()

    # Create the chain for this node
    chain = PLANNER_PROMPT | planner_llm

    # Invoke the chain

    try:
        plan_output: ProjectPlan = chain.invoke({"query": query})

        # Sanitize the output file structure
        sanitized_file_structure = [
            f.strip().lower() for f in plan_output.file_structure
        ]

        logs.append(f"✅ Project Title: {plan_output.project_title}")
        logs.append(f"📁 Files Generated: {', '.join(sanitized_file_structure)}")

        # Return the updates to the state
        return {
            "project_title": plan_output.project_title,
            "project_description": plan_output.project_description,
            "tech_stack": plan_output.tech_stack,
            "file_structure": sanitized_file_structure,
            "logs": logs,
        }
    except Exception as e:
        logs.append(f"❌ Error while planning: {str(e)}")
        return {"logs": logs}


# TEST
if __name__ == "__main__":
    test_state = {"query": "build me a simple to-do list app"}

    result = run_project_planner(test_state)

    print("\n--- Test Result ---")
    import json

    print(json.dumps(result, indent=2))
