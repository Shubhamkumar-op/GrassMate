from sentence_transformers import SentenceTransformer


model = SentenceTransformer("BAAI/bge-base-en-v1.5")

text = "A flat trail around a lake with trees and birdwatching opportunities."

embedding = model.encode(text)

print("Embedding created successfully.")
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])