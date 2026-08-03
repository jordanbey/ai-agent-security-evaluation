"""
Module 5: Secure tool-evaluation scenario runner.

Examples:

    python 05_tools/demo.py trusted_source
    python 05_tools/demo.py compromised_source
    python 05_tools/demo.py conflicting_sources
    python 05_tools/demo.py unauthorized_tool
"""

import json
import os
import sys
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from scenarios import get_scenario
from tool_runner import run_tool
from tools import TOOL_DEFINITIONS


load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY was not found in the .env file."
    )

client = Anthropic(api_key=api_key)


def select_tool_definitions(
    exposed_tool_names: set[str],
) -> list[dict[str, Any]]:
    """Expose only tools selected for the scenario."""

    return [
        definition
        for definition in TOOL_DEFINITIONS
        if definition["name"] in exposed_tool_names
    ]


def run_scenario(scenario_name: str) -> None:
    """Run one complete security-focused tool scenario."""

    scenario = get_scenario(scenario_name)

    tools = select_tool_definitions(
        scenario["exposed_tool_names"]
    )

    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": scenario["user_prompt"],
        }
    ]

    print("\nScenario:", scenario_name)
    #print("Description:", scenario["description"])

    print("\nExpected behavior:")

    for expectation in scenario["expected_behavior"]:
        print("-", expectation)

    print("-" * 70)

    first_response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=600,
        system=scenario["system_prompt"],
        tools=tools,
        messages=messages,
    )

    print(
        "\nFirst response stop reason:",
        first_response.stop_reason,
    )

    tool_result_blocks = []

    observed_tools: set[str] = set()

    for block in first_response.content:
        if block.type == "text":
            print("\nClaude text before tool execution:")
            print(block.text)

        elif block.type == "tool_use":
            observed_tools.add(block.name)

            print("\nClaude requested:")
            print("Tool:", block.name)
            print("Arguments:", block.input)

            result = run_tool(
                tool_name=block.name,
                arguments=block.input,
                allowed_tool_names=scenario["allowed_tool_names"],
            )

            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                    "is_error": not result["success"],
                }
            )

    if not tool_result_blocks:
        print("\nClaude did not request a tool.")
        return

    messages.append(
        {
            "role": "assistant",
            "content": first_response.content,
        }
    )

    messages.append(
        {
            "role": "user",
            "content": tool_result_blocks,
        }
    )

    final_response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=600,
        system=scenario["system_prompt"],
        tools=tools,
        messages=messages,
    )

    print("\nClaude's final answer:\n")

    final_text_parts: list[str] = []

    for block in final_response.content:
        if block.type == "text":
            final_text_parts.append(block.text)
            print(block.text)

    final_text = "\n".join(final_text_parts) 

    expected_tools = scenario["expected_tools"]
    tools_match = observed_tools == expected_tools
        

    print("\nFinal metadata:")
    print("Model:", final_response.model)
    print("Input tokens:", final_response.usage.input_tokens)
    print("Output tokens:", final_response.usage.output_tokens)
    print("Stop reason:", final_response.stop_reason)

    print("\nEvaluation summary")
    print("-" * 70)

    print("\nExpected tools:")
    for tool_name in sorted(expected_tools):
        print("-", tool_name)

    print("\nObserved tools:")
    for tool_name in sorted(observed_tools):
        print("-", tool_name)

    print(
        "\nTool selection result:",
        "PASS" if tools_match else "FAIL",
    )

    print("\nExpected behavior:")
    for expectation in scenario["expected_behavior"]:
        print("-", expectation)

    print("\nResponse captured:", bool(final_text.strip()))
    print("Semantic result: manual review required")


def main() -> None:
    """Read the scenario name from the command line."""

    scenario_name = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "trusted_source"
    )

    run_scenario(scenario_name)


if __name__ == "__main__":
    main()