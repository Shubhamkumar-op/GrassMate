from sentence_transformers import SentenceTransformer
from src.db.connection import get_connection

MODEL_NAME = "BAAI/bge-base-en-v1.5"


def embed_trail_search():
    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, retrieval_text
                FROM trail_search
                WHERE embedding IS NULL
                ORDER BY id;
            """)

            rows = cursor.fetchall()

            print(f"Found {len(rows)} records to embed.")

            for count, (trail_id, text) in enumerate(rows, start=1):

                embedding = model.encode(
                    text,
                    normalize_embeddings=True
                ).tolist()

                cursor.execute("""
                    UPDATE trail_search
                    SET embedding = %s
                    WHERE id = %s;
                """, (embedding, trail_id))

                if count % 100 == 0:
                    connection.commit()
                    print(f"Embedded {count}/{len(rows)}")

            connection.commit()

    print("✅ trail_search embeddings completed.")


if __name__ == "__main__":
    embed_trail_search()