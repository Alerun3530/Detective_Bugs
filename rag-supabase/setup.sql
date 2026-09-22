-- Correr esto en Supabase → SQL Editor, antes de correr el script de Python.

-- 1. Habilitar la extensión de vectores
create extension if not exists vector;

-- 2. Tabla que va a guardar el "Contexto del proyecto" (Módulo 4)
--    embedding usa 1536 dimensiones porque es lo que devuelve
--    text-embedding-3-small de OpenAI.
create table if not exists documents_bugs (
  id bigint generated always as identity primary key,
  content text not null,
  embedding vector(1536),
  metadata jsonb,
  created_at timestamp with time zone default now()
);

-- 3. Índice para que la búsqueda por similitud sea rápida
create index if not exists documents_bugs_embedding_idx
  on documents_bugs using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- 4. Función RPC de búsqueda — esto es lo que el nodo Vector Store de n8n
--    (o cualquier retrieval que armes a mano) va a llamar para traer los
--    N chunks más parecidos al error nuevo.
create or replace function match_documents_bugs (
  query_embedding vector(1536),
  match_count int default 5,
  filter jsonb default '{}'
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documents_bugs.id,
    documents_bugs.content,
    documents_bugs.metadata,
    1 - (documents_bugs.embedding <=> query_embedding) as similarity
  from documents_bugs
  where documents_bugs.metadata @> filter
  order by documents_bugs.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- 5. Tabla separada para el "Historial de incidentes" (la otra colección
--    del Módulo 4 — se llena después, cuando resuelvan casos reales, no
--    ahora que estamos cargando el contexto inicial del proyecto).
create table if not exists incidentes (
  id bigint generated always as identity primary key,
  content text not null,
  embedding vector(1536),
  metadata jsonb,
  created_at timestamp with time zone default now()
);

create index if not exists incidentes_embedding_idx
  on incidentes using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create or replace function match_incidentes (
  query_embedding vector(1536),
  match_count int default 5,
  filter jsonb default '{}'
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    incidentes.id,
    incidentes.content,
    incidentes.metadata,
    1 - (incidentes.embedding <=> query_embedding) as similarity
  from incidentes
  where incidentes.metadata @> filter
  order by incidentes.embedding <=> query_embedding
  limit match_count;
end;
$$;
