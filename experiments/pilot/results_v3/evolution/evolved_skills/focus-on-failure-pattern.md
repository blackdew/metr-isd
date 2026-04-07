---
name: focus-on-failure-pattern
description: When analyzing a failed conversation to create a new skill, focus on the reason for the failure itself, not the thematic content of the user's examples.
category: agentic
---

## Target the Root Cause of Failure

1. When a prompt contains examples to illustrate a format, do not treat the *topic* of the example as the subject of the task.
2. Identify the core error in the assistant's failed response (e.g., empty response, wrong format, ignoring instructions).
3. The new skill should provide guidance to prevent that specific error.
4. The goal is to fix the assistant's *behavior*, not to generate more content related to the example's topic.

**Anti-pattern:** The user asks you to fix a formatting error, providing an example about cooking. You create a new skill about cooking instead of a skill about correct formatting.
