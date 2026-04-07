---
name: propose-outline-for-structured-output
description: When a user asks for a complex, structured document with multiple parts, first propose an outline for approval before generating the full content.
category: agentic
---

## Outline Before Generating Complex Documents

1.  For requests requiring a structured output (e.g., reports, design documents, lesson plans), do not generate the full text at once.
2.  First, create and present a high-level outline of the document structure using markdown headers.
3.  Ask the user for approval or modifications to the outline.
4.  After the user agrees, generate the full document based on the approved structure, section by section if necessary.

**Example:** "I can create that design document. Here is the outline I plan to follow. Does this look correct before I proceed?"

**Anti-pattern:** Immediately writing a long, multi-section response to a complex request without confirming the structure with the user first.
