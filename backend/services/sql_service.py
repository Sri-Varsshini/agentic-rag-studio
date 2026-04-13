from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.openai_api_key)

# Tables to expose for querying (exclude internal/system tables)
ALLOWED_SCHEMAS = ["public"]


def get_schema_context(supabase) -> str:
    """Fetch table/column info from information_schema for allowed schemas."""
    result = supabase.rpc("get_schema_info").execute()
    if result.data:
        lines = []
        current_table = None
        for row in result.data:
            if row["table_name"] != current_table:
                current_table = row["table_name"]
                lines.append(f"\nTable: {current_table}")
            lines.append(f"  - {row['column_name']} ({row['data_type']})")
        return "\n".join(lines)
    return "No schema information available."


def generate_sql(natural_language_query: str, schema_context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a SQL expert. Generate a single read-only SELECT query based on the user's question and the schema below.\n"
                    "Rules:\n"
                    "- Only SELECT statements allowed\n"
                    "- No INSERT, UPDATE, DELETE, DROP, CREATE, or any mutations\n"
                    "- Return ONLY the SQL query, no explanation, no markdown\n"
                    f"\nSchema:\n{schema_context}"
                )
            },
            {"role": "user", "content": natural_language_query}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def is_select_only(sql: str) -> bool:
    normalized = sql.strip().upper()
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
    if not normalized.startswith("SELECT"):
        return False
    return not any(keyword in normalized for keyword in forbidden)


def query_database(supabase, natural_language_query: str) -> str:
    try:
        schema_context = get_schema_context(supabase)
        sql = generate_sql(natural_language_query, schema_context)
        print(f"[sql_service] generated SQL: {sql}")

        if not is_select_only(sql):
            return "Error: Only SELECT queries are allowed."

        result = supabase.rpc("execute_sql", {"query": sql}).execute()
        if not result.data:
            return "Query returned no results."

        rows = result.data
        if not rows:
            return "No results found."

        headers = list(rows[0].keys())
        lines = [" | ".join(headers)]
        lines.append("-" * len(lines[0]))
        for row in rows[:50]:  # cap at 50 rows
            lines.append(" | ".join(str(row.get(h, "")) for h in headers))

        return "\n".join(lines)
    except Exception as e:
        print(f"[sql_service] error: {e}")
        return f"Database query failed: {str(e)}"
