"""
demo.py

End-to-end demonstration of the ML context-pruning pipeline.

Run from the repository root:
    python demo.py

What this script does:
    1. Defines a realistic sample query and a mixed bag of context chunks
       (some relevant, some not)
    2. Runs the pruning pipeline
    3. Prints a clear before/after comparison showing which chunks were kept
       and their relevance scores

No API keys, no internet connection, no AWS account needed.
The embedding model (all-MiniLM-L6-v2) downloads automatically on first run
(~90 MB, cached locally after that).
"""

from ml.pruner import prune_context, prune_context_from_text


# ---------------------------------------------------------------------------
# Demo 1: pre-split chunks
# ---------------------------------------------------------------------------

def demo_pre_split_chunks():
    print("=" * 60)
    print("DEMO 1: Pre-split context chunks")
    print("=" * 60)

    query = "What are the health risks of long-term ibuprofen use?"

    # Mix of relevant and irrelevant chunks — the pruner should surface the right ones
    context_chunks = [
        "Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) used to relieve pain.",
        "Long-term use of ibuprofen can lead to gastrointestinal bleeding and ulcers.",
        "The Eiffel Tower is located in Paris, France.",
        "Chronic NSAID use is associated with increased risk of cardiovascular events.",
        "Photosynthesis is the process by which plants convert sunlight into food.",
        "Kidney damage is a known complication of prolonged ibuprofen consumption.",
        "Python is a popular programming language used in data science.",
        "Patients with existing heart conditions should avoid regular ibuprofen use.",
        "The Great Wall of China stretches over 13,000 miles.",
        "Ibuprofen should not be taken on an empty stomach to reduce gastric irritation.",
    ]

    print(f"\nQuery:\n  {query}\n")
    print(f"Input chunks: {len(context_chunks)} total\n")

    result = prune_context(
        query=query,
        context_chunks=context_chunks,
        top_k=5,
        threshold=0.2,
    )

    print(f"Retained: {result['retained_count']} / {result['original_count']} chunks\n")
    print("Ranked results (best match first):")
    print("-" * 60)
    for i, (chunk, score) in enumerate(
        zip(result["ranked_chunks"], result["scores"]), start=1
    ):
        print(f"  [{i}] score={score:.4f}  |  {chunk}")

    print()


# ---------------------------------------------------------------------------
# Demo 2: raw text input (chunking handled automatically)
# ---------------------------------------------------------------------------

def demo_raw_text():
    print("=" * 60)
    print("DEMO 2: Raw text input (auto-chunked by sentence)")
    print("=" * 60)

    query = "How do vaccines protect against infectious diseases?"

    raw_text = """
    Vaccines work by training the immune system to recognize and fight specific pathogens.
    They contain weakened or inactivated forms of a virus or bacteria, or just key proteins from them.
    The stock market experienced significant volatility last quarter due to inflation concerns.
    When a vaccinated person encounters the real pathogen, their immune system can respond quickly.
    Herd immunity occurs when a large portion of a community becomes immune to a disease.
    The best recipe for chocolate chip cookies includes butter, sugar, and vanilla extract.
    Some vaccines require multiple doses to build full immunity over time.
    Climate change is causing shifts in global weather patterns and sea levels.
    mRNA vaccines, like those developed for COVID-19, teach cells to produce a harmless protein that triggers an immune response.
    """

    print(f"\nQuery:\n  {query}\n")

    result = prune_context_from_text(
        query=query,
        raw_text=raw_text,
        chunking_strategy="sentence",
        top_k=4,
        threshold=0.2,
    )

    print(f"Chunks after splitting: {result['original_count']}")
    print(f"Retained: {result['retained_count']} / {result['original_count']} chunks\n")
    print("Ranked results (best match first):")
    print("-" * 60)
    for i, (chunk, score) in enumerate(
        zip(result["ranked_chunks"], result["scores"]), start=1
    ):
        print(f"  [{i}] score={score:.4f}  |  {chunk}")

    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_pre_split_chunks()
    demo_raw_text()

    print("=" * 60)
    print("Demo complete.")
    print("This is the interface your backend will call:")
    print("  from ml.pruner import prune_context")
    print("  result = prune_context(query, chunks, top_k, threshold)")
    print("=" * 60)
