import os
import re
import inspect
import importlib
import sys
import ast

def extract_decorated_functions(file_path):
    """Extract decorated functions from a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        decorated_functions = []
        utility_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has decorators
                is_decorated = False
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) or isinstance(decorator, ast.Call):
                        is_decorated = True
                        break
                
                docstring = ast.get_docstring(node)
                
                # Get function parameters
                params = []
                for arg in node.args.args:
                    if arg.arg != 'self':
                        params.append(arg.arg)
                
                function_info = {
                    "name": node.name,
                    "params": ", ".join(params),
                    "docstring": docstring or "No documentation available.",
                    "file": os.path.basename(file_path),
                    "line": node.lineno
                }
                
                if is_decorated:
                    decorated_functions.append(function_info)
                else:
                    # Only add utility functions that aren't private
                    if not node.name.startswith('_'):
                        utility_functions.append(function_info)
        
        return decorated_functions, utility_functions
    
    except SyntaxError as e:
        print(f"Error parsing file {file_path}: {e}")
        return [], []

def extract_tag_definitions(file_path):
    """Extract tag definitions from a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        tag_definitions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and ('tag' in target.id.lower() or 'cut' in target.id.lower()):
                        if isinstance(node.value, ast.List):
                            values = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Str):
                                    values.append(elt.s)
                                elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    values.append(elt.value)
                            
                            tag_definitions.append({
                                "name": target.id,
                                "values": values,
                                "file": os.path.basename(file_path),
                                "line": node.lineno
                            })
        
        return tag_definitions
    
    except SyntaxError as e:
        print(f"Error parsing file {file_path}: {e}")
        return []

def scan_directory(directory):
    """Scan a directory for Python files and extract information."""
    cut_functions = []
    utility_functions = []
    tag_definitions = []
    
    for root, dirs, files in os.walk(directory):
        if "__pycache__" in root:
            continue
        
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(root, file)
                decorated, utilities = extract_decorated_functions(file_path)
                tags = extract_tag_definitions(file_path)
                
                cut_functions.extend(decorated)
                utility_functions.extend(utilities)
                tag_definitions.extend(tags)
    
    return cut_functions, utility_functions, tag_definitions

def generate_markdown(cut_functions, utility_functions, tag_definitions):
    """Generate Markdown documentation."""
    markdown = "# Lantern Analysis Documentation\n\n"
    
    # Add cuts section if there are any
    if cut_functions:
        markdown += "## Registered Cut Functions\n\n"
        
        # Group by file
        cuts_by_file = {}
        for cut in cut_functions:
            file = cut["file"]
            if file not in cuts_by_file:
                cuts_by_file[file] = []
            cuts_by_file[file].append(cut)
        
        for file, cuts in sorted(cuts_by_file.items()):
            markdown += f"### {file}\n\n"
            
            for cut in sorted(cuts, key=lambda x: x["line"]):
                params_str = f"({cut['params']})" if cut['params'] else "()"
                markdown += f"#### `{cut['name']}{params_str}`\n\n"
                markdown += f"{cut['docstring']}\n\n"
    
    # Add utility functions section if there are any
    if utility_functions:
        markdown += "## Utility and Helper Functions\n\n"
        
        # Group by file
        utils_by_file = {}
        for util in utility_functions:
            file = util["file"]
            if file not in utils_by_file:
                utils_by_file[file] = []
            utils_by_file[file].append(util)
        
        for file, utils in sorted(utils_by_file.items()):
            markdown += f"### {file}\n\n"
            
            for util in sorted(utils, key=lambda x: x["line"]):
                params_str = f"({util['params']})" if util['params'] else "()"
                markdown += f"#### `{util['name']}{params_str}`\n\n"
                markdown += f"{util['docstring']}\n\n"
    
    # Add tags section if there are any
    if tag_definitions:
        markdown += "## Tag Definitions\n\n"
        
        # Group by file
        tags_by_file = {}
        for tag in tag_definitions:
            file = tag["file"]
            if file not in tags_by_file:
                tags_by_file[file] = []
            tags_by_file[file].append(tag)
        
        for file, tags in sorted(tags_by_file.items()):
            markdown += f"### {file}\n\n"
            
            for tag in sorted(tags, key=lambda x: x["line"]):
                markdown += f"#### `{tag['name']}`\n\n"
                markdown += "```python\n[\n"
                for value in tag["values"]:
                    markdown += f"    \"{value}\",\n"
                markdown += "]\n```\n\n"
    
    return markdown

def main():
    # Default to the current directory if no arguments are provided
    repo_root = os.path.dirname(os.path.abspath(__file__))
    lantern_dir = os.path.join(repo_root, "lantern_ana")
    
    print(f"Scanning directory: {lantern_dir}")
    
    # Scan for decorated functions, utility functions, and tag definitions
    cut_functions, utility_functions, tag_definitions = scan_directory(lantern_dir)
    
    print(f"Found {len(cut_functions)} decorated functions")
    print(f"Found {len(utility_functions)} utility functions")
    print(f"Found {len(tag_definitions)} tag definitions")
    
    # Generate and save documentation
    markdown = generate_markdown(cut_functions, utility_functions, tag_definitions)
    output_file = os.path.join(repo_root, "CUTS_AND_TAGS.md")
    
    with open(output_file, "w") as f:
        f.write(markdown)
    
    print(f"Documentation generated in {output_file}")

if __name__ == "__main__":
    main()