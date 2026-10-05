import os
import json
import pandas as pd
import streamlit as st
import snowflake.connector
import ollama
from dotenv import load_dotenv

load_dotenv()

# Local Llama model running through Ollama
MODEL = "llama3.2:3b"

FORBIDDEN_WORDS = [
    "drop", "delete", "truncate", "alter",
    "update", "insert", "create", "replace",
    "grant", "revoke"
]

EXAMPLE_QUESTIONS = [
    "Top 10 cities by GMV",
    "Which cuisine has the most orders?",
    "Average delivery time by city, worst first",
    "Cancel rate by payment method"
]


SCHEMA = """
Tables available in Snowflake. Use bare table names, no database
or schema prefix.

FCT_ORDERS(
    order_id,
    order_date,
    customer_id,
    restaurant_id,
    city,
    cuisine,
    payment_method,
    order_status,
    is_delivered,
    sales_amount,
    discount,
    delivery_fee,
    gst,
    customer_rating,
    delivery_time_min
)

DIM_RESTAURANT(
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    rating,
    cost_for_two
)

DIM_CUSTOMER(
    customer_id,
    customer_name,
    age,
    age_segment,
    gender,
    city
)

MART_DAILY_CITY_REVENUE(
    order_date,
    city,
    orders,
    cancel_rate,
    gmv,
    aov
)

MART_RESTAURANT_PERFORMANCE(
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    orders,
    revenue,
    avg_customer_rating,
    cancel_rate
)

MART_DELIVERY_SLA(
    city,
    order_hour,
    delivered_orders,
    p50_delivery_min,
    late_rate
)

Note:
- gmv means delivered revenue.
- Prefer MART_ tables when they fit the question.
"""


SYSTEM_PROMPT = f"""
You are a Snowflake SQL expert.

Convert the user's natural-language question into ONE SQL query.

Rules:
- Generate SELECT queries only.
- Never modify data.
- You may use WITH/CTEs.
- Use bare table names.
- Do not use database or schema prefixes.
- Add LIMIT 100 or less unless the question asks for a single total.
- Return ONLY valid JSON.
- The JSON must have exactly this format:

{{"sql": "your SQL query here"}}

Database schema:

{SCHEMA}
"""


# -----------------------------
# Snowflake connection
# -----------------------------

@st.cache_resource
def get_connection():

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="MARTS",
        role="DBT_ROLE"
    )


# -----------------------------
# Llama → SQL
# -----------------------------


def generate_sql(question):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        options={
            "temperature": 0
        }
    )

    answer = response["message"]["content"]

    sql = json.loads(answer)["sql"]

    sql = sql.replace("ZOMATO.MARTS.", "").replace("ZOMATO.", "")

    # Fix known table-name typo
    sql = sql.replace(
        "MART_DAILY_CITY_REVENUNE",
        "MART_DAILY_CITY_REVENUE"
    )

    return sql.strip().rstrip(";")


# -----------------------------
# SQL safety check
# -----------------------------

def is_safe(sql):

    lowered = sql.lower().strip()

    # Only SELECT or WITH queries
    if not (
        lowered.startswith("select")
        or lowered.startswith("with")
    ):
        return False

    # Reject dangerous SQL commands
    for word in FORBIDDEN_WORDS:

        if word in lowered:
            return False

    return True


# -----------------------------
# Execute SQL in Snowflake
# -----------------------------

def run_query(sql):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("USE DATABASE ZOMATO")
    cursor.execute("USE SCHEMA MARTS")

    return cursor.execute(sql).fetch_pandas_all()


# -----------------------------
# Streamlit UI
# -----------------------------

st.title("Chat with your Zomato Data")

st.caption(
    f"Ask in English, {MODEL} generates the SQL, "
    "and Snowflake executes it."
)


with st.sidebar:

    st.header("Example Questions")

    for q in EXAMPLE_QUESTIONS:

        st.markdown(f"- {q}")


question = st.text_input(
    "Enter your question here",
    placeholder="e.g. Top 10 restaurants by revenue in Bangalore"
)


if question:

    try:

        # Step 1: Llama generates SQL
        sql = generate_sql(question)

        # Show generated SQL
        st.subheader("Generated SQL")

        st.code(sql, language="sql")


        # Step 2: Safety check
        if not is_safe(sql):

            st.error(
                "The generated SQL is not safe to run."
            )

        else:

            # Step 3: Execute in Snowflake
            df = run_query(sql)

            st.success(
                f"{len(df)} rows returned"
            )

            # Step 4: Display results
            st.dataframe(
                df,
                hide_index=True
            )


            # Simple visualization
            if (
                len(df.columns) == 2
                and pd.api.types.is_numeric_dtype(
                    df.iloc[:, 1]
                )
            ):

                st.bar_chart(
                    df,
                    x=df.columns[0],
                    y=df.columns[1]
                )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )