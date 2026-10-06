
 Zomato AI Data Engineering & Analytics Platform

An end-to-end data engineering and AI analytics project built around Zomato restaurant data.

The project demonstrates a complete workflow from raw data processing and warehouse transformation to analytical queries and AI-powered interaction with structured and unstructured data.

---

 Project Overview

The system processes Zomato datasets through a structured data engineering pipeline and makes the resulting data available for analytics and AI-based querying.

The pipeline includes:

- Data ingestion and processing using Python
- Snowflake as the analytical data warehouse
- dbt for SQL-based data transformation
- Apache Airflow for workflow orchestration
- Docker for the Airflow environment
- Streamlit for interactive applications
- Llama 3.2 through Ollama for local AI inference
- Sentence Transformers for semantic embeddings
- RAG for querying restaurant reviews
- Text-to-SQL for querying structured warehouse data

---

 Architecture

```text
                    Raw Zomato Data
                           |
                           v
                        Python
                           |
                           v
                      Snowflake
                           |
                           v
                    dbt Transformations
                           |
                  +--------+--------+
                  |                 |
               Staging            Marts
                  |                 |
                  +--------+--------+
                           |
                           v
                  Airflow + Docker
                           |
                           v
                    Analytics Layer
                           |
              +------------+------------+
              |                         |
              v                         v
        Review RAG Assistant       Text-to-SQL
              |                         |
              v                         v
        Semantic Search             Snowflake
              |                         |
              +------------+------------+
                           |
                           v
                  Llama 3.2 / Ollama