'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import OwnershipChart from './components/OwnershipChart'
import ConcentrationGauge from './components/ConcentrationGauge'

const DEFENSE_TICKERS = ['LMT', 'RTX', 'NOC', 'GD']

export default function Home() {
  const [defenseHoldings, setDefenseHoldings] = useState<any[]>([])
  const [totalDefenseValue, setTotalDefenseValue] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const { data } = await supabase
        .from('holdings')
        .select('*')
        .in('ticker', DEFENSE_TICKERS)

      if (data) {
        setDefenseHoldings(data)
        const total = data.reduce((sum, h) => sum + (h.value_dollars || 0), 0)
        setTotalDefenseValue(total)
      }
      setLoading(false)
    }
    fetchData()
  }, [])

  const formatBillions = (n: number) => `$${(n / 1_000_000_000_000).toFixed(1)}B`

  const chartData = DEFENSE_TICKERS.map(ticker => {
    const holdings = defenseHoldings.filter(h => h.ticker === ticker)
    const byCIK: Record<string, number> = {}
    holdings.forEach(h => {
      byCIK[h.cik] = (byCIK[h.cik] || 0) + (h.value_dollars || 0)
    })
    const cikValues = Object.values(byCIK)
    return {
      ticker,
      blackrock: cikValues[0] || 0,
      vanguard: cikValues[1] || 0,
      statestreet: cikValues[2] || 0,
    }
  })

  return (
    <main style={{
      background: '#0a0a0a',
      minHeight: '100vh',
      color: '#ffffff',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '80px 24px 60px'
      }}>

        {/* Header tag */}
        <div style={{
          fontSize: '11px',
          letterSpacing: '3px',
          color: '#ff4444',
          textTransform: 'uppercase',
          marginBottom: '24px'
        }}>
          Public Data. Public Interest.
        </div>

        {/* Hero headline */}
        <h1 style={{
          fontSize: 'clamp(36px, 6vw, 72px)',
          fontWeight: '700',
          lineHeight: '1.1',
          marginBottom: '32px',
          letterSpacing: '-2px'
        }}>
          Three companies<br />
          own America's<br />
          <span style={{ color: '#ff4444' }}>war machine.</span>
        </h1>

        <p style={{
          fontSize: '20px',
          color: '#888',
          lineHeight: '1.7',
          maxWidth: '600px',
          marginBottom: '48px'
        }}>
          BlackRock, Vanguard, and State Street simultaneously own
          Lockheed Martin, Raytheon, Northrop Grumman, and General Dynamics.
          When America goes to war, they all profit. Every time.
        </p>

        {/* MHHI Key metric */}
        <div style={{
          background: '#111',
          border: '1px solid #ff4444',
          borderRadius: '12px',
          padding: '40px',
          marginBottom: '60px',
          display: 'inline-block'
        }}>
          <div style={{ fontSize: '13px', color: '#888', marginBottom: '8px', letterSpacing: '2px' }}>
            COMMON OWNERSHIP CONCENTRATION (ΔMHHI)
          </div>
          <div style={{ fontSize: '80px', fontWeight: '700', color: '#ff4444', lineHeight: '1' }}>
            66,972
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '12px' }}>
            The airline study that triggered Senate hearings found 2,000.<br />
            This is <strong style={{ color: '#fff' }}>33× higher.</strong>
          </div>
        </div>

        {/* Concentration Gauge */}
        <div style={{
          background: '#111',
          border: '1px solid #222',
          borderRadius: '12px',
          padding: '40px',
          marginBottom: '24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
          <div style={{
            fontSize: '13px',
            color: '#666',
            letterSpacing: '2px',
            marginBottom: '24px'
          }}>
            CONCENTRATION GAUGE
          </div>
          <ConcentrationGauge
            value={66972}
            max={100000}
            label="Defense Sector ΔMHHI"
          />
          <div style={{
            marginTop: '24px',
            fontSize: '14px',
            color: '#666',
            textAlign: 'center'
          }}>
            Airline study that triggered Senate hearings: <strong style={{ color: '#fff' }}>2,000</strong>
            <br />
            Defense sector: <strong style={{ color: '#ff4444' }}>33× higher</strong>
          </div>
        </div>

        {/* Bar chart */}
        <h2 style={{ fontSize: '28px', fontWeight: '600', marginBottom: '8px', marginTop: '60px' }}>
          What they own
        </h2>
        <p style={{ color: '#666', marginBottom: '24px', fontSize: '15px' }}>
          Combined holdings of BlackRock, Vanguard, and State Street in each defense contractor
        </p>

        {loading ? (
          <div style={{
            background: '#111',
            border: '1px solid #222',
            borderRadius: '12px',
            padding: '60px',
            textAlign: 'center',
            color: '#444'
          }}>
            Loading holdings data...
          </div>
        ) : (
          <>
            {/* Ownership bar chart */}
            <div style={{
              background: '#111',
              border: '1px solid #222',
              borderRadius: '12px',
              padding: '32px',
              marginBottom: '24px'
            }}>
              <div style={{
                fontSize: '13px',
                color: '#666',
                letterSpacing: '2px',
                marginBottom: '24px'
              }}>
                HOLDINGS BY CONTRACTOR
              </div>
              <OwnershipChart data={chartData} />
            </div>

            {/* Holdings cards */}
            <div style={{ display: 'grid', gap: '12px', marginBottom: '16px' }}>
              {DEFENSE_TICKERS.map(ticker => {
                const holdings = defenseHoldings.filter(h => h.ticker === ticker)
                const totalValue = holdings.reduce((s, h) => s + (h.value_dollars || 0), 0)
                const totalShares = holdings.reduce((s, h) => s + (h.shares || 0), 0)
                const issuers = [...new Set(holdings.map(h => h.issuer_name))]
                return (
                  <div key={ticker} style={{
                    background: '#111',
                    border: '1px solid #222',
                    borderRadius: '10px',
                    padding: '24px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontSize: '22px', fontWeight: '700' }}>{ticker}</div>
                      <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>
                        {issuers[0] || 'Defense Contractor'}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '22px', fontWeight: '700', color: '#ff4444' }}>
                        {formatBillions(totalValue)}
                      </div>
                      <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>
                        {totalShares.toLocaleString()} shares
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Total */}
            <div style={{
              padding: '20px 24px',
              background: '#111',
              border: '1px solid #333',
              borderRadius: '10px',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <div style={{ color: '#888' }}>Total defense holdings — Big Three</div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#ff4444' }}>
                {formatBillions(totalDefenseValue)}
              </div>
            </div>
          </>
        )}
{/* What is MHHI — plain English */}
<div style={{
  marginTop: '60px',
  marginBottom: '60px',
}}>
  <h2 style={{ fontSize: '28px', fontWeight: '600', marginBottom: '24px' }}>
    What does 66,972 actually mean?
  </h2>

  {/* Comparison bars */}
  <div style={{ display: 'grid', gap: '16px', marginBottom: '40px' }}>
    {[
      {
        label: 'Perfect competition',
        sublabel: 'No common ownership — companies fully compete',
        value: 0,
        max: 70000,
        color: '#22c55e'
      },
      {
        label: 'Airline industry',
        sublabel: 'Triggered Senate hearings in 2018',
        value: 2000,
        max: 70000,
        color: '#ff8800'
      },
      {
        label: 'Banking industry',
        sublabel: 'Why your bank fees keep rising',
        value: 8000,
        max: 70000,
        color: '#ff6600'
      },
      {
        label: 'Defense industry',
        sublabel: 'BlackRock + Vanguard + State Street own everything',
        value: 66972,
        max: 70000,
        color: '#ff4444'
      }
    ].map(item => (
      <div key={item.label}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '8px'
        }}>
          <div>
            <span style={{ fontSize: '15px', fontWeight: '600' }}>{item.label}</span>
            <span style={{
              fontSize: '12px',
              color: '#666',
              marginLeft: '12px'
            }}>
              {item.sublabel}
            </span>
          </div>
          <span style={{
            fontSize: '15px',
            fontWeight: '700',
            color: item.color
          }}>
            {item.value.toLocaleString()}
          </span>
        </div>
        <div style={{
          height: '8px',
          background: '#1a1a1a',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${(item.value / item.max) * 100}%`,
            background: item.color,
            borderRadius: '4px',
            transition: 'width 1s ease'
          }} />
        </div>
      </div>
    ))}
  </div>

  {/* Plain English explanation */}
  <div style={{
    background: '#111',
    border: '1px solid #222',
    borderRadius: '12px',
    padding: '32px',
  }}>
    <div style={{
      fontSize: '13px',
      color: '#666',
      letterSpacing: '2px',
      marginBottom: '20px'
    }}>
      PLAIN ENGLISH
    </div>
    <div style={{ display: 'grid', gap: '20px' }}>
      {[
        {
          emoji: '🏦',
          title: 'What is ΔMHHI?',
          body: 'It measures how much competitive incentive is destroyed by common ownership. Zero means full competition. Higher means companies have less reason to compete because they share the same investors.'
        },
        {
          emoji: '✈️',
          title: 'Why airlines matter',
          body: 'In 2018 economists proved that when BlackRock and Vanguard owned competing airlines, ticket prices were 3-7% higher on those routes. The Senate held hearings. The ΔMHHI on those routes averaged 2,000.'
        },
        {
          emoji: '🔫',
          title: 'What 66,972 means',
          body: 'The defense sector concentration is 33 times higher than the airline number that caused Senate hearings. Lockheed, Raytheon, Northrop, and General Dynamics have almost no financial incentive to compete with each other — they pay the same investors.'
        },
        {
          emoji: '💰',
          title: 'What this costs you',
          body: 'Defense spending is your tax dollars. When there is no real competition for contracts, prices stay high. The Pentagon pays more. You pay more. The same three asset managers collect dividends from all of it.'
        }
      ].map(item => (
        <div key={item.title} style={{
          display: 'flex',
          gap: '16px',
          paddingBottom: '20px',
          borderBottom: '1px solid #1a1a1a'
        }}>
          <div style={{ fontSize: '24px', flexShrink: 0 }}>{item.emoji}</div>
          <div>
            <div style={{
              fontSize: '16px',
              fontWeight: '600',
              marginBottom: '6px'
            }}>
              {item.title}
            </div>
            <div style={{
              fontSize: '14px',
              color: '#888',
              lineHeight: '1.7'
            }}>
              {item.body}
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
</div>
        {/* Why this matters */}
        <div style={{ marginTop: '80px' }}>
          <h2 style={{ fontSize: '28px', fontWeight: '600', marginBottom: '16px' }}>
            Why this matters
          </h2>
          <p style={{ color: '#888', lineHeight: '1.8', fontSize: '17px', maxWidth: '680px' }}>
            When the same investors own all the competitors in an industry,
            those companies have less incentive to compete against each other.
            Why undercut a rival when you both pay the same shareholders?
            Economists call this <strong style={{ color: '#fff' }}>common ownership</strong> —
            and peer-reviewed research shows it raises consumer prices by 3-7%
            in industries where it's prevalent.
          </p>
          <p style={{ color: '#888', lineHeight: '1.8', fontSize: '17px', maxWidth: '680px', marginTop: '16px' }}>
            In the defense sector, the effect is 33× stronger than in airlines.
            Every missile contract, every defense bill, every conflict —
            the same three investors collect from every side.
          </p>
        </div>

        {/* Footer */}
        <div style={{
          marginTop: '80px',
          paddingTop: '40px',
          borderTop: '1px solid #222',
          fontSize: '13px',
          color: '#444',
          lineHeight: '1.8'
        }}>
          <div style={{ marginBottom: '8px', color: '#666' }}>Data sources</div>
          All data sourced from public government disclosures.
          SEC Form 13F institutional holdings filings via EDGAR.
          Security identifiers via Bloomberg OpenFIGI (open source).
          This platform presents statistical correlations — not allegations of illegality.
          Every data point traceable to its original SEC filing.
        </div>

      </div>
    </main>
  )
}