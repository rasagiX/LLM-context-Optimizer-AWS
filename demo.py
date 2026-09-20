"""
demo.py

End-to-end demonstration of the ML Context Compiler & Token Optimization Suite.

Run from the repository root:
    python demo.py

What this script demonstrates:
    1. Context Pruning & Two-Stage Reranking
    2. Selective Sub-Sentence Token Compression
    3. Semantic Vector Tool Selector
    4. Quantitative ML Quality & Semantic Retention Evaluation
"""

from ml import (
    prune_context,
    prune_context_from_text,
    compress_tokens,
    evaluate_optimization,
)
from app.optimizer import tool_selector


def demo_pre_split_chunks():
    print("=" * 70)
    print("DEMO 1: Context Pruning & Two-Stage Reranking")
    print("=" * 70)

    query = "What are the health risks of long-term ibuprofen use?"

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

    print(f"Query: {query}")
    print(f"Input chunks: {len(context_chunks)} total\n")

    result = prune_context(
        query=query,
        context_chunks=context_chunks,
        top_k=5,
        threshold=0.2,
        use_reranker=True,
    )

    print(f"Retained: {result['retained_count']} / {result['original_count']} chunks")
    print("-" * 70)
    for i, (chunk, score) in enumerate(zip(result["ranked_chunks"], result["scores"]), start=1):
        print(f"  [{i}] Score={score:.4f} | {chunk}")

    print()


def demo_token_compression():
    print("=" * 70)
    print("DEMO 2: Selective Token & Clause Compression")
    print("=" * 70)

    query = "What AWS security and compliance standards are supported?"
    raw_document = (
        "Please note that in order to process payment card data, AWS holds PCI-DSS Level 1 certification, "
        "which is basically the highest level of security standard available. Furthermore, as mentioned above, "
        "AWS also maintains SOC 2 Type II compliance and HIPAA eligibility for healthcare workloads."
    )

    print(f"Original Text:\n  '{raw_document}'\n")

    compressed = compress_tokens(raw_document, query=query)
    print(f"Compressed Text:\n  '{compressed}'\n")

    eval_stats = evaluate_optimization([raw_document], [compressed], query=query)
    print(f"Original Tokens: {eval_stats['original_tokens']}")
    print(f"Retained Tokens: {eval_stats['retained_tokens']}")
    print(f"Tokens Saved:    {eval_stats['removed_tokens']} ({eval_stats['reduction_percent']}%)")
    print(f"Semantic Preservation Score: {eval_stats['semantic_preservation_score']} ({eval_stats['semantic_preservation_percent']}%)")
    print()


def demo_vector_tool_selection():
    print("=" * 70)
    print("DEMO 3: Vector Tool Selection")
    print("=" * 70)

    query = "Check if our cloud infrastructure meets security standards for credit card data."

    tools = [
        {
            "name": "get_compliance_report",
            "description": "Fetch compliance certification reports like PCI-DSS, SOC 2, HIPAA, and ISO 27001 for cloud providers.",
        },
        {
            "name": "compare_pricing",
            "description": "Compare hourly instance costs across AWS, Azure, and Google Cloud.",
        },
        {
            "name": "order_office_supplies",
            "description": "Order stationery, printers, and desks for the office.",
        },
        {
            "name": "send_slack_message",
            "description": "Post an update notification to a Slack channel.",
        },
    ]

    print(f"Query: '{query}'")
    print(f"Available tools: {len(tools)}")

    selected = tool_selector.select(tools, query, top_n=1)
    print(f"\nSelected Tool by ML Vector Router:\n  Name: '{selected[0]['name']}'\n  Description: '{selected[0]['description']}'")
    print()


if __name__ == "__main__":
    demo_pre_split_chunks()
    demo_token_compression()
    demo_vector_tool_selection()

    print("=" * 70)
    print("All ML Token Optimizer Demos Executed Successfully.")
    print("=" * 70)
