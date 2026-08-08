"""
Module 8 - LangChain LLM Pipeline

A compact example of LangChain orchestration using:
- ChatAnthropic
- ChatPromptTemplate
- StrOutputParser
- LCEL composition
"""

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


MODEL_NAME = "claude-sonnet-5"


def create_model() -> ChatAnthropic:
    """Create the Claude chat model through LangChain."""

    return ChatAnthropic(
        model=MODEL_NAME,
    )


def build_chain():
    """Build a reusable LangChain pipeline."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an AI engineering assistant. "
                "Provide concise and technically accurate answers.",
            ),
            (
                "human",
                "Analyze the following topic:\n\n{topic}",
            ),
        ]
    )

    model = create_model()
    parser = StrOutputParser()

    return prompt | model | parser


def run_analysis(
    topic: str,
) -> str:
    """Run the reusable LLM pipeline."""

    chain = build_chain()

    return chain.invoke(
        {
            "topic": topic,
        }
    )


def main() -> None:
    """Run the example pipeline."""

    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError(
            "ANTHROPIC_API_KEY was not found."
        )

    topic = (
        "Explain why prompt injection is a security concern "
        "for AI agents that can call external tools."
    )

    answer = run_analysis(topic)

    print("\nTopic:\n")
    print(topic)

    print("\nAnalysis:\n")
    print(answer)


if __name__ == "__main__":
    main()