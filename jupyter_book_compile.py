import nbformat as nbf
import re
import os
import shutil
import glob

# Constants
SRC_DIR = "../lectures"
DST_DIR = "../jupyter-book"
URL = "https://yongkaw.people.clemson.edu/ece4420"


def modify_notebook_metadata(ntbk):
    """Remove specific metadata from the notebook."""
    metadata_keys_to_remove = ["jupytext", "toc", "vscode", "celltoolbar"]
    for key in metadata_keys_to_remove:
        ntbk.metadata.pop(key, None)


def modify_markdown_cells(ntbk):
    """Modify markdown cells to replace image paths."""
    for cell in ntbk.cells:
        if cell.cell_type == "markdown" and cell.source:
            cell.source = re.sub('src="img/', f'src="{URL}/img/', cell.source)


def modify_ipynb(input_file, output_file):
    """Read, modify and write Jupyter notebooks."""
    try:
        ntbk = nbf.read(input_file, nbf.NO_CONVERT)
        modify_notebook_metadata(ntbk)
        modify_markdown_cells(ntbk)
        nbf.write(ntbk, output_file, version=nbf.NO_CONVERT)
    except IOError as e:
        print(f"Error processing file {input_file}: {e}")


def copy_and_tweak_files():
    """Copy and tweak ipynb and md files from lectures to jupyter-book."""
    for root, dirs, files in os.walk(SRC_DIR, topdown=False):
        for name in files:
            if "checkpoint" in name:
                continue

            src_file = os.path.join(root, name)
            dst_file = os.path.join(DST_DIR, name)

            # Process .ipynb files
            if name.endswith(".ipynb"):
                modify_ipynb(src_file, dst_file)

            # Process .md files only if the corresponding .ipynb file does not exist
            elif name.endswith(".md"):
                base_name = os.path.splitext(name)[0]
                ipynb_file = f"{base_name}.ipynb"
                if not os.path.exists(os.path.join(SRC_DIR, ipynb_file)):
                    shutil.copy(src_file, dst_file)


def clean():
    """Remove specific files and directories."""
    files_to_remove = ["*.ipynb", "b01_attribution.md", "b02_LICENSE.md"]
    directories_to_remove = ["cache", "_build/jupyter_execute", "_build/.doctrees"]

    # Uncomment the following line if you want to remove the 'img' directory
    # directories_to_remove.append("img")

    for pattern in files_to_remove:
        for file_path in glob.glob(os.path.join(DST_DIR, pattern)):
            os.remove(file_path)

    for directory in directories_to_remove:
        full_path = os.path.join(DST_DIR, directory)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)


def modify_html_files(modify_names=True, remove_buttons=True):
    """Modify HTML files to optionally remove download buttons and/or modify download names."""
    directory = os.path.join(DST_DIR, "_build/html")

    # Regex patterns for modifications
    remove_pattern = r'<div class="dropdown dropdown-download-buttons">.*?</div>'
    modify_pattern = r'(<a href="_sources/([^"]+)" target="_blank")'
    modify_replacement = r'<a href="_sources/\2" download="\2" target="_blank"'

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Remove download buttons if specified
                if remove_buttons:
                    content = re.sub(remove_pattern, "", content, flags=re.DOTALL)

                # Modify download name if specified
                if modify_names:
                    content = re.sub(modify_pattern, modify_replacement, content)

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)

                print(f"Modified: {file_path}")
            except IOError as e:
                print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    copy_and_tweak_files()
    os.system("jupyter-book build .")
    clean()
    modify_html_files(modify_names=True, remove_buttons=True)
    shutil.copy(".htaccess", "_build/html")
