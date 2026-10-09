from sentence_transformers import SentenceTransformer

from src.db.connection import get_connection


MODEL_NAME = "BAAI/bge-base-en-v1.5"

# Maximum allowed semantic distance.
# Lower distance = stronger match.
MAX_VECTOR_DISTANCE = 0.55


def search_trails(query, top_k=1):
    print("Loading BGE model on CPU...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.id,
                    c.chunk_text,
                    c.bge_embedding <=> %s::vector
                        AS vector_distance,
                    ts_rank(
                        to_tsvector('english', c.chunk_text),
                        plainto_tsquery('english', %s)
                    ) AS keyword_score
                FROM chunks c
                WHERE c.bge_embedding IS NOT NULL
                ORDER BY
                    c.bge_embedding <=> %s::vector ASC
                LIMIT %s;
                """,
                (
                    query_embedding.tolist(),
                    query,
                    query_embedding.tolist(),
                    top_k
                )
            )

            results = cursor.fetchall()

    if not results:
        return []

    best_result = results[0]

    vector_distance = best_result[2]

    if vector_distance > MAX_VECTOR_DISTANCE:
        return []

    return results


if __name__ == "__main__":
    query = "I want to exercise and go jogging."

    results = search_trails(query)

    print("\nSEARCH QUERY:")
    print(query)

    print("\nRESULTS:")

    if not results:
        print("No relevant trails found.")

    for (
        chunk_id,
        chunk_text,
        vector_distance,
        keyword_score
    ) in results:

        print("\n-----------------------------")
        print(f"Chunk ID: {chunk_id}")
        print(f"Vector Distance: {vector_distance:.4f}")
        print(f"Keyword Score: {keyword_score:.4f}")
        print(chunk_text)