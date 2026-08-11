import os
from typing import Any, Literal, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    goal: str
    selected_tool: str
    tool_args: dict[str, Any]
    tool_result: str
    memory: list[str]
    risk_score: int
    status: str
    answer: str


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression."""

    allowed = set("0123456789+-*/(). ")

    if not set(expression) <= allowed:
        raise ValueError(
            "Unsupported calculator expression."
        )

    result = eval(
        expression,
        {"__builtins__": {}},
        {},
    )

    return str(result)


@tool
def knowledge_lookup(topic: str) -> str:
    """Return a small internal knowledge entry."""

    knowledge = {
        "rag": (
            "Retrieval-Augmented Generation retrieves "
            "external information before generation."
        ),
        "langgraph": (
            "LangGraph supports stateful workflows "
            "with nodes, edges, routing, and loops."
        ),
        "prompt injection": (
            "Prompt injection attempts to manipulate "
            "an LLM through untrusted instructions."
        ),
    }

    return knowledge.get(
        topic.lower(),
        "No internal knowledge found.",
    )


TOOLS = {
    "calculator": calculator,
    "knowledge_lookup": knowledge_lookup,
}


def create_model() -> ChatAnthropic:
    """Create the Claude model."""

    return ChatAnthropic(
        model="claude-sonnet-5",
    )


def planner(state: AgentState) -> AgentState:
    """Let Claude select an appropriate tool."""

    model = create_model()

    model_with_tools = model.bind_tools(
        list(TOOLS.values())
    )

    response = model_with_tools.invoke(
        state["goal"]
    )

    if not response.tool_calls:
        return {
            **state,
            "selected_tool": "none",
            "tool_args": {},
            "status": "direct_answer",
        }

    tool_call = response.tool_calls[0]

    return {
        **state,
        "selected_tool": tool_call["name"],
        "tool_args": tool_call["args"],
        "status": "tool_selected",
    }


def security_check(
    state: AgentState,
) -> AgentState:
    """Evaluate the selected action before execution."""

    blocked_tools = {
        "delete_system_file",
        "disable_security",
    }

    if state["selected_tool"] in blocked_tools:
        return {
            **state,
            "risk_score": 10,
            "status": "blocked",
        }

    risk_score = 0

    if state["selected_tool"] != "none":
        risk_score += 1

    return {
        **state,
        "risk_score": risk_score,
        "status": "approved",
    }


def route_after_security(
    state: AgentState,
) -> Literal["tool", "answer"]:
    """Route based on security decision."""

    if (
        state["status"] == "approved"
        and state["selected_tool"] != "none"
    ):
        return "tool"

    return "answer"


def execute_tool(
    state: AgentState,
) -> AgentState:
    """Execute the tool selected by Claude."""

    tool_name = state["selected_tool"]

    if tool_name not in TOOLS:
        return {
            **state,
            "tool_result": "",
            "status": "tool_error",
        }

    try:
        selected_tool = TOOLS[tool_name]

        result = selected_tool.invoke(
            state["tool_args"]
        )

        return {
            **state,
            "tool_result": str(result),
            "status": "tool_complete",
        }

    except Exception as exc:
        return {
            **state,
            "tool_result": str(exc),
            "status": "tool_error",
        }


def update_memory(
    state: AgentState,
) -> AgentState:
    """Store the tool observation in working memory."""

    memory = list(state["memory"])

    if state["selected_tool"] != "none":
        memory.append(
            (
                f"tool={state['selected_tool']} | "
                f"args={state['tool_args']} | "
                f"result={state['tool_result']}"
            )
        )

    return {
        **state,
        "memory": memory,
    }


def runtime_monitor(
    state: AgentState,
) -> AgentState:
    """Update runtime risk based on execution behavior."""

    risk_score = state["risk_score"]

    if state["status"] == "tool_error":
        risk_score += 2

    if len(state["memory"]) > 3:
        risk_score += 1

    return {
        **state,
        "risk_score": risk_score,
    }


def generate_answer(
    state: AgentState,
) -> AgentState:
    """Generate the final response."""

    model = create_model()

    prompt = f"""
You are completing an AI agent task.

Goal:
{state["goal"]}

Selected tool:
{state["selected_tool"]}

Tool result:
{state["tool_result"]}

Runtime status:
{state["status"]}

Risk score:
{state["risk_score"]}

Answer the user's goal concisely.

If an action was blocked or failed,
explain that clearly.
"""

    response = model.invoke(prompt)

    return {
        **state,
        "answer": str(response.content),
        "status": "complete",
    }


def build_agent():
    """Build and compile the agent workflow."""

    graph = StateGraph(AgentState)

    graph.add_node(
        "planner",
        planner,
    )

    graph.add_node(
        "security",
        security_check,
    )

    graph.add_node(
        "tool",
        execute_tool,
    )

    graph.add_node(
        "memory",
        update_memory,
    )

    graph.add_node(
        "monitor",
        runtime_monitor,
    )

    graph.add_node(
        "answer",
        generate_answer,
    )

    graph.add_edge(
        START,
        "planner",
    )

    graph.add_edge(
        "planner",
        "security",
    )

    graph.add_conditional_edges(
        "security",
        route_after_security,
        {
            "tool": "tool",
            "answer": "answer",
        },
    )

    graph.add_edge(
        "tool",
        "memory",
    )

    graph.add_edge(
        "memory",
        "monitor",
    )

    graph.add_edge(
        "monitor",
        "answer",
    )

    graph.add_edge(
        "answer",
        END,
    )

    return graph.compile()


def main() -> None:
    """Run the agent workflow."""

    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError(
            "ANTHROPIC_API_KEY was not found."
        )

    agent = build_agent()

    result = agent.invoke(
        {
            #"goal": "Calculate 25 multiplied by 17.",
            "goal": "Explain prompt injection in one sentence.",
            "selected_tool": "",
            "tool_args": {},
            "tool_result": "",
            "memory": [],
            "risk_score": 0,
            "status": "new",
            "answer": "",
        }
    )

    print("\nFinal Agent State:\n")
    print(result)


if __name__ == "__main__":
    main()