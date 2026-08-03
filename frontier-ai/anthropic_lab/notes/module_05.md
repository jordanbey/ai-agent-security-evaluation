# Module 5 – Secure Tool Use

## What I Learned

Claude does not execute Python functions directly. It requests tools, and the application decides whether to execute them.

The tool lifecycle is:

```text
User → Claude → Tool Request → Validation → Execution or Block → Tool Result → Claude