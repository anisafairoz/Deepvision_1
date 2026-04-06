import React from 'react';

function MonitorView({ isRunning }) {
  return (
    <div className="card">
      <h2 className="card-title">Live Sensor Feed</h2>
      
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#000',
        borderRadius: '8px',
        overflow: 'hidden',
        minHeight: '400px',
        border: '1px solid var(--border-color)',
        position: 'relative'
      }}>
        {isRunning ? (
          <img 
            src="http://localhost:8000/api/video_feed" 
            alt="Live Feed" 
            style={{ width: '100%', height: 'auto', display: 'block' }} 
          />
        ) : (
          <div style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>📷</div>
            <p>System is currently in standby mode.</p>
            <p style={{ fontSize: '0.85rem', marginTop: '8px', opacity: 0.7 }}>Click "Start Scan" to initialize sensors.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default MonitorView;
