from typing import List, Tuple, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, literal
from app.models.transcript_chunk import TranscriptChunk
from app.models.episode import Episode
from app.ai.factory import AIProviderFactory
from app.schemas.session import CitationItem

SIMILARITY_THRESHOLD = 0.35  # Minimum cosine similarity (1 - distance) required for grounding

async def retrieve_context(
    query: str,
    db: AsyncSession,
    top_k: int = 6,
    embedding_provider_name: str | None = None,
    source_ids: List[UUID] | None = None,
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
    if source_ids:
        stmt = stmt.where(TranscriptChunk.episode_id.in_(source_ids))

    result = await db.execute(stmt)
    rows = result.all()

    # Add lexical candidates so exact names, uploaded-document terms, and
    # distinctive phrases are not lost when embedding similarity is broad.
    terms = [term for term in query.split() if len(term) >= 5][:8]
    if terms:
        lexical_stmt = (
            select(TranscriptChunk, Episode, literal(0.36).label("similarity"))
            .join(Episode, TranscriptChunk.episode_id == Episode.id)
            .where(or_(*(TranscriptChunk.chunk_text.ilike(f"%{term}%") for term in terms)))
            .limit(top_k * 2)
        )
        if source_ids:
            lexical_stmt = lexical_stmt.where(TranscriptChunk.episode_id.in_(source_ids))
        lexical_result = await db.execute(lexical_stmt)
        rows.extend(lexical_result.all())

    if not rows:
        return "", [], False

    # Avoid repeated chunks from legacy ingestions or near-identical summaries.
    unique_rows = []
    seen = set()
    for row in rows:
        chunk, episode, _ = row
        key = (str(episode.id), chunk.chunk_index, chunk.chunk_text[:180])
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(row)
        if len(unique_rows) >= top_k:
            break
    rows = unique_rows

    top_similarity = rows[0][2]
    is_grounded = top_similarity >= SIMILARITY_THRESHOLD

    citations: List[CitationItem] = []
    cited_episode_ids = set()
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
        if str(episode.id) not in cited_episode_ids:
            citations.append(citation)
            cited_episode_ids.add(str(episode.id))

        block = (
            f"--- SOURCE: {episode.guest_name} on \"{episode.title}\" "
            f"(Timestamp: {chunk.timestamp_start or 'N/A'}) ---\n"
            f"{chunk.chunk_text}\n"
        )
        context_blocks.append(block)

    formatted_context = "\n".join(context_blocks)
    return formatted_context, citations, is_grounded
