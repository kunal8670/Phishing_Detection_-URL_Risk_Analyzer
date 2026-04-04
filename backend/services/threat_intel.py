import os
import re
import psycopg2
from psycopg2.pool import SimpleConnectionPool

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "threats_db")
DB_USER = os.getenv("DB_USER", "threddb")
DB_PASS = os.getenv("DB_PASS", "12345")

DOMAIN_PATTERN = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$"
)

pool = None


def get_pool():
    global pool
    if pool is None:
        pool = SimpleConnectionPool(
            minconn=2,
            maxconn=20,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
    return pool


def init_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS malicious_domains (
            domain TEXT PRIMARY KEY,
            sources TEXT NOT NULL,
            added_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON malicious_domains(domain)")
    conn.commit()
    conn.close()


def _is_valid_domain(domain):
    if not domain or not isinstance(domain, str):
        return False
    return DOMAIN_PATTERN.match(domain) is not None


def check_threat_intel(domain):
    if not _is_valid_domain(domain):
        return {"found": False, "sources": []}

    p = get_pool()
    conn = p.getconn()
    try:
        cursor = conn.cursor()
        check_domains = [domain]
        if domain.startswith("www."):
            check_domains.append(domain[4:])
        else:
            check_domains.append("www." + domain)

        for check_domain in check_domains:
            cursor.execute(
                "SELECT sources FROM malicious_domains WHERE domain = %s",
                (check_domain,),
            )
            row = cursor.fetchone()
            if row:
                sources = [s.strip() for s in row[0].split(",") if s.strip()]
                return {"found": True, "sources": sources}
        return {"found": False, "sources": []}
    finally:
        p.putconn(conn)
