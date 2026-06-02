'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'

interface Props {
  data: {
    ticker: string
    blackrock: number
    vanguard: number
    statestreet: number
  }[]
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '8px',
        padding: '12px 16px',
        fontSize: '13px'
      }}>
        <div style={{ color: '#fff', fontWeight: '600', marginBottom: '8px' }}>{label}</div>
        {payload.map((p: any) => (
          <div key={p.name} style={{ color: p.color, marginBottom: '4px' }}>
            {p.name}: ${(p.value / 1_000_000_000).toFixed(2)}B
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function OwnershipChart({ data }: Props) {
  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
          <XAxis
            dataKey="ticker"
            stroke="#444"
            tick={{ fill: '#888', fontSize: 13 }}
          />
          <YAxis
            stroke="#444"
            tick={{ fill: '#888', fontSize: 11 }}
            tickFormatter={(v) => `$${(v / 1_000_000_000).toFixed(0)}B`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="blackrock" name="BlackRock" fill="#ff4444" radius={[4, 4, 0, 0]} />
          <Bar dataKey="vanguard" name="Vanguard" fill="#ff8800" radius={[4, 4, 0, 0]} />
          <Bar dataKey="statestreet" name="State Street" fill="#ffcc00" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div style={{
        display: 'flex',
        gap: '24px',
        justifyContent: 'center',
        marginTop: '12px'
      }}>
        {[
          { color: '#ff4444', label: 'BlackRock' },
          { color: '#ff8800', label: 'Vanguard' },
          { color: '#ffcc00', label: 'State Street' }
        ].map(item => (
          <div key={item.label} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: '#888'
          }}>
            <div style={{
              width: '10px',
              height: '10px',
              borderRadius: '2px',
              background: item.color
            }} />
            {item.label}
          </div>
        ))}
      </div>
    </div>
  )
}