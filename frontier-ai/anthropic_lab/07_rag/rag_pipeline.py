"""
Configurable Retrieval-Augmented Generation pipeline.

Supported chunking strategies:
- document: one chunk per file
- word: fixed-size chunks with word overlap
- paragraph: paragraph-aware chunks with paragraph overlap
"""

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
from anthropic import Anthropic
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


ChunkingStrategy = Literal["document", "word", "paragraph"]

DOCUMENTS_DIR = Path(__file__).with_name("documents")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CLAUDE_MODEL = "claude-sonnet-5"

DEFAULT_CHUNK_SIZE = 80
DEFAULT_WORD_OVERLAP = 20
DEFAULT_PARAGRAPH_OVERLAP = 1
DEFAULT_TOP_K = 3
DEFAULT_MIN_SCORE = 0.25


@dataclass
class Chunk:
    """A searchable document chunk."""

    id: str
    source: str
    chunk_number: int
    text: str
    embedding: np.ndarray | None = None


@dataclass
class SearchResult:
    """A retrieved chunk and its similarity score."""

    chunk: Chunk
    score: float


def document_chunking(text: str) -> list[str]:
    """Treat the entire document as one chunk."""

    cleaned_text = text.strip()

    if not cleaned_text:
        return []

    return [cleaned_text]


def word_chunking(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """Split text into fixed-size overlapping word chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "word overlap must be at least zero "
            "and smaller than chunk_size."
        )

    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks


def paragraph_chunking(
    text: str,
    chunk_size: int,
    overlap_paragraphs: int,
) -> list[str]:
    """Split text while preserving paragraph boundaries."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap_paragraphs < 0:
        raise ValueError(
            "paragraph overlap cannot be negative."
        )

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    if not paragraphs:
        return []

    chunks: list[str] = []
    current_paragraphs: list[str] = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_word_count = len(paragraph.split())

        if (
            current_paragraphs
            and current_word_count + paragraph_word_count > chunk_size
        ):
            chunks.append(
                "\n\n".join(current_paragraphs)
            )

            if overlap_paragraphs:
                current_paragraphs = current_paragraphs[
                    -overlap_paragraphs:
                ]

                current_word_count = sum(
                    len(item.split())
                    for item in current_paragraphs
                )
            else:
                current_paragraphs = []
                current_word_count = 0

        current_paragraphs.append(paragraph)
        current_word_count += paragraph_word_count

    if current_paragraphs:
        chunks.append(
            "\n\n".join(current_paragraphs)
        )

    return chunks


def split_document(
    text: str,
    strategy: ChunkingStrategy,
    chunk_size: int,
    word_overlap: int,
    paragraph_overlap: int,
) -> list[str]:
    """Apply the selected chunking strategy."""

    if strategy == "document":
        return document_chunking(text)

    if strategy == "word":
        return word_chunking(
            text=text,
            chunk_size=chunk_size,
            overlap=word_overlap,
        )

    if strategy == "paragraph":
        return paragraph_chunking(
            text=text,
            chunk_size=chunk_size,
            overlap_paragraphs=paragraph_overlap,
        )

    raise ValueError(
        f"Unsupported chunking strategy: {strategy}"
    )


def load_chunks(
    strategy: ChunkingStrategy,
    chunk_size: int,
    word_overlap: int,
    paragraph_overlap: int,
) -> list[Chunk]:
    """Read documents and create chunk records."""

    chunks: list[Chunk] = []

    for file_path in sorted(
        DOCUMENTS_DIR.glob("*.txt")
    ):
        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        document_chunks = split_document(
            text=text,
            strategy=strategy,
            chunk_size=chunk_size,
            word_overlap=word_overlap,
            paragraph_overlap=paragraph_overlap,
        )

        print(
            f"{file_path.name}: "
            f"{len(document_chunks)} chunk(s)"
        )

        for chunk_number, chunk_text in enumerate(
            document_chunks,
            start=1,
        ):
            chunks.append(
                Chunk(
                    id=(
                        f"{file_path.stem}_"
                        f"{chunk_number}"
                    ),
                    source=file_path.name,
                    chunk_number=chunk_number,
                    text=chunk_text,
                )
            )

    if not chunks:
        raise ValueError(
            f"No text documents were found in "
            f"{DOCUMENTS_DIR}."
        )

    return chunks


def create_embeddings(
    chunks: list[Chunk],
    model: SentenceTransformer,
) -> None:
    """Generate one embedding for every chunk."""

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    for chunk, embedding in zip(
        chunks,
        embeddings,
        strict=True,
    ):
        chunk.embedding = np.asarray(
            embedding,
            dtype=np.float32,
        )


def cosine_similarity(
    vector_a: np.ndarray,
    vector_b: np.ndarray,
) -> float:
    """Calculate cosine similarity."""

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(vector_a, vector_b)
        / denominator
    )


