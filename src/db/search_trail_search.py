from sentence_transformers import SentenceTransformer
from src.db.connection import get_connection

MODEL_NAME = "BAAI/bge-base-en-v1.5"


def search_trails(query, limit=5):
    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    trail_name,
                    latitude,
                    longitude,
                    distance_km,
                    activities,
                    route_type,
                    route_category,
                    retrieval_text,
                    embedding <=> %s::vector AS distance
                FROM trail_search
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (
                query_embedding,
                query_embedding,
                limit
            ))

            return cursor.fetchall()


if __name__ == "__main__":

    query = "I want a peaceful hiking trail for nature and relaxation."

    results = search_trails(query)

    print("\n🔎 Query:", query)
    print("\nTop trails:\n")

    for i, result in enumerate(results, start=1):
        (
            name,
            lat,
            lon,
            distance,
            activities,
            route_type,
            category,
            retrieval_text,
            score
        ) = result

        print(f"{i}. {name}")
        print(f"   Distance: {distance:.4f}")
        print(f"   Trail length: {distance:.2f} km")
        print(f"   Activities: {activities}")
        print(f"   Surface: {route_type}")
        print(f"   Category: {category}")
        print(f"   Location: {lat:.5f}, {lon:.5f}")
        print()