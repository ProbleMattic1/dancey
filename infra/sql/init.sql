-- DanceApp schema
CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY,
  source_url TEXT NOT NULL,
  preview_url TEXT,
  duration_ms INTEGER,
  fps REAL,
  width INTEGER,
  height INTEGER,
  status TEXT DEFAULT 'NEW',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analysis_jobs (
  id TEXT PRIMARY KEY,
  video_id TEXT REFERENCES videos(id) ON DELETE CASCADE,
  model_version TEXT,
  state TEXT,
  log JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS segments (
  id BIGSERIAL PRIMARY KEY,
  video_id TEXT REFERENCES videos(id) ON DELETE CASCADE,
  start_ms INTEGER NOT NULL,
  end_ms INTEGER NOT NULL,
  move_id TEXT NOT NULL,
  confidence REAL,
  mirror BOOLEAN DEFAULT FALSE,
  alts JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);
