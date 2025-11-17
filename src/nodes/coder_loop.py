from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage
from agent.state import AgentState
from agent.llm import get_coder_llm, get_critic_llm
from core.prompts import CODER_PROMPT, CODER_CORRECTION_PROMPT, CRITIC_PROMPT


def run_code(state: AgentState) -> dict:
    """
    Runs the coder node.

    This node writes code for the 'current_file' based on its plan.
    It will either write a first draft or correct a previous,
    critiqued draft.
    """
    logs = state.get("logs", [])

    # Get the state components
    current_file = state["current_file"]
    file_plan = state["file_plans"][current_file]
    critique = state.get("critique")
    current_code_draft = state.get("current_code_draft")
    current_code_draft = state["current_code_draft"]

    # Get teh LLM and prompt
    code_llm: Runnable = get_coder_llm()

    if critique:
        # We are in a correction loop
        print(f"    > Correcting code for {current_file} based on critique...")
        logs.append(f"✍️ Fixing code for **{current_file}** based on critique...")
        prompt = CODER_CORRECTION_PROMPT
        prompt_input = {
            "current_file": current_file,
            "file_plan": file_plan,
            "critique": critique,
            "current_code_draft": current_code_draft,
        }
    else:
        # This is the first draft
        print(f"    > Writing first draft for {current_file}...")
        logs.append(f"🆕 Writing first draft for **{current_file}**...")
        prompt = CODER_PROMPT
        prompt_input = {"current_file": current_file, "file_plan": file_plan}

    # Create the chain for this node
    chain = prompt | code_llm

    try:
        # Invoke the chain which gives an AI message, extract its content
        response = chain.invoke(prompt_input)
        new_code_draft = response.content.strip()

        # Clean up any markdown formatting
        if new_code_draft.startswith("```"):
            new_code_draft = new_code_draft.split("\n", 1)[1]
            if new_code_draft.endswith("```"):
                new_code_draft = new_code_draft.rsplit("\n", 1)[0]

        logs.append(f"✅ Code draft for **{current_file}** generated.")

        # Return
        return {
            "current_code_draft": new_code_draft,
            "coder_iterations": state["coder_iterations"] + 1,
            "critique": None,  # Clear the critique after using it
            "logs": logs,
        }
    except Exception as e:
        logs.append(f"❌ Error in coder: {str(e)}")
        print(f"    > ERROR in Coder: {e}")
        return {"logs": logs}


def run_critic(state: AgentState) -> dict:
    """
    Runs the critic node.

    This node reviews the 'current_code_draft' against the 'file_plan'
    and either responds with "PERFECT" or a critique.
    """
    print(f"--- 3b. RUNNING CRITIC ---")
    logs = state.get("logs", [])

    # Get the necessary state components
    current_file = state["current_file"]
    file_plan = state["file_plans"][current_file]
    current_code_draft = state["current_code_draft"]

    # Get the critic llm
    critic_llm: Runnable = get_critic_llm()

    # Create the chain for this node
    chain = CRITIC_PROMPT | critic_llm

    # Prepare the input for the prompt
    prompt_input = {
        "current_file": current_file,
        "file_plan": file_plan,
        "current_code_draft": current_code_draft,
    }

    try:
        # Invoke the chain
        response = chain.invoke(prompt_input)
        critique_text = response.content.strip()

        if "PERFECT" in critique_text.upper():
            logs.append(f"✅ {current_file} passed review with **PERFECT**.")
            print(f"    > Critique for {current_file}: PERFECT")
            return {"critique": "PERFECT", "logs": logs}
        else:
            logs.append(f"🛠 Found issues in **{current_file}**:\n{critique_text}")
            print(f"    > Critique for {current_file}: \n{critique_text}")
            return {"critique": critique_text, "logs": logs}

    except Exception as e:
        logs.append(f"❌ Error in critic: {str(e)}")
        print(f"    > ERROR in Critic: {e}")
        return {"logs": logs}
