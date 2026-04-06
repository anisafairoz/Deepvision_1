import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

const API_BASE = 'http://localhost:8000/api';

function Analytics() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Polling every 5 sec
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/analytics`);
      const data = await res.json();
      setMetrics(data);
    } catch (err) {
      console.error("Failed fetching analytics:", err);
    }
  };

  if (!metrics) {
    return <div className="card" style={{padding: '40px', textAlign: 'center', color: 'var(--text-secondary)'}}>Initializing Intelligence Metrics...</div>;
  }

  const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];

  // Mock data for FPS stability graph
  const fpsData = Array.from({ length: 20 }).map((_, i) => ({
    time: i,
    value: 30 + Math.random() * 5 - 2.5
  }));

  return (
    <div>
      <div className="card">
        <h2 className="card-title">Key Performance Indicators</h2>
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          
          <div style={{ flex: 1, minWidth: '200px', padding: '20px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>Total Detections</p>
             <h3 style={{ fontSize: '2.5rem', margin: 0, color: 'var(--text-primary)' }}>{metrics.total}</h3>
          </div>

          <div style={{ flex: 1, minWidth: '200px', padding: '20px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>Model Confidence</p>
             <h3 style={{ fontSize: '2.5rem', margin: 0, color: 'var(--success)' }}>{metrics.confidence}% <span style={{fontSize: '1rem'}}>🎯</span></h3>
          </div>

          <div style={{ flex: 1, minWidth: '200px', padding: '20px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>Risk Alerts</p>
             <h3 style={{ fontSize: '2.5rem', margin: 0, color: 'var(--danger)' }}>{metrics.intrusions} <span style={{fontSize: '1rem'}}>🚨</span></h3>
          </div>

          <div style={{ flex: 1, minWidth: '200px', padding: '20px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
             <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>Pipeline FPS</p>
             <h3 style={{ fontSize: '2.5rem', margin: 0, color: '#A855F7' }}>{metrics.fps} <span style={{fontSize: '1rem'}}>⚡</span></h3>
          </div>

        </div>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        <div className="card" style={{ flex: 1, minWidth: '300px' }}>
          <h2 className="card-title">Category Distribution</h2>
          <div style={{ height: '280px' }}>
            {metrics.distribution && metrics.distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={metrics.distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {metrics.distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'var(--surface-color)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }}
                    itemStyle={{ color: 'var(--text-primary)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
               <div style={{height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)'}}>
                 No class distribution data
               </div>
            )}
          </div>
        </div>

        <div className="card" style={{ flex: 1, minWidth: '300px' }}>
          <h2 className="card-title">FPS Stability Network</h2>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={fpsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="time" hide />
                <YAxis domain={['dataMin - 5', 'dataMax + 5']} stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'var(--surface-color)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }}
                />
                <Line type="monotone" dataKey="value" stroke="#A855F7" strokeWidth={3} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
