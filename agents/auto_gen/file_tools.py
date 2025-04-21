# file_tools.py – File Management and Directory Listing
import os

# --- Utility to get a tree view of current project structure ---
def get_folder_structure(root_path='.'):
    folder_view = []
    for root, dirs, files in os.walk(root_path):
        level = root.replace(root_path, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_view.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            folder_view.append(f"{sub_indent}{f}")
    return '\n'.join(folder_view)

# --- Read contents of a specific file ---
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading {filepath}: {e}]"

# --- Write contents to a file ---
def write_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"[Success writing to {filepath}]"
    except Exception as e:
        return f"[Error writing to {filepath}: {e}]"

# --- List contents of a directory ---
def list_directory(path='.'):
    try:
        return os.listdir(path)
    except Exception as e:
        return f"[Error listing directory {path}: {e}]"
