import os
import json
import logging
import urllib.request

# Configure standard telemetry logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

# Immutable version-locked CDN endpoint (Bypasses mutable API issues)
DATA_URL = "https://unpkg.com/quran-json@3.1.2/dist/quran_en.json"

def ingest_bronze_layer():
    logging.info("[Bronze ETL] Commencing data extraction from immutable CDN...")
    
    bronze_dir = "data/bronze"
    os.makedirs(bronze_dir, exist_ok=True)
    output_path = os.path.join(bronze_dir, "quran_raw.json")
    
    # Standard request context header
    req = urllib.request.Request(
        DATA_URL, 
        headers={'User-Agent': 'Mozilla/5.0 DataEngineerPipeline/1.0'}
    )
    
    try:
        logging.info(f"[Bronze ETL] Establishing clean stream link to immutable data tier...")
        
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_text = response.read().decode('utf-8')
            payload = json.loads(raw_text)
            
        logging.info("[Bronze ETL] Payload downloaded successfully. Compiling local cache...")
        
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=4)
            
        logging.info(f"[Bronze ETL] Success! Pristine raw layer cached to: {output_path}")
        
    except Exception as e:
        logging.error(f"[Bronze ETL] Pipeline ingestion execution halted: {e}")

if __name__ == "__main__":
    ingest_bronze_layer()