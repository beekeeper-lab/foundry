# LLM Operations, RAG & Prompt Engineering

Guidelines for integrating large language models into production systems, building
retrieval-augmented generation pipelines, and managing prompts as versioned artifacts.

---

## LLM Integration Patterns

### Provider Abstraction

Wrap LLM calls behind a provider-agnostic interface. Switching providers should
require only a configuration change, not code changes.

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Send a completion request to the LLM."""

    @abstractmethod
    def complete_structured(self, prompt: str, schema: type, **kwargs) -> LLMResponse:
        """Request structured output conforming to a Pydantic schema."""


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: str | None = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        import time
        start = time.monotonic()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}],
        )
        latency = (time.monotonic() - start) * 1000
        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency,
        )
```

### Structured Output

Always use structured output parsers for LLM responses that feed into downstream logic:

```python
from pydantic import BaseModel, Field


class SentimentResult(BaseModel):
    sentiment: str = Field(description="One of: positive, negative, neutral")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of the classification")


# Use the LLM provider with structured output
result = provider.complete_structured(
    prompt=f"Classify the sentiment of this review: {review_text}",
    schema=SentimentResult,
)
```

### Error Handling & Resilience

```python
import time
from functools import wraps


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Retry LLM calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, ServiceUnavailableError) as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

Key resilience patterns:
- **Retry with backoff** for transient errors (rate limits, 5xx responses).
- **Timeout limits** appropriate to the use case (2s for interactive, 30s for batch).
- **Fallback models** — if the primary model is unavailable, fall back to a secondary.
- **Circuit breaker** — stop calling a failing provider after N consecutive errors.
- **Request budgets** — cap daily token usage per service to prevent cost overruns.

---

## RAG (Retrieval-Augmented Generation)

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  User Query  │────▶│  Retriever    │────▶│  Reranker    │
└─────────────┘     │  (vector DB)  │     │  (optional)  │
                    └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐     ┌──────▼──────┐
                    │  LLM Response │◀────│  Generator   │
                    │  + Citations  │     │  (LLM call)  │
                    └──────────────┘     └─────────────┘
```

### Document Ingestion Pipeline

```python
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    chunk_size: int = 512       # tokens per chunk
    chunk_overlap: int = 64     # overlapping tokens between chunks
    min_chunk_size: int = 100   # discard chunks smaller than this


def ingest_documents(documents: list[str], config: ChunkConfig) -> list[dict]:
    """Chunk, embed, and index documents for RAG retrieval."""
    chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc, config)
        for chunk in doc_chunks:
            embedding = embed(chunk.text)
            chunks.append({
                "text": chunk.text,
                "embedding": embedding,
                "metadata": {
                    "source": chunk.source,
                    "page": chunk.page,
                    "chunk_index": chunk.index,
                },
            })
    vector_store.upsert(chunks)
    return chunks
```

### Chunking Strategies

| Strategy | When to Use | Trade-offs |
|----------|-------------|------------|
| **Fixed-size** (token count) | General-purpose text | Simple but may split mid-sentence |
| **Recursive character** | Structured documents | Respects paragraph/section boundaries |
| **Semantic** (embedding-based) | Dense technical content | Better coherence but slower ingestion |
| **Document-structure-aware** | HTML, Markdown, PDF | Preserves headings and tables as units |
| **Parent-child** | Long documents needing context | Retrieve child, pass parent to LLM for context |

### Retrieval Quality

Measure retrieval before tuning generation:

```python
def evaluate_retrieval(test_set: list[dict], retriever, k: int = 5) -> dict:
    """Evaluate retrieval quality on a labeled test set."""
    hits_at_k = 0
    mrr_sum = 0.0

    for item in test_set:
        results = retriever.search(item["query"], top_k=k)
        result_ids = [r.id for r in results]

        if item["relevant_doc_id"] in result_ids:
            hits_at_k += 1
            rank = result_ids.index(item["relevant_doc_id"]) + 1
            mrr_sum += 1.0 / rank

    n = len(test_set)
    return {
        "recall_at_k": hits_at_k / n,
        "mrr": mrr_sum / n,
    }
```

Key metrics:
- **Recall@k** — fraction of queries where the relevant document is in the top-k results.
- **MRR** (Mean Reciprocal Rank) — average of 1/rank for the first relevant result.
- **Answer accuracy** — end-to-end: does the generated answer match the ground truth?

---

## Prompt Engineering

### Prompt Templates

Store prompts as versioned template files, not inline strings:

```
prompts/
├── v1/
│   ├── summarize.md
│   ├── classify-sentiment.md
│   └── extract-entities.md
├── v2/
│   ├── summarize.md       # Updated with few-shot examples
│   └── classify-sentiment.md
└── evaluation/
    ├── summarize-eval.jsonl
    └── classify-eval.jsonl
```

```python
from pathlib import Path
from jinja2 import Template


def load_prompt(name: str, version: str = "v1", **kwargs) -> str:
    """Load and render a versioned prompt template."""
    path = Path("prompts") / version / f"{name}.md"
    template = Template(path.read_text())
    return template.render(**kwargs)


# Usage
prompt = load_prompt(
    "classify-sentiment",
    version="v2",
    review_text=user_input,
    categories=["positive", "negative", "neutral"],
)
```

### Prompt Design Principles

- **Be specific.** State the exact output format, constraints, and edge-case handling.
- **Provide examples.** Few-shot examples in the prompt improve consistency more than longer instructions.
- **Separate instructions from data.** Use clear delimiters (XML tags, triple backticks) between the task description and the input data.
- **Constrain output.** Request structured output (JSON, specific fields) rather than free-form text when the result feeds into code.
- **Test on edge cases.** Include adversarial, ambiguous, and boundary inputs in the evaluation set.

### Prompt Evaluation

```python
import json


def evaluate_prompts(
    prompt_versions: list[str],
    eval_set_path: str,
    provider: LLMProvider,
) -> dict:
    """Compare prompt versions against an evaluation dataset."""
    eval_data = [json.loads(line) for line in open(eval_set_path)]
    results = {}

    for version in prompt_versions:
        correct = 0
        for item in eval_data:
            prompt = load_prompt("classify-sentiment", version=version, **item["inputs"])
            response = provider.complete(prompt)
            if response.content.strip() == item["expected"]:
                correct += 1
        results[version] = correct / len(eval_data)

    return results  # e.g., {"v1": 0.82, "v2": 0.91}
```

---

## LLM Observability

### What to Log

Every LLM call must capture:

| Field | Purpose |
|-------|---------|
| `request_id` | Correlate logs across services |
| `prompt_template` | Which template and version was used |
| `prompt_variables` | Input variables (PII-redacted) |
| `model` | Model identifier and version |
| `input_tokens` | Cost tracking and optimization |
| `output_tokens` | Cost tracking and optimization |
| `latency_ms` | Performance monitoring |
| `response` | Raw response (PII-redacted) for debugging |
| `status` | Success, error, timeout, rate-limited |

### PII Redaction

```python
import re

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


def redact_pii(text: str) -> str:
    """Remove PII before logging or sending to external LLM APIs."""
    for pii_type, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[REDACTED_{pii_type.upper()}]", text)
    return text
```

### Cost Tracking

```python
MODEL_COSTS = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},  # per 1M tokens
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for an LLM call in USD."""
    rates = MODEL_COSTS.get(model, {"input": 0, "output": 0})
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
```
