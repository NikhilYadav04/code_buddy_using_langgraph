from typing import TypedDict, List, Dict, Optional


class AgentState(TypedDict):
    """
    The state of our AI developer agent.
    This object is passed between all nodes and updated at each step
    """

    # ---Input----
    # User prompt
    query: str

    # ---Node 1 Output: Project Plan --
    project_title: Optional[str]
    project_description: Optional[str]
    tech_stack: Optional[List[str]]
    file_structure: Optional[List[str]]  # e.g., ["index.html", "style.css", "app.js"]

    # ---Node 2 Output: File-by-File Plan---
    file_plans: Optional[Dict[str, str]]  # Maps filename -> detailed plan

    # -- Node 3 ( Code Loop ) State ----

    files_to_code_queue: List[str]

    current_file: Optional[str]

    current_code_draft: Optional[str]

    # to check if critique is there or not
    critique: Optional[str]

    # The *final* code, built up file by file.
    workspace: Dict[str, str]  # Maps filename -> "PERFECT" code

    # A counter to prevent infinite loops in the coder
    coder_iterations: int

    # for user logs
    logs: List[str]
