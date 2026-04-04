CREATE TABLE IF NOT EXISTS malicious_domains (
    domain TEXT PRIMARY KEY,
    sources TEXT NOT NULL,
    added_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_domain ON malicious_domains(domain);
