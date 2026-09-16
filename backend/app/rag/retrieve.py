from typing import List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transcript_chunk import TranscriptChunk
from app.models.episode import Episode
from app.ai.factory import AIProviderFactory
from app.schemas.session import CitationItem

SIMILARITY_THRESHOLD = 0.35  # Minimum cosine similarity (1 - distance) required for grounding

async def retrieve_context(
    query: str,
    db: AsyncSession,
    top_k: int = 6,
    embedding_provider_name: str | None = None
) -> Tuple[str, List[CitationItem], bool]:
    """
    Retrieves the most relevant transcript chunks using pgvector cosine distance.
    Returns:
      - formatted_context_str: string formatted for the system prompt
      - citations: list of structured CitationItem objects
      - is_grounded: boolean flag indicating if top results meet the confidence threshold
    """
    embedder = AIProviderFactory.get_embedding_provider(provider=embedding_provider_name)
    try:
        query_embeddings = await embedder.embed([query])
    except Exception as e:
        import logging
        logging.getLogger("lenny_assistant").warning(f"Embedding failed: {e}. Degrading gracefully.")
        query_embeddings = None

    if not query_embeddings:
        return "", [], False

    query_vector = query_embeddings[0]

    # Query pgvector cosine distance
    emb_col: Any = TranscriptChunk.embedding
    distance_expr = emb_col.cosine_distance(query_vector)
    stmt = (
        select(
            TranscriptChunk,
            Episode,
            (1.0 - distance_expr).label("similarity")
        )
        .join(Episode, TranscriptChunk.episode_id == Episode.id)
        .order_by(distance_expr)
        .limit(top_k)
    )

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return "", [], False

    top_similarity = rows[0][2]
    is_grounded = top_similarity >= SIMILARITY_THRESHOLD

    citations: List[CitationItem] = []
    context_blocks: List[str] = []

    for chunk, episode, sim in rows:
        # Extract a short representative quote snippet
        quote_sample = chunk.chunk_text[:280].replace("\n", " ").strip() + "..."
        citation = CitationItem(
            episode_id=str(episode.id),
            episode_title=episode.title,
            guest_name=episode.guest_name,
            chapter_title=chunk.chapter_title or "Transcript Excerpt",
            timestamp=chunk.timestamp_start or "",
            quote=quote_sample,
            similarity_score=round(float(sim), 4)
        )
        citations.append(citation)

        block = (
            f"--- SOURCE: {episode.guest_name} on \"{episode.title}\" "
            f"(Timestamp: {chunk.timestamp_start or 'N/A'}) ---\n"
            f"{chunk.chunk_text}\n"
        )
        context_blocks.append(block)

    formatted_context = "\n".join(context_blocks)
    return formatted_context, citations, is_grounded
