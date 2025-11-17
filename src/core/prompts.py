from langchain_core.prompts import PromptTemplate

# -- 1. Project Planner Prompt --
# Takes the user query and creates the high-level plan.
# Input: {query}
# Output: ProjectPlan (JSON)

PLANNER_TEMPLATE = """
You are an expert software project manager. Your job is to take a user's 
request and create a high-level project plan.

Analyze the user's request:
"{query}"

Based on this, generate a project title, a single-sentence project 
description, a list of the required tech stack (e.g., HTML, CSS, JS), 
and a complete list of all necessary filenames (file_structure).
"""

PLANNER_PROMPT = PromptTemplate(template=PLANNER_TEMPLATE, input_variables=["query"])

# --- 2. File Architect Prompt ---
# Takes the high-level plan and creates a plan for *each* file.
# Input: {project_description}, {tech_stack}, {file_structure}
# Output: FilePlans (JSON)

ARCHITECT_TEMPLATE = """
You are a senior software architect. Your job is to create a detailed, 
step-by-step implementation plan for *each* file in a project.

Here is the high-level plan:
Project Description: {project_description}
Tech Stack: {tech_stack}
File Structure: {file_structure}

Your response *MUST* be a single, valid JSON dictionary.
The keys of the dictionary *MUST* be the filenames.
The value for each filename *MUST* be a SINGLE STRING containing the
detailed, step-by-step plan for that file.

*DO NOT* use a list of steps. The plan must be one single block of text.

Example of your *EXACT* output format:
{{
  "index.html": "1. Create the basic HTML structure. 2. Add a main div with id 'app'. 3. Inside 'app', add a heading, a span for the count, and two buttons.",
  "style.css": "1. Center the app container. 2. Style the buttons..."
}}

Do *NOT* add any other text, explanations, or markdown formatting (like ```json).
Your response must *START* with {{ and *END* with }}.
"""

ARCHITECT_PROMPT = PromptTemplate(
    template=ARCHITECT_TEMPLATE,
    input_variables=["project_description", "tech_stack", "file_structure"],
)

# --- 3. Coder Prompts (First Draft & Correction) ---

# 3a. First Draft
# Takes a file plan and writes the first version of the code.
# Input: {current_file}, {file_plan}
# Output: Raw Code (string)

CODER_TEMPLATE = """
You are an expert web developer. Your task is to write the *full and complete* code for the following file, based on the provided plan.

File to write: {current_file}
Plan:
{file_plan}

Important: Respond *only* with the raw code for this file.
Do not add *any* other text, explanations, or markdown formatting (like ```)
around the code.
"""

CODER_PROMPT = PromptTemplate(
    template=CODER_TEMPLATE, input_variables=["current_file", "file_plan"]
)


# 3b. Correction
# Takes a critique and a previous draft, then fixes the code.
# Input: {current_file}, {file_plan}, {critique}, {current_code_draft}
# Output: Raw Code (string)

CODER_CORRECTION_TEMPLATE = """
You are an expert web developer. Your previous code draft for {current_file} 
was flawed. You must fix it.

Original Plan:
{file_plan}

Your Previous Draft:
{current_code_draft}

Critique from Reviewer:
{critique}

Generate the *new, corrected, and complete* code for the *entire* file 
based on the critique.

Important: Respond *only* with the raw, corrected code.
Do not add *any* other text, explanations, or markdown formatting.
"""

CODER_CORRECTION_PROMPT = PromptTemplate(
    template=CODER_CORRECTION_TEMPLATE,
    input_variables=["current_file", "file_plan", "critique", "current_code_draft"],
)

# --- 4. Critic Prompt ---
# Reviews the code against the plan and either says "PERFECT" or gives a critique.
# Input: {current_file}, {file_plan}, {current_code_draft}
# Output: "PERFECT" or Critique (string)

CRITIC_TEMPLATE = """
You are an expert code reviewer and quality assurance specialist. 
Your job is to review the code draft against its implementation plan.

File: {current_file}

Plan:
{file_plan}

Code Draft:
{current_code_draft}

Review the draft. Does it *perfectly and completely* implement the plan?

- If YES: Respond with only the single word: PERFECT
- If NO: Provide a concise, actionable critique of what is wrong or 
  missing. Do not say 'PERFECT' if even a small part is missing.
"""

CRITIC_PROMPT = PromptTemplate(
    template=CRITIC_TEMPLATE,
    input_variables=["current_file", "file_plan", "current_code_draft"],
)
