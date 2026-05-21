
import os
import json
import logging
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Initialize and parse the local configuration file
load_dotenv()

# Database configuration - Update these with your local Postgres credentials
DB_CONFIG = {
    "dbname": "ilm_gate_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

def load_silver_to_postgres():
    input_path = "data/silver/quran_silver.json"
    
    if not os.path.exists(input_path):
        logging.error(f"[Postgres Load] Source file not found: {input_path}")
        return

    logging.info("[Postgres Load] Connecting to PostgreSQL cluster...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Create Schema Structures
        logging.info("[Postgres Load] Initializing relational table schemas...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS surahs (
                id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                transliteration VARCHAR(100)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verses (
                id SERIAL PRIMARY KEY,
                surah_id INT REFERENCES surahs(id) ON DELETE CASCADE,
                verse_number INT NOT NULL,
                arabic_text TEXT NOT NULL,
                english_translation TEXT NOT NULL,
                UNIQUE (surah_id, verse_number)
            );
        """)
        
        # 2. Extract and Load Data
        with open(input_path, 'r', encoding='utf-8') as f:
            silver_data = json.load(f)
            
        logging.info("[Postgres Load] Transforming and parsing source array...")
        
        # We use sets to track distinct Surahs to seed our dimension table first
        distinct_surahs = {}
        verses_to_insert = []
        
        for row in silver_data:
            s_id = row["surah_id"]
            if s_id not in distinct_surahs:
                distinct_surahs[s_id] = (s_id, row["surah_name"], row.get("transliteration", ""))
            
            verses_to_insert.append((
                s_id,
                row["verse_id"],
                row["text"],
                row["translation"]
            ))
            
        # 3. Batch Bulk Execution (High-Performance Data Engineering)
        logging.info(f"[Postgres Load] Bulk inserting {len(distinct_surahs)} surah dimensions...")
        surah_query = """
            INSERT INTO surahs (id, name, transliteration) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (id) DO NOTHING;
        """
        psycopg2.extras.execute_batch(cursor, surah_query, list(distinct_surahs.values()))
        
        logging.info(f"[Postgres Load] Bulk inserting {len(verses_to_insert)} verse records...")
        verse_query = """
            INSERT INTO verses (surah_id, verse_number, arabic_text, english_translation) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (surah_id, verse_number) DO NOTHING;
        """
        psycopg2.extras.execute_batch(cursor, verse_query, verses_to_insert)
        
        # Commit transaction cleanly
        conn.commit()
        logging.info("[Postgres Load] Production data sync complete. Transaction committed.")
        
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        logging.error(f"[Postgres Load] Pipeline aborted. Database transaction rolled back: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    load_silver_to_postgres()