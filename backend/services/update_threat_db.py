#!/usr/bin/env python3
"""
Standalone script to update the threat intelligence database (PostgreSQL).

Downloads feeds from OpenPhish and URLHaus, extracts unique domains,
and populates the PostgreSQL threats_db database.

Usage:
    python services/update_threat_db.py

Can be scheduled via cron:
    0 */6 * * * cd /path/to/backend && python services/update_threat_db.py
"""

import os
import requests
import psycopg2
from datetime import datetime, timezone
from urllib.parse import urlparse

OPENPHISH_FEED = "https://openphish.com/feed.txt"
URLHAUS_FEED = "https://urlhaus.abuse.ch/downloads/text/"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "threats_db")
DB_USER = os.getenv("DB_USER", "threddb")
DB_PASS = os.getenv("DB_PASS", "12345")


def download_domains(feed_url, source_name):
    """Download a feed and extract unique domains."""
    domains = set()
    print(f"  Downloading {source_name} feed...")

    try:
        resp = requests.get(feed_url, timeout=60)
        if resp.status_code != 200:
            print(f"  WARNING: {source_name} returned HTTP {resp.status_code}")
            return domains

        for line in resp.text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            try:
                parsed = urlparse(line)
                domain = parsed.netloc.split(":")[0].lower()
                if domain:
                    domains.add(domain)
            except Exception:
                continue

        print(f"  {source_name}: {len(domains)} unique domains extracted")
    except Exception as e:
        print(f"  ERROR: {source_name} feed failed — {e}")

    return domains


def build_database():
    """Download all feeds, merge domains, and populate PostgreSQL."""
    print("=" * 60)
    print("Threat Intelligence Database Update (PostgreSQL)")
    print("=" * 60)

    openphish_domains = download_domains(OPENPHISH_FEED, "OpenPhish")
    urlhaus_domains = download_domains(URLHAUS_FEED, "URLHaus")

    domain_sources = {}
    for domain in openphish_domains:
        domain_sources[domain] = {"openphish"}
    for domain in urlhaus_domains:
        if domain in domain_sources:
            domain_sources[domain].add("urlhaus")
        else:
            domain_sources[domain] = {"urlhaus"}

    only_openphish = sum(1 for s in domain_sources.values() if s == {"openphish"})
    only_urlhaus = sum(1 for s in domain_sources.values() if s == {"urlhaus"})
    both = sum(1 for s in domain_sources.values() if len(s) == 2)

    print(f"\n  Total unique domains: {len(domain_sources)}")
    print(f"    OpenPhish only:  {only_openphish}")
    print(f"    URLHaus only:    {only_urlhaus}")
    print(f"    Both sources:    {both}")

    print(f"\n  Writing to PostgreSQL: {DB_NAME}@{DB_HOST}:{DB_PORT}...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE malicious_domains")

    now = datetime.now(timezone.utc).isoformat()
    entries = [
        (domain, ",".join(sorted(sources)), now, now)
        for domain, sources in domain_sources.items()
    ]

    cursor.executemany(
        "INSERT INTO malicious_domains (domain, sources, added_at, updated_at) VALUES (%s, %s, %s, %s)",
        entries,
    )

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM malicious_domains")
    count = cursor.fetchone()[0]
    conn.close()

    print(f"\n  Database updated: {count} domains in {DB_NAME}")
    print("=" * 60)
    print("Update complete!")
    print("=" * 60)


if __name__ == "__main__":
    build_database()
