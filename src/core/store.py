import os


def save_workspace_to_disk(workspace: dict, base_dir: str = "src/output"):
    """
    Saves the generated workspace files to a specified directory.
    """
    print(f"\n--- 💾 SAVING PROJECT TO FOLDER: {base_dir} ---")

    # 1. Create the base directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)

    # 2. Loop through each file in the workspace
    for filename, code_content in workspace.items():
        file_path = os.path.join(base_dir, filename)

        # This line gets the directory part of the path (e.g., "project_output/src" or creates if needed)
        file_dir = os.path.dirname(file_path)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)

        # 4. Write the code to the file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            print(f"    > Created file: {file_path}")
        except Exception as e:
            print(f"    > ERROR saving {filename}: {e}")

    print("--- ✅ PROJECT SAVED ---")
