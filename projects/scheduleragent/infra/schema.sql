-- ============================================================
-- LifeAgent — Supabase schema
-- Run once in the Supabase SQL editor.
-- ============================================================

-- Enable pgvector for semantic search on notes
create extension if not exists vector;

-- ── Tasks ────────────────────────────────────────────────────
create table if not exists tasks (
    id          uuid primary key default gen_random_uuid(),
    user_id     text        not null,
    title       text        not null,
    description text,
    status      text        not null default 'pending'
                            check (status in ('pending', 'in_progress', 'done')),
    due_date    timestamptz,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

create index if not exists tasks_user_id_idx on tasks (user_id);
create index if not exists tasks_status_idx  on tasks (user_id, status);

-- ── Notes ────────────────────────────────────────────────────
create table if not exists notes (
    id          uuid primary key default gen_random_uuid(),
    user_id     text        not null,
    content     text        not null,
    embedding   vector(384),          -- all-MiniLM-L6-v2 output dimension
    created_at  timestamptz not null default now()
);

create index if not exists notes_user_id_idx on notes (user_id);

-- Similarity search function used by notes_db.py
create or replace function match_notes(
    query_embedding vector(384),
    match_user_id   text,
    match_count     int default 5
)
returns table (
    id         uuid,
    content    text,
    similarity float
)
language sql stable
as $$
    select
        id,
        content,
        1 - (embedding <=> query_embedding) as similarity
    from notes
    where user_id = match_user_id
      and embedding is not null
    order by embedding <=> query_embedding
    limit match_count;
$$;

-- ── Memory / Preferences ─────────────────────────────────────
create table if not exists memory (
    id         uuid primary key default gen_random_uuid(),
    user_id    text        not null,
    key        text        not null,
    value      text        not null,
    updated_at timestamptz not null default now(),
    unique (user_id, key)
);

create index if not exists memory_user_id_idx on memory (user_id);
