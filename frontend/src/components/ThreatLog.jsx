import React, { useState, useEffect } from 'react';
import { formatDistanceToNow, parseISO, subHours, subDays, isAfter, isBefore } from 'date-fns';

const API_BASE = 'http://localhost:8000/api';

const WEAPON_CLASSES = [
  "pistol", "handgun", "revolver", "rifle", "assault rifle", 
  "shotgun", "sniper", "knife", "machete", "sword", "dagger", 
  "grenade", "pipe bomb", "rocket launcher", "baseball bat", 
  "crowbar", "brass knuckles"
];

function ThreatLog() {
  const [logs, setLogs] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [filterType, setFilterType] = useState('All');
  const [timeFilter, setTimeFilter] = useState('All History');
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');

  useEffect(() => {
    fetchLogs();
    fetchSnapshots();
    const interval = setInterval(() => {
      fetchLogs();
      fetchSnapshots();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/logs?limit=50`);
      const data = await res.json();
      setLogs(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchSnapshots = async () => {
    try {
      const res = await fetch(`${API_BASE}/snapshots`);
      const data = await res.json();
      setSnapshots(data);
    } catch (err) {
      console.error(err);
    }
  };

  // Normalize all classes to lowercase to prevent duplicates ("Knife" vs "knife")
  const logClasses = logs.map(log => log.class_name.toLowerCase().replace('⚠️ warning: ', ''));
  const uniqueClasses = ['All', ...new Set([...logClasses, ...WEAPON_CLASSES])];

  const filteredLogs = logs.filter(log => {
      const normalizedClass = log.class_name.toLowerCase().replace('⚠️ warning: ', '');
      // 1. Time Filter
      const logDate = parseISO(log.timestamp);
      const now = new Date();
      let timePasses = true;

      if (timeFilter === 'Last 1 Hour') {
        timePasses = isAfter(logDate, subHours(now, 1));
      } else if (timeFilter === 'Last 24 Hours') {
        timePasses = isAfter(logDate, subDays(now, 1));
      } else if (timeFilter === 'Last 7 Days') {
        timePasses = isAfter(logDate, subDays(now, 7));
      } else if (timeFilter === 'Custom') {
        if (customStart) {
           timePasses = timePasses && isAfter(logDate, new Date(customStart));
        }
        if (customEnd) {
           timePasses = timePasses && isBefore(logDate, new Date(customEnd));
        }
      }

      if (!timePasses) return false;

      // 2. Class Filter
      if (filterType === 'All') return true;
      return normalizedClass.includes(filterType.toLowerCase());
  });

  return (
    <div>
      {/* Evidence Gallery */}
      <div className="card">
         <h2 className="card-title">Recent Forensic Evidence</h2>
         <div style={{ display: 'flex', gap: '16px', overflowX: 'auto', paddingBottom: '10px' }}>
            {snapshots.length > 0 ? snapshots.map((snap, idx) => (
               <img 
                 key={idx}
                 src={`http://localhost:8000${snap.url}`}
                 alt="Evidence"
                 style={{ height: '140px', borderRadius: '8px', border: '1px solid var(--border-color)', objectFit: 'cover' }}
               />
            )) : <p style={{color: 'var(--text-secondary)'}}>No recent evidence captured.</p>}
         </div>
      </div>

      {/* Audit Log Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
           <h2 className="card-title" style={{margin: 0}}>Audit History Archive</h2>
           <div className="input-group" style={{margin: 0, gap: '12px'}}>
             <select 
                className="input-field" 
                value={timeFilter} 
                onChange={(e) => setTimeFilter(e.target.value)}
             >
                <option value="All History">🕒 All History</option>
                <option value="Last 1 Hour">🕒 Last 1 Hour</option>
                <option value="Last 24 Hours">🕒 Last 24 Hours</option>
                <option value="Last 7 Days">🕒 Last 7 Days</option>
                <option value="Custom">⚙️ Custom Range</option>
             </select>

             {timeFilter === 'Custom' && (
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                   <input 
                      type="datetime-local" 
                      className="input-field" 
                      value={customStart} 
                      onChange={(e) => setCustomStart(e.target.value)} 
                      style={{ padding: '8px 12px' }}
                   />
                   <span style={{ color: 'var(--text-secondary)' }}>to</span>
                   <input 
                      type="datetime-local" 
                      className="input-field" 
                      value={customEnd} 
                      onChange={(e) => setCustomEnd(e.target.value)} 
                      style={{ padding: '8px 12px' }}
                   />
                </div>
             )}

             <select 
                className="input-field" 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
             >
                {uniqueClasses.map(cls => <option key={cls} value={cls}>{cls === 'All' ? '🎯 All Classes' : cls.toUpperCase()}</option>)}
             </select>
           </div>
        </div>
        
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Time Detected</th>
                <th>Object Class</th>
                <th>Confidence</th>
                <th>Zone Violation</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map(log => {
                const normalizedClass = log.class_name.toLowerCase().replace('⚠️ warning: ', '');
                const isWarning = WEAPON_CLASSES.includes(normalizedClass);
                return (
                  <tr key={log.id} className={isWarning ? 'row-weapon' : ''}>
                    <td>{formatDistanceToNow(parseISO(log.timestamp), { addSuffix: true })}</td>
                    <td>
                      {isWarning ? (
                        <span className="weapon-badge">⚠️ WARNING: {normalizedClass.toUpperCase()}</span>
                      ) : normalizedClass.toUpperCase()}
                    </td>
                    <td>{(log.confidence * 100).toFixed(1)}%</td>
                    <td>{log.is_intrusion ? '🛑 Intrusion' : '—'}</td>
                  </tr>
                );
              })}
              {filteredLogs.length === 0 && (
                <tr>
                   <td colSpan="4" style={{textAlign: 'center', color: 'var(--text-secondary)'}}>No records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ThreatLog;
