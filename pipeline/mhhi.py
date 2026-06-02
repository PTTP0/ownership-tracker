import numpy as np
from scipy.sparse import csr_matrix
from typing import Optional
from db.client import supabase


def get_sector_holdings(tickers: list[str]) -> dict:
    """
    Pull holdings data from Supabase for a list of tickers.
    Returns dict structured for MHHI computation.
    """
    try:
        result = supabase.table("holdings").select(
            "cik, ticker, shares, voting_sole, voting_shared, value_dollars"
        ).in_("ticker", tickers).execute()
        return result.data
    except Exception as e:
        print(f"[mhhi] Failed to fetch holdings: {e}")
        return []


def build_matrices(holdings: list[dict], tickers: list[str]) -> tuple:
    """
    Build voting (V) and financial (F) matrices from holdings data.
    
    V: M x N matrix — voting control of investor i in firm j
    F: M x N matrix — financial interest of investor i in firm k
    s: N x 1 vector — market shares of each firm
    
    Returns (V, F, s, investors, firms)
    """
    # Get unique investors and firms
    investors = list(set(h["cik"] for h in holdings))
    firms = tickers

    M = len(investors)  # number of investors
    N = len(firms)      # number of firms

    investor_idx = {inv: i for i, inv in enumerate(investors)}
    firm_idx = {firm: j for j, firm in enumerate(firms)}

    # Initialize sparse matrices
    V_data, V_row, V_col = [], [], []
    F_data, F_row, F_col = [], [], []

    # Track total shares per firm for normalization
    total_shares = {firm: 0 for firm in firms}
    for h in holdings:
        ticker = h.get("ticker")
        if ticker in firm_idx:
            total_shares[ticker] += h.get("shares", 0) or 0

    for h in holdings:
        ticker = h.get("ticker")
        cik = h.get("cik")
        shares = h.get("shares", 0) or 0
        voting = h.get("voting_sole", 0) or 0

        if ticker not in firm_idx or cik not in investor_idx:
            continue

        i = investor_idx[cik]
        j = firm_idx[ticker]
        total = total_shares[ticker]

        if total > 0:
            # Financial interest = share fraction
            financial_pct = shares / total
            F_data.append(financial_pct)
            F_row.append(i)
            F_col.append(j)

            # Voting control = voting share fraction
            voting_pct = voting / total if voting > 0 else financial_pct
            V_data.append(voting_pct)
            V_row.append(i)
            V_col.append(j)

    V = csr_matrix((V_data, (V_row, V_col)), shape=(M, N))
    F = csr_matrix((F_data, (F_row, F_col)), shape=(M, N))

    # Market shares — equal weight placeholder
    # In production replace with revenue based shares from 10-K
    s = np.ones(N) / N

    return V, F, s, investors, firms


def compute_mhhi_delta(
    market_shares: np.ndarray,
    voting_matrix: csr_matrix,
    financial_matrix: csr_matrix
) -> tuple[float, float, float]:
    """
    Compute HHI, MHHI, and MHHI Delta using sparse matrix algebra.
    
    Returns (hhi, mhhi, mhhi_delta) all scaled to 10,000.
    """
    N = len(market_shares)

    if N == 0:
        return 0.0, 0.0, 0.0

    # Numerator: V^T * F — N x N matrix
    numerator = voting_matrix.T.dot(financial_matrix)

    # Denominator: diagonal of V^T * V
    denominator_vector = np.array(
        voting_matrix.multiply(voting_matrix).sum(axis=0)
    ).ravel()

    # Avoid division by zero
    denominator_vector[denominator_vector == 0] = 1.0

    # Theta matrix — relative control weights
    num_dense = numerator.toarray()
    theta = num_dense / denominator_vector[:, np.newaxis]

    # Modified concentration matrix: diag(s) * theta * diag(s)
    S = np.diag(market_shares)
    mod_matrix = S.dot(theta).dot(S)

    # HHI = trace, MHHI = sum of all elements
    hhi = float(np.trace(mod_matrix)) * 10000.0
    mhhi = float(np.sum(mod_matrix)) * 10000.0
    mhhi_delta = max(0.0, mhhi - hhi)

    return round(hhi, 2), round(mhhi, 2), round(mhhi_delta, 2)


def analyze_sector(sector_name: str, tickers: list[str]) -> dict:
    """
    Full MHHI analysis for a sector.
    Takes sector name and list of tickers.
    Returns concentration scores.
    """
    print(f"\n[mhhi] Analyzing sector: {sector_name}")
    print(f"[mhhi] Firms: {tickers}")

    holdings = get_sector_holdings(tickers)
    if not holdings:
        print(f"[mhhi] No holdings data found for {sector_name}")
        return {}

    print(f"[mhhi] Found {len(holdings)} holding records")

    V, F, s, investors, firms = build_matrices(holdings, tickers)

    print(f"[mhhi] Matrix dimensions: {len(investors)} investors x {len(firms)} firms")

    hhi, mhhi, mhhi_delta = compute_mhhi_delta(s, V, F)

    result = {
        "sector": sector_name,
        "firms": firms,
        "num_investors": len(investors),
        "num_holdings": len(holdings),
        "hhi": hhi,
        "mhhi": mhhi,
        "mhhi_delta": mhhi_delta,
        "interpretation": interpret_delta(mhhi_delta)
    }

    print(f"[mhhi] HHI:        {hhi:,.0f}")
    print(f"[mhhi] MHHI:       {mhhi:,.0f}")
    print(f"[mhhi] ΔMHHI:      {mhhi_delta:,.0f}")
    print(f"[mhhi] {result['interpretation']}")

    return result


def interpret_delta(mhhi_delta: float) -> str:
    """
    Plain English interpretation of MHHI Delta score.
    """
    if mhhi_delta < 200:
        return "Low common ownership concentration"
    elif mhhi_delta < 500:
        return "Moderate common ownership — worth monitoring"
    elif mhhi_delta < 1000:
        return "Significant common ownership — competitive concern"
    elif mhhi_delta < 2000:
        return "High common ownership — strong anticompetitive signal"
    else:
        return "Extreme common ownership — matches airline study levels"


if __name__ == "__main__":
    # Install scipy if needed: pip3 install scipy numpy
    
    # Test with defense sector — the hero story
    defense = analyze_sector(
        "Defense",
        ["LMT", "RTX", "NOC", "GD"]  # Lockheed, Raytheon, Northrop, General Dynamics
    )

    # Test with any tickers you have in your database
    # Check what's actually in there first
    from db.client import supabase
    sample = supabase.table("holdings").select(
        "ticker"
    ).not_.is_("ticker", "null").limit(20).execute()
    
    tickers_in_db = list(set(
        r["ticker"] for r in sample.data if r.get("ticker")
    ))
    print(f"\n[mhhi] Tickers currently in DB: {tickers_in_db}")

    if tickers_in_db:
        sample_sector = analyze_sector("Sample Sector", tickers_in_db[:5])