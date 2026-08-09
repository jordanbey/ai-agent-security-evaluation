from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    task: str
    step: int
    requires_tool: bool
    tool_result: str
    status: str


def analyze_task(state: GraphState) -> GraphState:
    """Inspect the task and decide whether a tool is needed."""

    requires_tool = "calculate" in state["task"].lower()

    return {
        **state,
        "requires_tool": requires_tool,
        "status": "analyzed",
    }


def route_task(
    state: GraphState,
) -> Literal["tool", "review"]:
    """Route execution based on the current state."""

    if state["requires_tool"]:
        return "tool"

    return "review"


def tool_node(state: GraphState) -> GraphState:
    """Simulate external tool execution."""

    return {
        **state,
        "tool_result": "42",
        "step": state["step"] + 1,
        "status": "tool_executed",
    }


def review_node(state: GraphState) -> GraphState:
    """Review the current state."""

    return {
        **state,
        "step": state["step"] + 1,
        "status": "reviewed",
    }


def should_continue(
    state: GraphState,
) -> Literal["continue", "end"]:
    """Allow one additional review cycle."""

    if state["step"] < 2:
        return "continue"

    return "end"


def build_workflow():
    """Build and compile the stateful workflow."""

    graph = StateGraph(GraphState)

    graph.add_node(
        "analyze",
        analyze_task,
    )

    graph.add_node(
        "tool",
        tool_node,
    )

    graph.add_node(
        "review",
        review_node,
    )

    graph.add_edge(
        START,
        "analyze",
    )

    graph.add_conditional_edges(
        "analyze",
        route_task,
        {
            "tool": "tool",
            "review": "review",
        },
    )

    graph.add_edge(
        "tool",
        "review",
    )

    graph.add_conditional_edges(
        "review",
        should_continue,
        {
            "continue": "review",
            "end": END,
        },
    )

    return graph.compile()


def main() -> None:
    """Run the stateful workflow."""

    app = build_workflow()

    result = app.invoke(
        {
            "task": "Calculate the requested value.",
            "step": 0,
            "requires_tool": False,
            "tool_result": "",
            "status": "new",
        }
    )

    print("\nFinal state:\n")
    print(result)


if __name__ == "__main__":
    main()