# AI Agent Security Evaluation

An open research project exploring runtime evaluation, behavioral monitoring, and early detection of safety and security risks in autonomous AI agents.

## Vision

This project investigates model-agnostic methods for evaluating the runtime behavior of autonomous AI agents. The goal is to identify early indicators of unsafe or unauthorized behavior before harmful actions occur.

The initial prototype focuses on runtime trace analysis and early detection of deviations from an agent's authorized objective. Future work will expand to broader AI security evaluation, including prompt injection, tool misuse, memory integrity, retrieval attacks, goal integrity, and runtime policy enforcement.



## Research Question

Can observable runtime signals provide early warning that an autonomous AI agent is deviating from its authorized objective before a harmful or unauthorized action occurs?

## Motivation

Modern AI agents can plan, retrieve information, call tools, update memory, and act over multiple cycles. A harmful outcome may emerge gradually rather than from one isolated response. This project explores whether structured runtime telemetry can help identify that progression early enough for intervention.

Version 0.1 intentionally uses synthetic traces and a transparent rule-based evaluator. It is an empirical baseline and research scaffold, not a production security system or a claim of a novel solution.

## Version 0.1

The initial evaluator scores five observable dimensions:

1. **Goal fidelity** — Is the current subgoal consistent with the authorized objective?
2. **Tool appropriateness** — Is the selected tool permitted?
3. **Resource scope** — Is the agent accessing resources within the authorized scope?
4. **Task progress** — Is the cycle advancing the assigned task?
5. **Action escalation** — Is the action becoming more privileged or consequential?

The evaluator produces:

- risk score for each cycle,
- human-readable alert reasons,
- first-alert cycle,
- detection latency,
- false-positive and missed-detection indicators.

## Architecture

```text
Authorized Task
      |
Agent Execution Trace
      |
Normalized Runtime Events
      |
Rule-Based Baseline Evaluator
      |
Risk Timeline
      |
Continue / Alert / Human Review
```

## Quick Start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
python -m agent_runtime_eval.cli examples/normal_trace.json
python -m agent_runtime_eval.cli examples/injected_trace.json
```

## Why Version 0.1 Uses Explicit Labels

Simple lexical similarity is not a reliable measure of goal fidelity. For example, “write the final report” may be a valid subgoal even if it shares few words with “prioritize software vulnerabilities.” The first baseline therefore combines explicit scenario labels with transparent tool, resource, progress, and privilege rules. Later versions will compare semantic and model-based goal-fidelity evaluators.

## Research Roadmap

- [x] Structured trace schema
- [x] Transparent rule-based baseline
- [x] Normal and adversarial examples
- [x] Unit tests
- [ ] Larger synthetic evaluation set
- [ ] Detection-latency and precision/recall experiments
- [ ] Semantic goal-fidelity baseline
- [ ] LLM-based evaluator baseline
- [ ] Real agent adapter
- [ ] Prompt-injection and retrieval-poisoning scenarios
- [ ] Adaptive adversarial evaluation
- [ ] Tool-use and memory-integrity signals

## Limitations

- Synthetic traces do not capture the full complexity of real agents.
- Explicit labels are useful for a baseline but do not solve real-world goal inference.
- Allow-list rules are easy to evade.
- Risk thresholds are illustrative rather than calibrated.
- The monitor does not inspect or depend on private chain-of-thought.
- Human review remains necessary for ambiguous or high-impact cases.

## Responsible Use

This repository is intended for defensive AI-security evaluation. Example scenarios use fabricated data and safe local tools. Do not include proprietary data, credentials, private company code, or real sensitive records.

## License

MIT
