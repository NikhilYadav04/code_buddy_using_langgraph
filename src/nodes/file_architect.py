from langchain_core.runnables import Runnable
from agent.state import AgentState
from agent.llm import get_file_architect_llm
from core.prompts import ARCHITECT_PROMPT
from core.parsers import FilePlans
from langchain_core.messages import AIMessage
import json


def clean_json_response(raw_text: str) -> str:
    """
    Cleans the LLM's raw text output to extract just the JSON.
    """
    # Remove markdown backticks
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]

    # Find the first '{' and the last '}'
    start_index = raw_text.find("{")
    end_index = raw_text.rfind("}")

    if start_index == -1 or end_index == -1:
        raise ValueError("No valid JSON object found in the LLM response.")

    return raw_text[start_index : end_index + 1]


def run_file_architect(state: AgentState) -> dict:
    """
    Runs the file architect node with manual JSON parsing.
    """

    logs = state.get("logs", [])
    logs.append("✅ Starting File Architecture Phase...")

    # ... (Get state components, llm, chain, prompt_input ) ...
    project_description = state["project_description"]
    tech_stack = state["tech_stack"]
    file_structure = state["file_structure"]
    architect_llm: Runnable = get_file_architect_llm()

    chain = ARCHITECT_PROMPT | architect_llm
    prompt_input = {
        "project_description": project_description,
        "tech_stack": tech_stack,
        "file_structure": file_structure,
    }

    try:
        # 1. Invoke the chain, get raw AIMessage
        response: AIMessage = chain.invoke(prompt_input)
        raw_response_text = response.content
        logs.append("✅ Received response from architect LLM.")

        # 2. Clean the raw text to get JSON
        print(f"    > LLM Raw Output: {raw_response_text[:100]}...")
        json_text = clean_json_response(raw_response_text)

        # 3. Manually parse the JSON string to get the dictionary
        file_plans = json.loads(json_text)

        # 4. Check
        if not file_plans:
            raise ValueError("LLM generated empty plans.")

        # 5. Sanitize the dictionary keys
        sanitized_file_plans = {k.strip().lower(): v for k, v in file_plans.items()}

        print(f"    > Generated {len(sanitized_file_plans)} file plans.")
        print(f"    > Architect plans keys: {list(sanitized_file_plans.keys())}")

        logs.append(f"📁 File plans generated: {len(sanitized_file_plans)} files.")
        logs.append(f"✅ Ready to start coding phase.")

        # 6. PREPARE the state for the Coder Loop
        return {
            "file_plans": sanitized_file_plans,
            "files_to_code_queue": file_structure,
            "workspace": {},
            "current_file": None,
            "current_code_draft": None,
            "critique": None,
            "coder_iterations": 0,
            "logs": logs,
        }

    except Exception as e:
        logs.append(f"❌ Error in File Architect: {str(e)}")
        print(f"    > ERROR in File Architect: {e}")
        return {"logs": logs}


# test
if __name__ == "__main__":
    test_state = {
        "query": "build me a simple to-do list app",
        "project_description": "A simple to-do list app using HTML, CSS, and JS.",
        "tech_stack": ["HTML", "CSS", "JavaScript"],
        "file_structure": ["index.html", "style.css", "app.js"],
    }

    # Cast to AgentState for type checking, though it's just a dict at runtime
    result = run_file_architect(test_state)

    print("\n--- Test Result ---")
    import json

    print(json.dumps(result, indent=2))
