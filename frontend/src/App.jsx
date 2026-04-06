import { useState, useEffect } from 'react';
import { Shield, Activity, Video, Database, Play, Square } from 'lucide-react';
import MonitorView from './components/MonitorView';
import ThreatLog from './components/ThreatLog';
import Analytics from './components/Analytics';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [activeTab, setActiveTab] = useState('monitor');
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(res => res.json())
      .then(data => setIsRunning(data.running))
      .catch(err => console.error("Could not fetch status", err));
  }, []);

  const toggleSystem = async () => {
    try {
      const res = await fetch(`${API_BASE}/control?run=${!isRunning}`, { method: 'POST' });
      const data = await res.json();
      setIsRunning(data.status === 'running');
    } catch (err) {
      console.error("Failed to toggle system", err);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title">
            <Shield size={24} />
            DeepVision SOC
          </div>
        </div>
        
        <div className="nav-links">
          <div 
            className={`nav-item ${activeTab === 'monitor' ? 'active' : ''}`}
            onClick={() => setActiveTab('monitor')}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <Video size={18} /> Real-Time Monitor
            </div>
          </div>
          
          <div 
            className={`nav-item ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('logs')}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <Database size={18} /> Threat Archive
            </div>
          </div>
          
          <div 
            className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              <Activity size={18} /> Analytics Console
            </div>
          </div>
        </div>

        <div className="sidebar-controls">
          {isRunning ? (
             <button className="btn btn-danger" onClick={toggleSystem}>
               <Square size={18} /> STOP SYSTEM
             </button>
          ) : (
             <button className="btn btn-primary" onClick={toggleSystem}>
               <Play size={18} /> START SCAN
             </button>
          )}
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="topbar">
          <h1 style={{fontSize: '1.25rem', fontWeight: 600, margin: 0}}>
            {activeTab === 'monitor' && 'Live Surveillance Protocol'}
            {activeTab === 'logs' && 'Forensic Intelligence Archive'}
            {activeTab === 'analytics' && 'System Performance & Analytics'}
          </h1>
          <div className="status-badge">
            <div className={`status-dot ${isRunning ? 'active' : ''}`}></div>
            {isRunning ? 'System Online' : 'System Standby'}
          </div>
        </header>
        
        <div className="content-wrapper">
          {activeTab === 'monitor' && <MonitorView isRunning={isRunning} />}
          {activeTab === 'logs' && <ThreatLog />}
          {activeTab === 'analytics' && <Analytics />}
        </div>
      </main>
    </div>
  );
}

export default App;
