# Module 7 — Retrieval-Augmented Generation: Chunking and Retrieval Behavior

## Overview

This module implements a Retrieval-Augmented Generation (RAG) pipeline from first principles to study how document chunking affects semantic retrieval and grounded LLM responses.

The pipeline supports:

* Document-level retrieval
* Fixed-size word chunking with overlap
* Paragraph-aware chunking
* Sentence embeddings
* Cosine similarity search
* Top-k retrieval
* Similarity threshold filtering
* Grounded response generation using Claude

The embedding model used is:

`sentence-transformers/all-MiniLM-L6-v2`

---

## Architecture

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Semantic Search
    ↓
Similarity Filtering
    ↓
Top-k Chunks
    ↓
Context Construction
    ↓
Claude
    ↓
Grounded Answer
```

---

## Research Question

How does chunking strategy affect the completeness of retrieved information?

The main comparison focuses on fixed-size word chunking and paragraph-aware chunking.

---

## Chunking Strategies

### Document-Level

The entire document is treated as one chunk and represented by one embedding.

This provides a simple baseline but may combine multiple topics into a single representation.

### Fixed-Size Word Chunking

Documents are divided into fixed-size word chunks with configurable overlap.

Example:

```text
chunk_size = 16
word_overlap = 5
```

Overlap helps preserve information near chunk boundaries, but related facts can still be separated when they extend beyond the overlap window.

### Paragraph-Aware Chunking

Paragraph-aware chunking keeps complete paragraphs together instead of forcing every chunk to end at a fixed word count.

This preserves logically related information that belongs within the same paragraph.

---

## Controlled Experiment

The synthetic document `vacation_tiers.txt` contains two related policy rules:

* Employees with at least five years of continuous service receive **25 vacation days per year**.
* Employees with fewer than five years of continuous service receive **15 vacation days per year**.

The evaluation question was:

> How many vacation days do employees with at least five years receive, and how many do employees with fewer than five years receive?

To isolate the effect of chunk boundaries, the experiment used:

```text
top_k = 1
```

---

## Experimental Results

### 1. Document-Level Chunking

**Command**

```bash
python 07_rag/rag_pipeline.py \
    --chunking document \
    --question "How many vacation days do employees with at least five years receive, and how many do employees with fewer than five years receive?"
```

**Claude's Answer**

```text
- Employees with at least five years of continuous service receive 25 vacation days per year.
- Employees with fewer than five years of continuous service receive 15 vacation days per year.
```

---

### 2. Fixed-Size Word Chunking

**Command**

```bash
python 07_rag/rag_pipeline.py \
    --chunking word \
    --chunk-size 16 \
    --word-overlap 5 \
    --top-k 1 \
    --question "How many vacation days do employees with at least five years receive, and how many do employees with fewer than five years receive?"
```

**Claude's Answer**

```text
Based on the provided context, employees with at least five years of continuous service receive 25 vacation days per year.

However, the document does not provide the specific number of vacation days for employees with fewer than five years of continuous service because that portion of the policy was not included in the retrieved chunk.
```

---

### 3. Paragraph-Aware Chunking

**Command**

```bash
python 07_rag/rag_pipeline.py \
    --chunking paragraph \
    --chunk-size 16 \
    --paragraph-overlap 0 \
    --top-k 1 \
    --question "How many vacation days do employees with at least five years receive, and how many do employees with fewer than five years receive?"
```

**Claude's Answer**

```text
- Employees with at least five years of continuous service receive 25 vacation days per year.
- Employees with fewer than five years of continuous service receive 15 vacation days per year.
```

---

## Observation

In this experiment, document-level retrieval and paragraph-aware chunking both returned the complete policy.

Fixed-size word chunking, even with a 5-word overlap, split the policy across chunk boundaries. With `top_k=1`, only one chunk was retrieved, so Claude answered the first part correctly and reported that the second value was not available in the retrieved context.

This experiment shows that overlap reduces boundary fragmentation but does not always preserve complete semantic context when related information extends beyond the overlap window.

---

## Grounding

Claude is instructed to answer only from the retrieved context.

When the retrieved chunk does not contain enough information, the model reports that the information is unavailable instead of generating an unsupported answer.

This separates two responsibilities:

```text
Retrieval decides what information reaches the model.

Generation decides how the model uses that information.
```

---

## Key Takeaway

RAG quality depends not only on the language model or embedding model, but also on how documents are chunked before retrieval.

In this experiment, paragraph-aware chunking preserved a complete policy that fixed-size word chunking split across multiple chunks, allowing the model to produce a complete grounded answer under the same retrieval settings.
