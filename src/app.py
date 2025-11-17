import streamlit as st
import time
from agent.graph import run_agent
from dotenv import load_dotenv
import os
import io
import zipfile
import streamlit.components.v1 as components
import json


# ✅ Setup
# os.environ["LANGCHAIN_PROJECT"] = "code-buddy"
# load_dotenv()

st.set_page_config(page_title="Code Buddy", page_icon="🤖", layout="centered")

# ✅ Custom CSS styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .log-container {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid #667eea;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ Header
st.markdown('<h1 class="main-header">🤖 Code Buddy</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Your AI partner for turning ideas into web applications</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ✅ Prompt Input
prompt = st.text_area(
    "✨ **Describe your app idea**",
    key="prompt_input",
    placeholder="Example: Build a weather dashboard with search and 5-day forecast",
    height=180,
    help="Be specific about layout and features",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button(
        "🚀 Generate Web App", type="primary", use_container_width=True
    )

# ✅ Button Click Handler (runs agent once)
if run_button:
    if not prompt:
        st.error("⚠️ Please describe your app idea first!")
    else:
        st.markdown("### 🚧 **Building your app...**")

        log_box = st.empty()
        progress = st.progress(0)

        logs = []
        workspace = {}

        step_count = 0
        estimated_steps = 50  # for percentage indicator

        for update in run_agent(prompt):
            step_count += 1
            progress.progress(step_count / estimated_steps)

            state_update = list(update.values())[0]

            # ✅ live update logs
            if "logs" in state_update:
                logs = state_update["logs"]
                log_box.code("\n".join(logs))

            # ✅ live update workspace
            if "workspace" in state_update:
                workspace = state_update["workspace"]
                st.session_state["workspace"] = workspace
                st.session_state["logs"] = logs

        progress.empty()
        st.success("✅ App generation complete!")

# ✅ ---------------- DISPLAY SECTION (persists after rerun) ----------------
if "workspace" in st.session_state:
    workspace = st.session_state["workspace"]
    logs = st.session_state.get("logs", [])

    # ✅ Success box
    st.markdown(
        """
        <div class="success-box">
            <h3 style="margin:0; color:#667eea;">✅ Generation Complete!</h3>
            <p style="margin:0.5rem 0 0 0; color:#666;">Your web app is ready to preview</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ✅ Show generated files
    st.markdown("### 📁 Generated Files")
    for filename, code in workspace.items():
        with st.expander(f"📄 {filename}"):
            language = (
                "html"
                if filename.endswith(".html")
                else "css" if filename.endswith(".css") else "javascript"
            )
            st.code(code, language=language)

    # ✅ Logs
    st.markdown("### 📋 Generation Logs")
    with st.expander("View Logs"):
        st.code("\n".join(logs))

    # ✅ Preview & Download
    col_a, col_b = st.columns(2)

    # ✅ View Playground
    with col_a:
        if st.button("👁️ View Playground", use_container_width=True):
            workspace = st.session_state.get("workspace", {})

            if "index.html" not in workspace:
                st.warning("⚠️ No index.html found — preview works only for web apps.")
            else:
                html = workspace.get("index.html", "")
                css = workspace.get("style.css", "")
                js = workspace.get("app.js", "")

                full_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>{css}</style>
</head>
<body>
{html}
<script>{js}</script>
</body>
</html>
"""

                import base64

                encoded = base64.b64encode(full_html.encode()).decode()

                st.markdown("### ✅ Preview opened in a new tab")

                # ✅ Open preview in new tab
                st.components.v1.html(
                    f"""
                <a href="data:text/html;base64,{encoded}" 
                   target="_blank" id="openPreview"></a>
                <script>
                    document.getElementById('openPreview').click();
                </script>
                """,
                    height=0,
                    scrolling=False,
                )

    # ✅ Download ZIP
    with col_b:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, code in workspace.items():
                zip_file.writestr(filename, code)
        zip_buffer.seek(0)

        st.download_button(
            label="📥 Download Code",
            data=zip_buffer,
            file_name="codebuddy_project.zip",
            mime="application/zip",
            use_container_width=True,
        )
