
import psycopg2
import urllib.request
import json
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Initialize and parse the local configuration file
load_dotenv()

DB_CONFIG = {
    "dbname": "ilm_gate_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

def get_embedding(text):
    """Calls local Ollama API to get a 768-dimension vector"""
    url = "http://localhost:11434/api/embeddings"
    payload = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data["embedding"]

def populate_vectors():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Alter table to add a vector column matching nomic's 768 dimensions
    logging.info("[AI Pipeline] Adding vector column to schema...")
    cursor.execute("ALTER TABLE verses ADD COLUMN IF NOT EXISTS embedding vector(768);")
    conn.commit()
    
    # 2. Fetch all verses that don't have embeddings computed yet
    cursor.execute("SELECT id, english_translation FROM verses WHERE embedding IS NULL;")
    rows = cursor.fetchall()
    
    logging.info(f"[AI Pipeline] Generating embeddings for {len(rows)} verses. This may take a minute...")
    
    for v_id, text in rows:
        try:
            vector = get_embedding(text)
            cursor.execute("UPDATE verses SET embedding = %s WHERE id = %s;", (vector, v_id))
        except Exception as e:
            logging.error(f"Failed on verse ID {v_id}: {e}")
            continue
            
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("[AI Pipeline] Database vectors successfully generated!")

if __name__ == "__main__":
    populate_vectors()