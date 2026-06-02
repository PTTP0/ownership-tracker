from pipeline.monitor import fetch_latest_filings
from pipeline.parser import process_filing
from pipeline.mapping import enrich_positions
from db.client import insert_filing, insert_holdings, insert_security_mappings


def run_pipeline():
    """
    Full pipeline run:
    1. Fetch latest filings from EDGAR
    2. Parse holdings from each filing
    3. Resolve CUSIPs to FIGIs
    4. Store everything in Supabase
    """
    print("[pipeline] Starting full run...")

    filings = fetch_latest_filings()
    print(f"[pipeline] Found {len(filings)} filings to process")

    for filing in filings[:3]:  # Start with 3 for MVP testing
        print(f"\n[pipeline] Processing: {filing['company_name']}")

        # Store filing metadata
        insert_filing(filing)

        # Parse positions
        positions = process_filing(filing)
        if not positions:
            print(f"[pipeline] No positions found — skipping")
            continue

        # Enrich with FIGIs
        enriched = enrich_positions(positions)

        # Cache security mappings
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

        # Store holdings
        insert_holdings(enriched)

    print("\n[pipeline] Run complete")


if __name__ == "__main__":
    run_pipeline()