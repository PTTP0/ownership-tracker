# Ownership Tracker

A public transparency platform visualizing institutional common ownership 
concentration across US public companies using SEC 13F filings.

## What This Does

Large asset managers like BlackRock, Vanguard, and State Street simultaneously 
own significant stakes in competing companies across every major industry sector. 
Economic research suggests this common ownership may reduce competitive incentives 
between firms, potentially leading to higher prices for consumers.

This platform makes that ownership data visible to everyone — for free.

## Data Sources

All data is sourced from public government disclosures:

- **SEC EDGAR Form 13F** — institutional holdings filings (public domain)
- **Bloomberg OpenFIGI** — open source security identifiers
- **BLS Public Data API** — consumer and producer price indices
- **OpenSecrets** — lobbying expenditures and PAC contributions
- **Capitol Trades** — congressional stock disclosures (STOCK Act)

## Methodology

### MHHI Delta

This platform computes the Modified Herfindahl-Hirschman Index Delta (ΔMHHI), 
originally formalized by O'Brien and Salop (2000), to quantify the concentration 
premium added by overlapping institutional ownership.

The metric was used by Azar, Schmalz & Tecu (Journal of Finance, 2018) to 
demonstrate that common ownership was associated with 3-7% higher airline ticket 
prices on routes where institutional overlap was highest.

### Computation

For each industry sector:
1. Build voting (V) and financial interest (F) matrices from 13F holdings
2. Compute relative control weight matrix Θ = (VᵀF) / diag(VᵀV)
3. Calculate modified concentration matrix M = diag(s) · Θ · diag(s)
4. ΔMHHI = sum of off-diagonal elements of M × 10,000

Full mathematical derivation available in `pipeline/mhhi.py`.

## Legal Disclaimer

All visualizations represent statistical correlations derived from public 
government disclosures. This platform does not allege collusion, price-fixing, 
or illegal anticompetitive behavior.

Mere common ownership is legally protected under Section 7 of the Clayton Act 
for investments made "solely for investment" purposes without active coordination.

Data is provided solely for educational, academic, and transparency purposes 
and is not intended for active investment decisions.

Every data point is traceable to its original SEC EDGAR source filing.

## Stack

- **Backend:** Python / FastAPI
- **Database:** Supabase (PostgreSQL)
- **Frontend:** Next.js / Vercel
- **Pipeline:** GitHub Actions (automated quarterly ingestion)

## License

GNU GPL v3 — any derivative work must remain open source.

## Contributing

See `db/seed_data/` for mock data to run locally without hitting EDGAR 
rate limits. All pipeline modules are fully typed and independently testable.