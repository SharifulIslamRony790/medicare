---
name: Debugging and Troubleshooting Workflow
description: Mandates a strict process for diagnosing issues before making code changes.
---

# Debugging and Troubleshooting Workflow

When the user asks you to investigate a bug, fix an issue, or figure out why something is broken, you MUST follow this strict workflow:

1. **Investigate First**: Do not immediately start editing files. Use your tools (view_file, grep_search, etc.) to investigate the codebase and identify the root cause of the issue.
2. **Explain the Problem**: Clearly explain to the user what the root cause is, how you identified it, and why it is happening.
3. **Propose the Solution**: Outline the exact steps or code changes required to fix the issue.
4. **Wait for Approval**: DO NOT make any code changes yet. Wait for the user to explicitly agree to the solution or ask you to implement it.
5. **Execute**: Once approved, apply the solution exactly as proposed.

**Exception**: If the user explicitly says "fix it" and the fix is trivial (e.g., a simple typo), you may apply the fix immediately, but you must still explain what you did. However, if the user explicitly says "don't change anything yet" or "find the problem", you must strictly adhere to the first 4 steps.
