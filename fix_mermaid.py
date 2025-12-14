import re

# Read the file
with open('templates/emergency_protocol.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the mermaid div section and remove indentation from flowchart lines
# Pattern to match lines within the mermaid div that have leading spaces
pattern = r'(<div class="mermaid">)(.*?)(</div>)'

def remove_indentation(match):
    opening = match.group(1)
    mermaid_content = match.group(2)
    closing = match.group(3)
    
    # Split into lines and remove leading whitespace from each line
    lines = mermaid_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove leading whitespace but preserve the line
        cleaned_line = line.lstrip()
        if cleaned_line:  # Only add non-empty lines
            cleaned_lines.append(cleaned_line)
    
    # Join back with newlines
    cleaned_content = '\n' + '\n'.join(cleaned_lines) + '\n        '
    
    return opening + cleaned_content + closing

# Apply the fix
content = re.sub(pattern, remove_indentation, content, flags=re.DOTALL)

# Write back
with open('templates/emergency_protocol.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Mermaid indentation!")
