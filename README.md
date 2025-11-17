# 🤖 Code Buddy

Your AI partner for turning ideas into web applications. Code Buddy is an intelligent AI agent that takes natural language descriptions and generates complete, working web applications with HTML, CSS, and JavaScript.

## ✨ Features

- 🎯 **Natural Language Input**: Describe your app idea in plain English
- 🏗️ **Intelligent Planning**: AI creates a structured project plan with file architecture
- 💻 **Automated Code Generation**: Generates complete, working code for all files
- 🔍 **Self-Correction**: Built-in critic system reviews and improves code quality
- 👁️ **Live Preview**: View your generated app in the browser
- 📥 **Easy Export**: Download your complete project as a ZIP file
- 📊 **Real-time Logs**: Track the generation process step-by-step

## 🏛️ Architecture

Code Buddy uses a **LangGraph-based agentic workflow** with multiple specialized nodes:

```
┌─────────────────────────────────────────────────────────────┐
│                        START                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE 1: Project Planner                                     │
│  • Analyzes user query                                       │
│  • Creates project title & description                       │
│  • Defines tech stack                                        │
│  • Lists required files                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE 2: File Architect                                      │
│  • Creates detailed plan for each file                       │
│  • Defines implementation steps                              │
│  • Initializes file queue                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  CONDITIONAL: File Queue Check                               │
│  • Has files? → Prepare next file                            │
│  • Empty? → END                                              │
└──────────────┬───────────────────────┬──────────────────────┘
               │                       │
       (has files)                 (empty)
               │                       │
               ▼                       ▼
┌────────────────────────┐      ┌──────────┐
│ Prepare Next File      │      │   END    │
└──────────┬─────────────┘      └──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE 3: Coder                                               │
│  • Writes code based on file plan                            │
│  • First draft OR correction based on critique               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE 4: Critic                                              │
│  • Reviews code against plan                                 │
│  • Returns "PERFECT" or detailed critique                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  CONDITIONAL: Check Critique                                 │
│  • PERFECT? → Commit code                                    │
│  • Has issues? → Back to Coder (max 3 iterations)            │
└───────────┬──────────────────────┬─────────────────────────┘
            │                      │
       (PERFECT)            (needs revision)
            │                      │
            ▼                      │
┌────────────────────┐             │
│  Commit Code       │             │
│  • Save to workspace│            │
│  • Clear temp vars │             │
└─────────┬──────────┘             │
          │                        │
          └────────────────────────┘
          │
          └──► Back to File Queue Check (next file)
```

### Graph Flow Details

1. **Project Planner**: Takes user query → outputs structured plan
2. **File Architect**: Takes project plan → outputs detailed file plans
3. **File Queue Loop**: Iterates through each file that needs to be coded
4. **Coder-Critic Loop**: Self-correction loop with up to 3 iterations per file
   - Coder writes/revises code
   - Critic reviews code
   - If not perfect, loops back to Coder
   - If perfect (or max iterations), commits to workspace
5. **Workspace**: Accumulates all finalized files

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google API Key (for Gemini models)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd code-buddy
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

   To get a Google API key:

   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste it into your `.env` file

### Running the Application

```bash
streamlit run src/app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage

1. **Enter your app idea** in the text area

   - Example: "make a simple to-do app in which user can add notes and delete them. User should be able to view the notes."

2. **Click "Generate Web App"** to start the AI agent

3. **Watch the progress** as Code Buddy:

   - Plans your project
   - Designs the file structure
   - Writes and reviews code for each file

4. **View results**:
   - Expand generated files to see the code
   - Check logs to see the generation process
   - Preview your app in a new tab
   - Download the complete project as a ZIP file

## 📁 Project Structure

```
code-buddy/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py          # Main LangGraph workflow
│   │   ├── llm.py             # LLM configuration
│   │   └── state.py           # Agent state definition
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── project_planner.py # Node 1: Project planning
│   │   ├── file_architect.py  # Node 2: File architecture
│   │   └── coder_loop.py      # Nodes 3-4: Code generation & review
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parsers.py         # Pydantic models for structured output
│   │   ├── prompts.py         # LLM prompt templates
│   │   └── store.py           # Workspace storage utilities
│   └── app.py                 # Streamlit UI
├── requirements.txt
├── .env                       # Your API keys (create this)
└── README.md
```

## 🛠️ Technologies Used

- **LangGraph**: Agentic workflow orchestration
- **LangChain**: LLM integration and prompt management
- **Google Gemini 2.0**: AI model for code generation
- **Streamlit**: Web interface
- **Python-dotenv**: Environment variable management

## ⚙️ Configuration

### Customizing the LLM

Edit `src/agent/llm.py` to change:

- Model name (default: `gemini-2.0-flash`)
- Temperature settings
- Add custom LLM configurations

### Adjusting Iteration Limits

In `src/agent/graph.py`, modify:

- `recursion_limit`: Maximum graph steps (default: 100)
- Coder iterations per file: Check `check_critique()` function (default: 3)

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with ❤️ using LangGraph, LangChain, and Google's Gemini models.

---

**Happy Coding! 🚀**
