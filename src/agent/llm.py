import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our custom parsers
from core.parsers import ProjectPlan, FilePlans

load_dotenv()


def get_google_api_key():
    """Fetches the Google API key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in .env file. "
            "Please create a .env file and add: GOOGLE_API_KEY='your_key_here'"
        )
    return api_key


def create_structured_llm(
    model_name: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    parser_schema: type[BaseModel] = None,
) -> Runnable:
    """
    Creates an LLM instance bound with a specific Pydantic parser schema.

    Args:
        model_name: The name of the Gemini model to use.
        temperature: The creativity of the model (0.0 = deterministic).
        parser_schema: The Pydantic model (e.g., ProjectPlan) to format the output.

    Returns:
        A Runnable chain that will call the LLM and parse its output
        into the provided schema.
    """
    # Initialize the Gemini Chat model
    llm = ChatGoogleGenerativeAI(
        model=model_name, temperature=temperature, google_api_key=get_google_api_key()
    )

    if parser_schema:
        structured_llm = llm.with_structured_output(parser_schema)
        return structured_llm
    else:
        return llm


# -- Pre-built llm's for agent nodes --

def get_project_planner_llm() -> Runnable:
    """
    Returns a pre-configured LLM that *only* outputs a ProjectPlan.
    """
    return create_structured_llm(parser_schema=ProjectPlan)


def get_file_architect_llm() -> Runnable:
    """
    Returns a standard, non-structured LLM.
    We will parse the output manually in the node.
    """
    return create_structured_llm(
        parser_schema=None,
        model_name="gemini-2.0-flash",
        temperature=0.0,
    )


def get_coder_llm() -> Runnable:
    """
    Returns a standard, non-structured LLM for writing raw code.
    We don't use a parser here because we want the output to be
    the code itself, not a JSON object.
    """
    return create_structured_llm(
        parser_schema=None,
        model_name="gemini-2.0-flash",
        temperature=0.1,
    )


def get_critic_llm() -> Runnable:
    """
    Returns a standard, non-structured LLM for writing critiques.
    The critique is simple text (either "PERFECT" or a critique).
    We use a faster, cheaper model for this.
    """
    return create_structured_llm(
        parser_schema=None,
        model_name="gemini-2.0-flash",
        temperature=0.0,
    )
