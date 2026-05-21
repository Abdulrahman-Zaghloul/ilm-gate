
import psycopg2
import urllib.request
import json
import os
from dotenv import load_dotenv

# Initialize and parse the local configuration file
load_dotenv()

DB_CONFIG = {
    "dbname": "ilm_gate_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

def get_query_embedding(query):
    url = "http://localhost:11434/api/embeddings"
    payload = json.dumps({"model": "nomic-embed-text", "prompt": query}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))["embedding"]

def retrieve_context(query, limit=3):
    query_vector = get_query_embedding(query)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Cosine distance operator (<=>) finds the mathematically closest vectors
    cursor.execute("""
        SELECT s.name, v.verse_number, v.english_translation 
        FROM verses v
        JOIN surahs s ON v.surah_id = s.id
        ORDER BY v.embedding <=> %s::vector
        LIMIT %s;
    """, (query_vector, limit))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def ask_llm(query, context):
    url = "http://localhost:11434/api/chat"
    
    context_str = "\n".join([f"- Surah {r[0]} ({r[1]}): {r[2]}" for r in context])
    
    prompt = f"""You are a precise, objective text assistant. Answer the User Query using ONLY the provided Source Context below. If the text does not contain the answer, state that clearly.

Source Context:
{context_str}

User Query: {query}"""

    payload = json.dumps({
        "model": "phi4-mini",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))["message"]["content"]

if __name__ == "__main__":
    print("\n🌟 Ilm-Gate Local AI Core Online 🌟")
    print("Ask a complex question or type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
            
        print("\nSearching database matches...")
        context = retrieve_context(user_input)
        
        print("Synthesizing grounded answer...")
        answer = ask_llm(user_input, context)
        
        print(f"\nAI Assistant:\n{answer}\n")
        print("-" * 50 + "\n")