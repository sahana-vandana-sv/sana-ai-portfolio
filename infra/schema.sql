-- Run in Supabase SQL Editor

-- Enable pgvector
create extension if not exists vector;

-- Tasks
create table if not exists tasks (
  id          uuid primary key,
  user_id     text not null,
  title       text not null,
  due_date    timestamptz,
  completed   boolean default false,
  created_at  timestamptz default now()
);
create index if not exists tasks_user_id_idx on tasks(user_id);

-- Notes (with vector embedding)
create table if not exists notes (
  id          uuid primary key,
  user_id     text not null,
  content     text not null,
  entities    jsonb default '{}',
  embedding   vector(384),        -- all-MiniLM-L6-v2 dimension
  created_at  timestamptz default now()
);
create index if not exists notes_user_id_idx on notes(user_id);

-- Memory / preferences
create table if not exists memory (
  id          uuid primary key,
  user_id     text not null,
  content     text not null,
  entities    jsonb default '{}',
  created_at  timestamptz default now()
);
create index if not exists memory_user_id_idx on memory(user_id);

-- pgvector similarity search function for notes
create or replace function match_notes(
  query_embedding vector(384),
  match_user_id   text,
  match_count     int default 5
)
returns table (
  id          uuid,
  content     text,
  entities    jsonb,
  created_at  timestamptz,
  similarity  float
)
language sql stable
as $$
  select
    id, content, entities, created_at,
    1 - (embedding <=> query_embedding) as similarity
  from notes
  where user_id = match_user_id
  order by embedding <=> query_embedding
  limit match_count;
$$;
