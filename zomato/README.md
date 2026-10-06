# Zomato AI Data Engineering & Analytics

An end-to-end data engineering and AI analytics project built using Zomato restaurant data.

## Project Overview

The project processes raw Zomato data through data ingestion, transformation, warehousing and analytics. An AI layer was also added to allow users to interact with restaurant reviews and structured data using natural language.

## Architecture

```text
Raw Zomato Data
       ↓
Python
       ↓
Snowflake
       ↓
dbt Transformations
       ↓
Staging → Marts
       ↓
Airflow + Docker
       ↓
Streamlit Analytics
       ↓
AI Layer
   ┌───────────────┬────────────────┐
   │ RAG           │ Text-to-SQL    │
   │ Reviews       │ Snowflake Data │
   └───────────────┴────────────────┘
       ↓
Llama 3.2 + Ollama