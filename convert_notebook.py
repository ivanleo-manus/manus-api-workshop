#!/usr/bin/env python3
"""Convert Jupyter notebook to Markdown file."""

import json
import re
import sys
from pathlib import Path


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def convert_notebook_to_markdown(notebook_path: str, output_path: str = None):
    """Convert a Jupyter notebook to Markdown format.
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Optional output path for .md file (defaults to same name with .md extension)
    """
    notebook_file = Path(notebook_path)
    
    if not notebook_file.exists():
        print(f"Error: File not found: {notebook_path}")
        sys.exit(1)
    
    # Set output path
    if output_path is None:
        output_path = notebook_file.with_suffix('.md')
    else:
        output_path = Path(output_path)
    
    # Read the notebook
    with open(notebook_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Convert to markdown
    markdown_lines = []
    
    for cell in notebook.get('cells', []):
        cell_type = cell.get('cell_type')
        source = cell.get('source', [])
        
        # Handle source as list or string
        if isinstance(source, list):
            content = ''.join(source)
        else:
            content = source
        
        if cell_type == 'markdown':
            # Add markdown cell content directly
            markdown_lines.append(content)
            markdown_lines.append('\n')
        
        elif cell_type == 'code':
            # Add code cell with syntax highlighting
            markdown_lines.append('```python\n')
            markdown_lines.append(content)
            if not content.endswith('\n'):
                markdown_lines.append('\n')
            markdown_lines.append('```\n\n')
            
            # Optionally include outputs
            outputs = cell.get('outputs', [])
            if outputs:
                markdown_lines.append('**Output:**\n\n')
                for output in outputs:
                    output_type = output.get('output_type')
                    
                    if output_type == 'stream':
                        text = ''.join(output.get('text', []))
                        text = strip_ansi_codes(text)
                        markdown_lines.append('```\n')
                        markdown_lines.append(text)
                        markdown_lines.append('```\n\n')
                    
                    elif output_type in ['execute_result', 'display_data']:
                        # Handle text/plain output
                        data = output.get('data', {})
                        if 'text/plain' in data:
                            text = ''.join(data['text/plain'])
                            text = strip_ansi_codes(text)
                            markdown_lines.append('```\n')
                            markdown_lines.append(text)
                            markdown_lines.append('\n```\n\n')
                    
                    elif output_type == 'error':
                        markdown_lines.append('```\n')
                        markdown_lines.append('\n'.join(output.get('traceback', [])))
                        markdown_lines.append('\n```\n\n')
    
    # Write the markdown file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown_lines))
    
    print(f"✓ Converted {notebook_path} to {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_notebook.py <notebook.ipynb> [output.md]")
        sys.exit(1)
    
    notebook_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_notebook_to_markdown(notebook_path, output_path)
