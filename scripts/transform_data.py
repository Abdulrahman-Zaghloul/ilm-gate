
import json
import os
import logging

# Configure logging for the transformation pipeline
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def transform_to_silver():
    logging.info("[Silver ETL] Transforming Bronze data...")
    
    input_path = "data/bronze/quran_raw.json"
    output_dir = "data/silver"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    silver_data = []
    
    # Flattening logic
    for surah in raw_data:
        surah_id = surah.get("id")
        surah_name = surah.get("name")
        
        # Access the 'verses' array within each surah
        for verse in surah.get("verses", []):
            silver_data.append({
                "surah_id": surah_id,
                "surah_name": surah_name,
                "verse_id": verse.get("id"),
                "text": verse.get("text"),
                "translation": verse.get("translation")
            })
            
    with open(os.path.join(output_dir, "quran_silver.json"), 'w', encoding='utf-8') as f:
        json.dump(silver_data, f, ensure_ascii=False, indent=4)
        
    logging.info(f"[Silver ETL] Transformation complete. {len(silver_data)} verses processed.")

if __name__ == "__main__":
    transform_to_silver()