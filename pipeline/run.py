from pipeline.monitor import fetch_latest_filings
from pipeline.parser import process_filing
from pipeline.mapping import enrich_positions
from db.client import insert_filing, insert_holdings, insert_security_mappings
import requests

HEADERS = {
    "User-Agent": "OwnershipTracker/1.0 (myshandle91869@sudomail.com)",
    "Accept-Encoding": "gzip, deflate",
}

# The Big Three — direct CIK + accession targeting
BIG_THREE = [
    {
        "cik": "1364742",
        "accession_number": "0001086364-24-008417",
        "company_name": "BlackRock Finance, Inc.",
        "filing_date": "2024-08-13",
        "filing_url": "https://www.sec.gov/Archives/edgar/data/1364742/000108636424008417/0001086364-24-008417-index.htm"
    },
    {
        "cik": "102909",
        "accession_number": "0000102909-26-000031",
        "company_name": "Vanguard Group Inc",
        "filing_date": "2026-01-29",
        "filing_url": "https://www.sec.gov/Archives/edgar/data/102909/000010290926000031/0000102909-26-000031-index.htm"
    },
    {
        "cik": "93751",
        "accession_number": "0000093751-26-000315",
        "company_name": "State Street Corp",
        "filing_date": "2026-05-15",
        "filing_url": "https://www.sec.gov/Archives/edgar/data/93751/000009375126000315/0000093751-26-000315-index.htm"
    }
]


def run_big_three():
    """
    Directly ingest the Big Three institutional holders.
    BlackRock, Vanguard, State Street.
    """
    print("[pipeline] Ingesting Big Three...")

    for filing in BIG_THREE:
        print(f"\n[pipeline] Processing: {filing['company_name']}")

        insert_filing(filing)

        positions = process_filing(filing)
        if not positions:
            print(f"[pipeline] No positions found — skipping")
            continue

        enriched = enrich_positions(positions)

        mappings = [
            {
                "cusip": p["cusip"],
                "figi": p.get("figi"),
                "ticker": p.get("ticker"),
                "security_name": p.get("security_name"),
                "security_type": p.get("security_type"),
            }
            for p in enriched if p.get("cusip")
        ]
        insert_security_mappings(mappings)
        insert_holdings(enriched)

    print("\n[pipeline] Big Three ingestion complete")


def run_pipeline():
    """
    Full pipeline run on latest EDGAR filings.
    """
    print("[pipeline] Starting full run...")
    filings = fetch_latest_filings()
    print(f"[pipeline] Found {len(filings)} filings to process")

    for filing in filings[:3]:
        print(f"\n[pipeline] Processing: {filing['company_name']}")
        insert_filing(filing)
        positions = process_filing(filing)
        if not positions:
            continue
        enriched = enrich_positions(positions)
        mappings = [
            {
                "cusip": p["cusip"],
                "figi": p.get("figi"),
                "ticker": p.get("ticker"),
                "security_name": p.get("security_name"),
                "security_type": p.get("security_type"),
            }
            for p in enriched if p.get("cusip")
        ]
        insert_security_mappings(mappings)
        insert_holdings(enriched)

    print("\n[pipeline] Run complete")


if __name__ == "__main__":
    run_big_three()