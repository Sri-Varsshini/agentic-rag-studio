-- RPC: get_schema_info
-- Returns table/column info for public schema tables (excluding internal ones)
create or replace function get_schema_info()
returns table(table_name text, column_name text, data_type text)
language sql
security definer
as $$
  select
    c.table_name::text,
    c.column_name::text,
    c.data_type::text
  from information_schema.columns c
  where c.table_schema = 'public'
    and c.table_name not in ('schema_migrations')
  order by c.table_name, c.ordinal_position;
$$;

-- RPC: execute_sql
-- Executes a read-only SQL query and returns results as JSON rows
-- Note: The SELECT-only validation is enforced in the application layer (sql_service.py)
create or replace function execute_sql(query text)
returns json
language plpgsql
security definer
as $$
declare
  result json;
begin
  execute 'select json_agg(t) from (' || query || ') t' into result;
  return coalesce(result, '[]'::json);
end;
$$;
