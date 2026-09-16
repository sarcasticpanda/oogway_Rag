"""
Artifact parsing and generation utilities.
"""
import re
from typing import Tuple, Optional

def extract_artifact_from_response(response: str) -> Tuple[str, Optional[dict]]:
    """
    Extract artifact tags from LLM response.
    Returns: (cleaned_response, artifact_data)
    
    Supports:
    <artifact type="markdown" title="...">content</artifact>
    <artifact type="html" title="...">content</artifact>
    """
    # Pattern to match artifact tags
    artifact_pattern = r'<artifact\s+type="(\w+)"\s+title="([^"]+)"\s*>(.*?)</artifact>'
    
    match = re.search(artifact_pattern, response, re.DOTALL | re.IGNORECASE)
    if match:
        artifact_type = match.group(1).lower()
        title = match.group(2)
        content = match.group(3).strip()
    else:
        # Accept older providers that emit an untyped artifact wrapper.
        legacy_match = re.search(r'<artifact\s*>(.*?)</artifact>', response, re.DOTALL | re.IGNORECASE)
        if not legacy_match:
            return response, None
        artifact_type = "markdown"
        title = "Generated Artifact"
        content = legacy_match.group(1).strip()
        match = legacy_match
    
    cleaned_response = response[:match.start()] + response[match.end():]
    cleaned_response = cleaned_response.strip()
    artifact_data = {"type": artifact_type, "title": title, "content": content}
    return cleaned_response, artifact_data


def should_generate_artifact(message: str) -> bool:
    """Check if message requests artifact generation."""
    triggers = ['@artifact', '@ship30', '@document', '@report', '@webpage']
    message_lower = message.lower()
    return any(trigger in message_lower for trigger in triggers)


def get_artifact_prompt_instructions(task_type: str = "general") -> str:
    """Get instructions for LLM to generate artifacts."""
    
    base_instructions = """
When generating artifacts, wrap your output in artifact tags:

<artifact type="markdown" title="Your Title Here">
# Your Content Here
## Sections
- Bullet points
- **Bold text**
- *Italic text*
</artifact>

OR for HTML:

<artifact type="html" title="Your Title Here">
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <!-- Your HTML here -->
</body>
</html>
</artifact>

The artifact will be displayed in a side panel. Keep the main chat response brief and conversational.
Use the supplied evidence as source material, not as text to copy. Build a coherent deliverable with a clear purpose, useful organization, and explicit source traceability. Never invent details that are absent from the evidence.
"""
    
    if task_type == "ship30":
        return base_instructions + """
For Ship 30 for 30 essays:
- Use markdown format
- Target 1,150-1,350 words
- Strong hook in first paragraph
- Clear structure with headers
- Actionable takeaway at end
- Ground all claims in Lenny transcript evidence
"""

    if task_type == "html":
        return base_instructions + "\nPrefer type=\"html\" with self-contained HTML and CSS. Ensure the body contains the requested deliverable, not just raw source excerpts."
    if task_type in {"summary", "report", "checklist"}:
        return base_instructions + f"\nCreate a useful {task_type} in Markdown with clear sections, actionable detail, and a short Evidence/Source basis section. For a checklist, turn source requirements into verifiable checklist items; do not add generic filler."
    
    return base_instructions
