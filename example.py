from sentence_transformers import SentenceTransformer
import psycopg2

def _generate_vector(model, text):
    return model.encode(text)

def _generate_and_persist_vector(conn, cursor, model, text):
    embedding = _generate_vector(model, text)
    cursor.execute("INSERT INTO embeddings (text, embedding) VALUES (%s, %s)", (text, embedding.tolist(),))
    conn.commit()

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="testdb",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()

model = SentenceTransformer('all-MiniLM-L6-v2')
_generate_and_persist_vector(conn, cursor, model, "Animals on the forest")
_generate_and_persist_vector(conn, cursor, model, "PC Gaming")
_generate_and_persist_vector(conn, cursor, model, "Animals on the sea")



print("Vectors on embedding:")
cursor.execute("""
    SELECT id, text, embedding
    FROM embeddings
""")

for row in cursor.fetchall():
    print(row)

embedding = _generate_vector(model, "going to swim to the sea")

cursor.execute("""
    SELECT id, text, embedding <-> %s::vector AS distance
    FROM embeddings
    ORDER BY distance ASC
    LIMIT 3
""", (embedding.tolist(),))

for row in cursor.fetchall():
    print(f"ID: {row[0]} | Text: {row[1]} | Distance: {row[2]:.4f}")