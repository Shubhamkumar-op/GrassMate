from sentence_transformers import SentenceTransformer

from src.db.connection import get_connection


MODEL_NAME = "BAAI/bge-base-en-v1.5"


def embed_real_trails():

    print("Loading BGE model on CPU...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, retrieval_text
                FROM real_trails
                WHERE embedding IS NULL
                  AND retrieval_text IS NOT NULL;
            """)

            rows = cursor.fetchall()

            print(f"Trails to embed: {len(rows)}")

            for index, (trail_id, text) in enumerate(rows, start=1):

                embedding = model.encode(
                    text,
                    normalize_embeddings=True
                )

                cursor.execute(
                    """
                    UPDATE real_trails
                    SET embedding = %s
                    WHERE id = %s;
                    """,
                    (
                        embedding.tolist(),
                        trail_id
                    )
                )

                if index % 100 == 0:
                    connection.commit()
                    print(f"Embedded {index}/{len(rows)}")

            connection.commit()

    print("\n✅ Real trail embeddings stored successfully.")


if __name__ == "__main__":
    embed_real_trails()