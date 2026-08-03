# Module 5 – Secure Tool Use

## Goal

Evaluate how Claude requests tools, how the application enforces policy, and how the model responds to trusted, compromised, conflicting, or unavailable evidence.

Claude proposes tool calls. The application validates, authorizes, executes, and logs them.

## Components

- `tools.py` – simulated security tools
- `validation.py` – authorization and argument checks
- `tool_runner.py` – controlled execution
- `audit_logger.py` – runtime event logging
- `scenarios.py` – evaluation cases
- `demo.py` – scenario runner

## Scenarios

- `trusted_source`
- `compromised_source`
- `conflicting_sources`
- `unauthorized_tool`

Each scenario defines:

- tools exposed to Claude
- tools allowed by policy
- expected tool requests
- expected model behavior

## Current Evaluation

The framework automatically compares expected and observed tool selection.

It also records events such as:

- `tool_requested`
- `tool_executed`
- `tool_blocked`
- `tool_failed`

Claude’s final reasoning is still reviewed manually.

## Security Principles

- The model is not the authorization layer.
- Tool output is untrusted evidence.
- Requests must be validated before execution.
- Runtime behavior should be logged and evaluated.

## Next Steps

- runtime-event PASS/FAIL checks
- semantic response evaluation
- JSON trace export
- integration with `ai-agent-security-evaluation`