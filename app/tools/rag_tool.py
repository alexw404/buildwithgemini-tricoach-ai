"""RAG Retrieval tool for TriCoach AI training docs."""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-01-57b0d8b0ef08"
LOCATION = "us-central1"


def consult_triathlon_manual(query: str) -> str:
    """Consult the grounded triathlon manual and training guide for authoritative answers on endurance training.

    Args:
        query: Specific question about triathlon, training, nutrition, or herbal recovery remedies.

    Returns:
        Relevant retrieved context from the grounded training manual.
    """
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        corpora = list(rag.list_corpora())
        if not corpora:
            return "No active training manual corpus found. Providing general expert endurance guidance."

        corpus_name = corpora[0].name
        results = rag.retrieval_query(
            rag_corpora=[corpus_name],
            text=query,
            similarity_top_k=3,
        )
        if hasattr(results, "contexts") and results.contexts.contexts:
            context_texts = [c.text for c in results.contexts.contexts]
            return "\n\n".join(context_texts)
        return "No specific excerpt found in manual for this query."
    except Exception as e:
        return f"Triathlon manual query note: {str(e)}"
