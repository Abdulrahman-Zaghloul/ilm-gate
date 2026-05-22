# Ilm-Gate: Foundational Islamic Source AI (IN PROGRESS)

A conservative, source-verified AI assistant designed to provide accurate rulings based exclusively on the Holy Quran, Sahih al-Bukhari, and Sahih Muslim. Built with a "Strict Guardrail" RAG architecture to ensure absolute adherence to foundational texts.

## 🏗️ System Architecture

This project uses a RAG (Retrieval-Augmented Generation) pipeline with metadata filtering to maintain scholarly integrity:

> **[User Query]** -> **[Metadata-Filter]** -> **[Vector Store]** -> **[System Guardrail Prompt]** -> **[Verified Source Citation]**

## 🚀 Key Engineering Features

* **Strict Source Governance**: Uses a "Conservative Guardrail" prompt—if an answer isn't in the verified source text, the AI is instructed to refuse the answer rather than hallucinate.
* **Comparative Jurisprudence**: Built to analyze and present comparative nuances across the four major Sunni schools of thought (Hanafi, Shafi'i, Maliki, Hanbali) where applicable.
* **Metadata-Driven Retrieval**: Every text chunk is tagged with its source (Quran/Bukhari/Muslim), allowing the engine to provide exact citations for every ruling.
* **Production Observability**: Full pipeline logging and error handling to ensure data integrity during ingestion and processing.

## 🛠️ Technology Stack
* **Language**: Python 3
* **Vector Engine**: ChromaDB
* **Framework**: Streamlit (UI) & LangChain
* **Data Sources**: Authenticated text repositories (Quran.com/Sunnah.com schemas)

## 🔮 Future Roadmap
* **Multilingual Citation**: Implementation of side-by-side Arabic/English rendering.
* **Operational Webhooks**: Integration of status monitoring for pipeline ingestion health.
