import requests
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "OwnershipTracker/1.0 (myshandle91869@sudomail.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

# 13F XML namespace
INFO_TABLE_NS = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"


def fetch_filing_index(index_url: str) -> Optional[str]:
    """
    Given an EDGAR index URL, find the XML holdings file
    by parsing the directory listing.
    """
    try:
        # Convert index URL to directory URL
        dir_url = index_url.replace("-index.htm", "").rsplit("/", 1)[0] + "/"
        # Handle both -index.htm and -index.html
        if "-index" in dir_url:
            dir_url = index_url.rsplit("/", 1)[0] + "/"

        response = requests.get(dir_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[parser] Failed to fetch directory: {e}")
        return None

    content = response.text

    # Find all XML file hrefs — skip primary_doc.xml
    xml_files = []
    for line in content.split("<"):
        if 'href="' in line.lower() and ".xml" in line.lower():
            start = line.lower().find('href="') + 6
            end = line.find('"', start)
            path = line[start:end]
            if path.endswith(".xml") and "primary_doc" not in path.lower():
                if not path.startswith("http"):
                    path = f"https://www.sec.gov{path}"
                xml_files.append(path)

    if xml_files:
        print(f"[parser] Found holdings file: {xml_files[0]}")
        return xml_files[0]

    print(f"[parser] No holdings XML found in: {dir_url}")
    return None


def parse_holdings(xml_url: str, cik: str, accession_number: str) -> list[dict]:
    """
    Download and parse a 13F XML information table.
    Returns list of clean position dicts.
    """
    try:
        response = requests.get(xml_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[parser] Failed to fetch XML: {e}")
        return []

    try:
        print(response.text[:2000])
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"[parser] XML parse error: {e}")
        return []

    positions = []

    for info in root.findall(f"{INFO_TABLE_NS}infoTable"):
        position = parse_position(info, cik, accession_number)
        if position:
            positions.append(position)

    print(f"[parser] Extracted {len(positions)} positions from {accession_number}")
    return positions


def parse_position(info, cik: str, accession_number: str) -> Optional[dict]:
    """
    Parse a single infoTable entry into a clean position dict.
    """
    try:
        ns = INFO_TABLE_NS

        issuer = info.findtext(f"{ns}nameOfIssuer", default="").strip()
        cusip = info.findtext(f"{ns}cusip", default="").strip()
        
        # Raw value is in thousands — multiply by 1000
        raw_value = info.findtext(f"{ns}value", default="0") or "0"
        value_dollars = int(raw_value.replace(",", "")) * 1000

        # Shares
        shrs_element = info.find(f"{ns}shrsOrPrnAmt")
        shares = 0
        if shrs_element is not None:
            raw_shares = shrs_element.findtext(f"{ns}sshPrnamt", default="0") or "0"
            shares = int(raw_shares.replace(",", ""))

        # Investment discretion — filter SHARED to avoid double counting
        discretion = info.findtext(f"{ns}investmentDiscretion", default="").strip()
        if discretion == "SHARED":
            return None

        # Voting authority
        voting = info.find(f"{ns}votingAuthority")
        voting_sole = 0
        voting_shared = 0
        if voting is not None:
            sole = voting.findtext(f"{ns}Sole", default="0") or "0"
            shared = voting.findtext(f"{ns}Shared", default="0") or "0"
            voting_sole = int(sole.replace(",", ""))
            voting_shared = int(shared.replace(",", ""))

        if not cusip or not issuer:
            return None

        return {
            "cik": cik,
            "accession_number": accession_number,
            "issuer_name": issuer,
            "cusip": cusip,  # backend only — never display publicly
            "value_dollars": value_dollars,
            "shares": shares,
            "investment_discretion": discretion,
            "voting_sole": voting_sole,
            "voting_shared": voting_shared,
            "parsed_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        print(f"[parser] Failed to parse position: {e}")
        return None


def process_filing(filing: dict) -> list[dict]:
    """
    Main entry point — takes a filing dict from monitor.py
    and returns all parsed positions.
    """
    index_url = filing.get("filing_url")
    cik = filing.get("cik")
    accession = filing.get("accession_number")

    if not index_url or not cik or not accession:
        print(f"[parser] Missing required fields in filing: {filing}")
        return []

    print(f"[parser] Processing: {filing.get('company_name')} | {accession}")

    xml_url = fetch_filing_index(index_url)
    if not xml_url:
        return []

    return parse_holdings(xml_url, cik, accession)


if __name__ == "__main__":
    # Test with a real filing from monitor
    from pipeline.monitor import fetch_latest_filings

    filings = fetch_latest_filings()
    if filings:
        # Test on first filing
        test_filing = filings[0]
        print(f"\nTesting parser on: {test_filing['company_name']}")
        positions = process_filing(test_filing)
        for p in positions[:5]:  # Show first 5 positions
            print(p)