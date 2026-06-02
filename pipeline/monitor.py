import requests
import xml.etree.ElementTree as ET
from typing import Optional
import time
from datetime import datetime, timezone

# ----------------------------------------------------------------
# EDGAR Fair Access Policy — required or they block your IP
# Replace with your pseudonym email
# ----------------------------------------------------------------
HEADERS = {
    "User-Agent": "OwnershipTracker/1.0 (myshandle91869@sudomail.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

EDGAR_RSS = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR&dateb=&owner=include&count=40&search_text=&output=atom"

def fetch_latest_filings() -> list[dict]:
    """
    Poll EDGAR RSS feed for latest 13F-HR filings.
    Returns a list of new filing metadata dicts.
    """
    try:
        response = requests.get(EDGAR_RSS, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[monitor] EDGAR request failed: {e}")
        return []

    filings = []
    root = ET.fromstring(response.content)

    # EDGAR RSS uses Atom namespace
    namespace = "{http://www.w3.org/2005/Atom}"

    for entry in root.findall(f"{namespace}entry"):
        filing = parse_entry(entry, namespace)
        if filing:
            #skip amendment - only want origional filings 
            if filing.get("company_name") in ["13F-HR/A"]:
                continue
            filings.append(filing)

    print(f"[monitor] Found {len(filings)} 13F-HR filings")
    return filings


def parse_entry(entry, namespace: str) -> Optional[dict]:
    """
    Parse a single Atom entry from EDGAR RSS.
    Extracts CIK, accession number, company name, filing date.
    """
    try:
        title = entry.findtext(f"{namespace}title", default="")
        updated = entry.findtext(f"{namespace}updated", default="")
        link = entry.find(f"{namespace}link")
        filing_url = link.get("href", "") if link is not None else ""

        # Skip amendments
        if "13F-HR/A" in title:
            return None

        # Extract accession number from URL
        parts = filing_url.strip("/").split("/")
        cik = parts[-3] if len(parts) >= 3 else None
        accession = parts[-2] if len(parts) >= 2 else None

        if not cik or not accession:
            return None

        # Clean company name — title format is "13F-HR - Company Name (CIK) (Filer)"
        raw_name = title.split(" - ", 1)[1].strip() if " - " in title else title.strip()
        clean_name = raw_name.split("(")[0].strip()

        return {
            "cik": cik,
            "accession_number": accession,
            "company_name": clean_name,
            "filing_date": updated[:10],
            "filing_url": filing_url,
            "fetched_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        }

    except Exception as e:
        print(f"[monitor] Failed to parse entry: {e}")
        return None

def run_monitor(interval_seconds: int = 3600):
    """
    Main loop — polls EDGAR every hour by default.
    In production this is replaced by GitHub Actions cron.
    """
    print("[monitor] Starting EDGAR monitor...")
    while True:
        filings = fetch_latest_filings()
        for filing in filings:
            print(f"[monitor] New filing: {filing['company_name']} | {filing['filing_date']}")
        print(f"[monitor] Sleeping {interval_seconds}s...")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    # Quick test — fetch once and print
    filings = fetch_latest_filings()
    for f in filings:
        print(f)