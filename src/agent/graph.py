from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from nodes.project_planner import run_project_planner
from nodes.file_architect import run_file_architect
from nodes.coder_loop import run_code, run_critic
from core.store import save_workspace_to_disk

# -- 1. Define Helper Nodes & Conditional Logic --


def commit_code_to_workspace(state: AgentState) -> dict:
    """
    A simple node to "commit" the perfect code to the final workspace.
    """
    logs = state.get("logs", [])

    current_file = state["current_file"]
    current_code = state["current_code_draft"]

    # Update the workspace
    workspace = state["workspace"]
    workspace[current_file] = current_code

    print(f"    > Code for {current_file} saved to workspace.")
    logs.append(f"✅ Code for **{current_file}** saved to workspace.")

    # Clear the loop variables
    return {
        "workspace": workspace,
        "current_file": None,
        "current_code_draft": None,
        "critique": None,
        "coder_iterations": 0,
        "logs": logs,
    }


def decide_which_file_to_code(state: AgentState) -> str:
    """
    This is our first conditional edge.
    It *only* checks the file queue to decide the next step.
    It does *not* modify the state.
    """
    logs = state.get("logs", [])

    if not state["files_to_code_queue"]:
        # The queue is empty, we are done!
        print("    > Queue empty. Ending graph.")
        logs.append("✅ All files generated. Project complete.")
        return "END"
    else:
        print(f"    > Queue has files. Preparing next file.")
        logs.append("📁 Files remaining. Moving to next file...")
        return "prepare_next_file"


def prepare_next_file_node(state: AgentState) -> dict:
    """
    This is a *regular node* that prepares the state for the coder.
    It pops a file from the queue, sets 'current_file',
    and resets the coder loop variables.
    """
    print(f"--- 2c. PREPARING NEXT FILE ---")
    logs = state.get("logs", [])

    # Get the queue from the state
    queue = state["files_to_code_queue"]
    # Pop the next file
    next_file = queue.pop(0)

    logs.append(f"🧩 Preparing next file: **{next_file}**")

    print(f"    > Next file to code: {next_file}")

    return {
        "files_to_code_queue": queue,
        "current_file": next_file,
        "coder_iterations": 0,
        "critique": None,
        "current_code_draft": None,
        "logs": logs,
    }


def check_critique(state: AgentState) -> str:
    """
    This is our second conditional edge.
    It checks the critic's output and routes to the correct node.
    """
    print(f"--- 3c. CHECKING CRITIQUE ---")
    logs = state.get("logs", [])

    critique = state.get("critique")
    iterations = state["coder_iterations"]

    print(f"--- After 3c. checking critique {critique}")

    # Safety check to prevent infinite loops
    if iterations > 2:
        logs.append(
            f"⚠️ Max correction attempts reached for **{state['current_file']}**. Committing code anyway."
        )
        print(f"    > ERROR: Max iterations reached for {state['current_file']}.")
        return "commit_code"

    if critique == "PERFECT":
        logs.append(
            f"✅ Final review passed for **{state['current_file']}**. Committing code."
        )
        print(f"    > Critique is PERFECT. Committing code.")
        return "commit_code"
    else:
        logs.append(
            f"🔁 Revisions needed for **{state['current_file']}**. Sending back to coder."
        )
        print(f"    > Critique is NOT perfect. Returning to coder.")
        return "retry_coder"


# ---- 2. Assemble the Graph --


def create_agent_graph() -> StateGraph:
    """
    Creates and compiles the complete LangGraph agent.
    """

    # Initialize the graph with state
    builder = StateGraph(AgentState)

    # Add all nodes
    builder.add_node("project_planner", run_project_planner)
    builder.add_node("file_architect", run_file_architect)

    # This is a "dummy" node that just routes
    builder.add_node("file_queue_check", lambda state: state)

    # new node that prepares the next file to be worked on
    builder.add_node("prepare_next_file", prepare_next_file_node)

    builder.add_node("coder", run_code)
    builder.add_node("critic", run_critic)
    builder.add_node("commit_code", commit_code_to_workspace)

    # ---Define the graph flow ( edges ) --

    # 1. Planner Edge
    builder.add_edge(START, "project_planner")

    # 2. Planner -> Architect
    builder.add_edge("project_planner", "file_architect")
    builder.add_edge("file_architect", "file_queue_check")

    # 3. Architect -> Conditional Edge 1
    builder.add_conditional_edges(
        "file_queue_check",
        decide_which_file_to_code,
        # If files are there start loop, no files then end
        {
            "prepare_next_file": "prepare_next_file",
            "END": END,
        },
    )

    # 4. Connect prepare_file to coder edge
    builder.add_edge("prepare_next_file", "coder")

    # 5. Self Correction Loop (Critic -> Conditional Edge 2 (The Coder Loop))
    builder.add_edge("coder", "critic")
    builder.add_conditional_edges(
        "critic",
        check_critique,
        # If 'PERFECT' commit, if flawed retry
        {
            "commit_code": "commit_code",
            "retry_coder": "coder",
        },
    )

    # After committing, go back to check the queue
    builder.add_edge("commit_code", "file_queue_check")

    # Compile the graph
    print("✅ Agent Graph compiled successfully.")

    app = builder.compile()

    # Set the default config (including recursion limit) on the compiled app
    return app.with_config({"recursion_limit": 100})


# --- 3. Create a runnable instance ---

app = create_agent_graph()

# ---4. Main function to run the agent ---


def run_agent(query: str):
    """
    The main entry point to run the agent.
    """

    # Initial state
    initial_state: AgentState = {
        "query": query,
        "project_title": None,
        "project_description": None,
        "tech_stack": None,
        "file_structure": None,
        "file_plans": None,
        "files_to_code_queue": [],
        "current_file": None,
        "current_code_draft": None,
        "critique": None,
        "workspace": {},
        "coder_iterations": 0,
        "logs": [],
    }

    # The 'stream' method lets you see the output of each node
    # as it runs
    final_state = {}

    for step in app.stream(initial_state, config={"recursion_limit": 100}):
        # 'step' is a dictionary where the key is the node name
        # and the value is the output (the updated state dict)
        node_name = list(step.keys())[0]
        node_output = list(step.values())[0]

        yield step

        # Keep track of the final state
        if node_output:
            final_state.update(node_output)
        print(f"\n--- Finished Node: {node_name} ---")

    print("\n--- ✅ Agent Run Complete ---")


if __name__ == "__main__":
    # Test the full agent
    test_query = "Build a simple counter app with HTML, CSS, and JS. It needs a number, an increment button, and a decrement button."

    workspace = run_agent(test_query)

    save_workspace_to_disk(workspace, "project_output")

    print("\n\n--- 🚀 FINAL WORKSPACE 🚀 ---")
    for filename, code in workspace.items():
        print(f"\n--- 📄 {filename} ---")
        print(code)
        print("--------------------")
