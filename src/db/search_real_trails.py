from sentence_transformers import SentenceTransformer

from src.db.connection import get_connection


MODEL_NAME = "BAAI/bge-base-en-v1.5"


def search_real_trails(query, top_k=5):

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
                    id,
                    trail_name,
                    distance_km,
                    activities,
                    route_type,
                    route_category,
                    latitude,
                    longitude,

                    embedding <=> %s::vector
                        AS vector_distance,

                    ts_rank(
                        to_tsvector(
                            'english',
                            retrieval_text
                        ),
                        plainto_tsquery(
                            'english',
                            %s
                        )
                    ) AS keyword_score

                FROM real_trails

                WHERE embedding IS NOT NULL

                ORDER BY
                    (
                        0.7 * (
                            1 - (
                                embedding <=> %s::vector
                            )
                        )
                        +
                        0.3 * ts_rank(
                            to_tsvector(
                                'english',
                                retrieval_text
                            ),
                            plainto_tsquery(
                                'english',
                                %s
                            )
                        )
                    ) DESC

                LIMIT %s;
                """,
                (
                    query_embedding.tolist(),
                    query,
                    query_embedding.tolist(),
                    query,
                    top_k
                )
            )

            return cursor.fetchall()


if __name__ == "__main__":

    query = (
        "I want an easy hiking trail "
        "for nature and relaxation."
    )

    results = search_real_trails(query)

    print("\n===== QUERY =====")
    print(query)

    print("\n===== HYBRID RESULTS =====")

    for row in results:

        (
            trail_id,
            trail_name,
            distance_km,
            activities,
            route_type,
            route_category,
            latitude,
            longitude,
            vector_distance,
            keyword_score
        ) = row

        print("\n-----------------------------")
        print("Trail:", trail_name)
        print("Distance:", round(distance_km, 2), "km")
        print("Activities:", activities)
        print("Surface:", route_type)
        print("Category:", route_category)
        print("Location:", latitude, longitude)
        print("Vector distance:", round(vector_distance, 4))
        print("Keyword score:", round(keyword_score, 4))