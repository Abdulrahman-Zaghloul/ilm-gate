
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def build_gold_layer():
    logging.info("[Gold ETL] Starting transformation for AI ingestion...")
    
    input_path = "data/silver/quran_silver.json"
    output_dir = "data/gold"
    
    # Ensure the gold directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the normalized Silver Data
    with open(input_path, 'r', encoding='utf-8') as f:
        silver_data = json.load(f)
    
    output_path = os.path.join(output_dir, "quran_ai_corpus.jsonl")
    
    logging.info("[Gold ETL] Restructuring data into JSON Lines (JSONL) format...")
    
    # Write to JSONL format
    with open(output_path, 'w', encoding='utf-8') as f:
        for row in silver_data:
            # Constructing a highly specific payload tailored for AI prompting/context
            ai_payload = {
                "reference": f"{row['surah_name']} {row['surah_id']}:{row['verse_id']}",
                "arabic_text": row['text'],
                "english_translation": row['translation']
            }
            # json.dumps converts the single dictionary to a string, and we add a newline
            f.write(json.dumps(ai_payload, ensure_ascii=False) + '\n')
            
    logging.info(f"[Gold ETL] Gold layer successfully created at {output_path}")

if __name__ == "__main__":
    build_gold_layer()