def search(
    question: str,
    chunks: list[Chunk],
    model: SentenceTransformer,
    top_k: int,
    min_score: float,
) -> list[SearchResult]:
    """Retrieve the most relevant chunks."""

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    question_embedding = np.asarray(
        model.encode(
            question,
            normalize_embeddings=True,
        ),
        dtype=np.float32,
    )

    results: list[SearchResult] = []

    for chunk in chunks:
        if chunk.embedding is None:
            raise ValueError(
                f"Chunk {chunk.id} has no embedding."
            )

        score = cosine_similarity(
            question_embedding,
            chunk.embedding,
        )

        if score >= min_score:
            results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                )
            )

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return results[:top_k]


def build_context(
    results: list[SearchResult],
) -> str:
    """Build the context supplied to Claude."""

    context_parts: list[str] = []

    for result in results:
        context_parts.append(
            f"Source file: {result.chunk.source}\n"
            f"Chunk number: "
            f"{result.chunk.chunk_number}\n"
            f"Similarity score: "
            f"{result.score:.4f}\n"
            f"Content:\n"
            f"{result.chunk.text}"
        )

    return "\n\n---\n\n".join(
        context_parts
    )


def extract_text(response: Any) -> str:
    """Extract text blocks from an Anthropic response."""

    text_parts: list[str] = []

    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts)


def answer_question(
    question: str,
    results: list[SearchResult],
) -> str:
    """Generate a grounded answer using Claude."""

    if not results:
        return (
            "The available documents do not provide "
            "enough information."
        )

    api_key = os.getenv(
        "ANTHROPIC_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY was not found."
        )

    context = build_context(results)

    client = Anthropic(
        api_key=api_key
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=(
            "Answer the question using only the "
            "provided context. Do not invent "
            "information. If the context does not "
            "contain the answer, state that the "
            "available documents do not provide "
            "enough information."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Context:\n\n"
                    f"{context}\n\n"
                    f"Question:\n"
                    f"{question}"
                ),
            }
        ],
    )

    return extract_text(response)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the configurable RAG pipeline."
        )
    )

    parser.add_argument(
        "--chunking",
        choices=[
            "document",
            "word",
            "paragraph",
        ],
        default="paragraph",
        help="Chunking strategy to use.",
    )

    parser.add_argument(
        "--question",
        required=True,
        help="Question to answer.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=(
            "Approximate maximum words "
            "per chunk."
        ),
    )

    parser.add_argument(
        "--word-overlap",
        type=int,
        default=DEFAULT_WORD_OVERLAP,
        help=(
            "Overlapping words for "
            "word-based chunking."
        ),
    )

    parser.add_argument(
        "--paragraph-overlap",
        type=int,
        default=DEFAULT_PARAGRAPH_OVERLAP,
        help=(
            "Overlapping paragraphs for "
            "paragraph chunking."
        ),
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=(
            "Maximum number of retrieved chunks."
        ),
    )

    parser.add_argument(
        "--min-score",
        type=float,
        default=DEFAULT_MIN_SCORE,
        help=(
            "Minimum cosine-similarity score."
        ),
    )

    return parser.parse_args()


def main() -> None:
    """Run indexing, retrieval, and generation."""

    load_dotenv()

    args = parse_arguments()

    print("\nChunking strategy:")
    print(args.chunking)

    print("\nLoading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("\nPreparing documents...")

    chunks = load_chunks(
        strategy=args.chunking,
        chunk_size=args.chunk_size,
        word_overlap=args.word_overlap,
        paragraph_overlap=(
            args.paragraph_overlap
        ),
    )

    print(
        f"\nCreating embeddings for "
        f"{len(chunks)} chunk(s)..."
    )

    create_embeddings(
        chunks=chunks,
        model=embedding_model,
    )

    print("\nQuestion:")
    print(args.question)

    results = search(
        question=args.question,
        chunks=chunks,
        model=embedding_model,
        top_k=args.top_k,
        min_score=args.min_score,
    )

    print("\nRetrieved chunks:")

    if not results:
        print("- None")

    for result in results:
        print(
            f"- {result.chunk.source} "
            f"chunk "
            f"{result.chunk.chunk_number} "
            f"(score: {result.score:.4f})"
        )

    answer = answer_question(
        question=args.question,
        results=results,
    )

    print("\nClaude's answer:")
    print(answer)


if __name__ == "__main__":
    main()