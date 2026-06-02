import requests
import time
from typing import Optional
from datetime import datetime, timezone

OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"

# Get a free key at openfigi.com — increases rate limit from 25 to 250 req/min
# Add to .env file as OPENFIGI_API_KEY
# Leave as None to use without key during development
OPENFIGI_API_KEY = None

HEADERS = {
    "Content-Type": "application/json",
}

if OPENFIGI_API_KEY:
    HEADERS["X-OPENFIGI-APIKEY"] = OPENFIGI_API_KEY

# In-memory cache for this session
# In production this gets replaced by Supabase cache lookup
_cusip_cache: dict[str, dict] = {}


def resolve_cusips(cusips: list[str]) -> dict[str, dict]:
    """
    Takes a list of CUSIPs and returns a dict mapping
    each CUSIP to its resolved security data.
    
    Uses cache first, only calls OpenFIGI for unknowns.
    Batches 100 CUSIPs per request per OpenFIGI limits.
    """
    results = {}
    uncached = []

    # Check cache first
    for cusip in cusips:
        if cusip in _cusip_cache:
            results[cusip] = _cusip_cache[cusip]
        else:
            uncached.append(cusip)

    if not uncached:
        print(f"[mapping] All {len(cusips)} CUSIPs resolved from cache")
        return results

    print(f"[mapping] Resolving {len(uncached)} CUSIPs via OpenFIGI...")

    # Batch into groups of 100
    batch_size = 100 if OPENFIGI_API_KEY else 10
    batches = [uncached[i:i+batch_size] for i in range(0, len(uncached), batch_size)]

    for batch in batches:
        batch_results = _fetch_figi_batch(batch)
        results.update(batch_results)
        _cusip_cache.update(batch_results)

        # Rate limit — 25 req/min without key, 250 with key
        if not OPENFIGI_API_KEY:
            time.sleep(2.5)
        else:
            time.sleep(0.25)

    return results


def _fetch_figi_batch(cusips: list[str]) -> dict[str, dict]:
    """
    Send one batch of up to 100 CUSIPs to OpenFIGI.
    Returns dict of CUSIP -> security data.
    """
    payload = [{"idType": "ID_CUSIP", "idValue": c} for c in cusips]

    try:
        response = requests.post(
            OPENFIGI_URL,
            json=payload,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[mapping] OpenFIGI request failed: {e}")
        return {}

    data = response.json()
    results = {}

    for i, item in enumerate(data):
        cusip = cusips[i]

        if "data" not in item or not item["data"]:
            print(f"[mapping] No FIGI found for CUSIP: {cusip}")
            results[cusip] = {
                "cusip": cusip,
                "figi": None,
                "ticker": None,
                "security_name": None,
                "security_type": None,
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }
            continue

        # Take the first result
        security = item["data"][0]

        results[cusip] = {
            "cusip": cusip,
            "figi": security.get("figi"),
            "ticker": security.get("ticker"),
            "security_name": security.get("name"),
            "security_type": security.get("securityType"),
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }

    return results


def enrich_positions(positions: list[dict]) -> list[dict]:
    """
    Takes parsed positions from parser.py and adds
    FIGI + ticker to each one.
    CUSIP stays in the dict for backend use only.
    """
    cusips = [p["cusip"] for p in positions if p.get("cusip")]
    mappings = resolve_cusips(cusips)

    enriched = []
    for position in positions:
        cusip = position.get("cusip")
        mapping = mappings.get(cusip, {})

        enriched.append({
            **position,
            "figi": mapping.get("figi"),
            "ticker": mapping.get("ticker"),
            "security_name": mapping.get("security_name"),
            "security_type": mapping.get("security_type"),
        })

    return enriched


if __name__ == "__main__":
    # Test with real positions from parser
    from pipeline.monitor import fetch_latest_filings
    from pipeline.parser import process_filing

    filings = fetch_latest_filings()
    if filings:
        positions = process_filing(filings[0])
        print(f"\nEnriching {len(positions)} positions...")
        enriched = enrich_positions(positions)
        for p in enriched[:5]:
            print(f"{p['issuer_name']} | {p['ticker']} | {p['figi']} | ${p['value_dollars']:,}")