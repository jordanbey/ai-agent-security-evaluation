# Research Notes

## Working Question

Can observable runtime signals provide early warning that an autonomous AI agent is deviating from its authorized objective before a harmful or unauthorized action occurs?

## Version 0.1 Hypothesis

A transparent evaluator that combines goal annotations, tool appropriateness, resource scope, task progress, and privilege escalation will detect simple goal-redirection attacks earlier than final-outcome-only monitoring.

## Why the First Attempt Changed

An initial lexical-overlap rule incorrectly treated the legitimate subgoal “write the report” as suspicious because it shared few words with the authorized objective. This false positive demonstrates why goal fidelity cannot be reduced to surface word overlap. Version 0.1 now uses explicit scenario annotations while preserving the failed approach as a documented research lesson.

## Baseline

The first implementation establishes:

- a normalized trace schema,
- interpretable signals,
- a risk timeline,
- first-alert and latency measurements,
- testable normal and adversarial scenarios.

## Evaluation Questions

1. Does the monitor alert before the first harmful action?
2. How often does it alert on benign but unusual behavior?
3. Which signals contribute most to early detection?
4. Can an adaptive attacker preserve apparent goal fidelity while taking harmful actions?
5. How does a rule-based monitor compare with semantic or LLM-based auditors?

## Future Experiment Design

Create a labeled collection of agent traces with:

- normal completion,
- benign detours,
- prompt-injection redirection,
- retrieval poisoning,
- unauthorized tool access,
- delayed or subtle attack behavior.

Measure:

- precision,
- recall,
- false-positive rate,
- missed-detection rate,
- first-alert cycle,
- detection latency relative to compromise,
- detection margin before harmful action.

## Important Limitation

A monitor that only checks consistency with the current subgoal can fail if the subgoal itself has been corrupted. The monitor must preserve and compare against the original authorized objective and policy constraints.
