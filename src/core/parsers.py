from pydantic import BaseModel, Field
from typing import List, Dict


class ProjectPlan(BaseModel):
    """
    The structured output for Node 1 (project_planner).
    This defines the high-level project overview.
    """

    project_title: str = Field(description="A short, catchy title for the project.")
    project_description: str = Field(
        description="A single-sentence description of what the project does."
    )
    tech_stack: List[str] = Field(
        description="The list of technologies to be used, e.g., ['HTML', 'CSS', 'JavaScript']."
    )
    file_structure: List[str] = Field(
        description="The complete list of filenames required for the project, e.g., ['index.html', 'style.css', 'app.js']."
    )


class FilePlans(BaseModel):
    """
    The structured output for Node 2 (file_architect).
    This model *is* the dictionary of file plans.
    """

    root: Dict[str, str] = Field(
        description="A dictionary where each key is a filename (from the file_structure) "
        "and the value is a detailed, step-by-step plan for coding that specific file."
    )
