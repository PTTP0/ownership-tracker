import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

# Single shared client instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_filing(filing: dict) -> dict:
    """Insert a filing record — skip if already exists."""
    try:
        result = supabase.table("filings").upsert(
            filing,
            on_conflict="accession_number"
        ).execute()
        return result.data
    except Exception as e:
        print(f"[db] Failed to insert filing: {e}")
        return {}


def insert_holdings(positions: list[dict]) -> int:
    """Bulk insert holdings positions — skip duplicates."""
    if not positions:
        return 0
    try:
        result = supabase.table("holdings").upsert(
            positions,
            on_conflict="accession_number,cusip"
        ).execute()
        print(f"[db] Inserted {len(positions)} holdings")
        return len(positions)
    except Exception as e:
        print(f"[db] Failed to insert holdings: {e}")
        return 0


def insert_security_mappings(mappings: list[dict]) -> int:
    """Cache CUSIP to FIGI mappings — skip existing."""
    if not mappings:
        return 0
    try:
        result = supabase.table("security_mappings").upsert(
            mappings,
            on_conflict="cusip"
        ).execute()
        print(f"[db] Cached {len(mappings)} security mappings")
        return len(mappings)
    except Exception as e:
        print(f"[db] Failed to insert mappings: {e}")
        return 0


def get_cached_cusips(cusips: list[str]) -> dict[str, dict]:
    """
    Check database for already resolved CUSIPs.
    Returns dict of CUSIP -> mapping data.
    """
    if not cusips:
        return {}
    try:
        result = supabase.table("security_mappings").select("*").in_(
            "cusip", cusips
        ).execute()
        return {row["cusip"]: row for row in result.data}
    except Exception as e:
        print(f"[db] Failed to fetch cached CUSIPs: {e}")
        return {}