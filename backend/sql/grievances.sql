-- Paste this into the Supabase SQL editor (see README "Track a grievance").
-- The FastAPI backend uses the service_role key, which bypasses RLS.
-- Do not add policies that let anon or authenticated users read this table.

create table if not exists public.grievances (
  sr_id text primary key,
  key_hash text not null,
  service_id text not null,
  department text not null,
  status text not null default 'Received',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.grievances enable row level security;

comment on table public.grievances is
  'Demo civic tracking records. key_hash is HMAC-SHA256 of the one-time access key; plaintext keys are never stored.';
