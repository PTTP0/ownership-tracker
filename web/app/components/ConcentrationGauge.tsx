'use client'

import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis
} from 'recharts'

interface Props {
  value: number
  max?: number
  label: string
}

export default function ConcentrationGauge({ value, max = 100000, label }: Props) {
  const percentage = Math.min((value / max) * 100, 100)

  const data = [{ value: percentage }]

  const getColor = (pct: number) => {
    if (pct < 20) return '#22c55e'
    if (pct < 50) return '#ff8800'
    return '#ff4444'
  }

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ width: '200px', height: '200px', margin: '0 auto', position: 'relative' }}>
        <ResponsiveContainer>
          <RadialBarChart
            innerRadius="70%"
            outerRadius="100%"
            data={data}
            startAngle={180}
            endAngle={0}
          >
            <PolarAngleAxis
              type="number"
              domain={[0, 100]}
              angleAxisId={0}
              tick={false}
            />
            <RadialBar
              dataKey="value"
              cornerRadius={4}
              fill={getColor(percentage)}
              background={{ fill: '#222' }}
              angleAxisId={0}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '28px',
            fontWeight: '700',
            color: getColor(percentage)
          }}>
            {value.toLocaleString()}
          </div>
          <div style={{ fontSize: '11px', color: '#666', marginTop: '2px' }}>
            ΔMHHI
          </div>
        </div>
      </div>
      <div style={{ fontSize: '14px', color: '#888', marginTop: '8px' }}>{label}</div>
    </div>
  )
}