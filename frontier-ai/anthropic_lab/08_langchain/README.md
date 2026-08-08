# LangChain Abstraction Study

## Research Question

How does LangChain simplify LLM application development compared with direct use of the Anthropic SDK?

## Comparison

| Direct Anthropic SDK               | LangChain Abstraction  |    |
| ---------------------------------- | ---------------------- | -- |
| `messages.create()`                | `invoke()`             |    |
| Anthropic response object          | `AIMessage`            |    |
| Manual prompt construction         | `ChatPromptTemplate`   |    |
| Manual pipeline orchestration      | LCEL (`                | `) |
| Provider-specific application code | Common model interface |    |

## Execution Flow

```text
User Input
    ↓
ChatPromptTemplate
    ↓
ChatAnthropic
    ↓
Anthropic API
    ↓
Anthropic Response
    ↓
LangChain AIMessage
    ↓
StrOutputParser
    ↓
Python String
```

## Observation

LangChain does not replace the underlying model provider. It introduces an orchestration layer around provider APIs.

The main benefit is separation of concerns: prompt construction, model invocation, response representation, and output parsing can be composed as independent components.

LCEL provides a compact way to connect these components into a reusable pipeline, while execution remains explicit through `invoke()`.

The abstraction reduces provider-specific application code while retaining access to the underlying model.
