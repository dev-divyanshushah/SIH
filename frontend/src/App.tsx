import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Toaster } from 'sonner';

import { MissionControl } from '@/pages/MissionControl';
import { LiveMap } from '@/pages/LiveMap';
import { Fleet } from '@/pages/Fleet';
import { AIIntelligence } from '@/pages/AIIntelligence';
import { MissionPlanner } from '@/pages/MissionPlanner';
import { PersistentCoverage } from '@/pages/PersistentCoverage';
import { DigitalTwin } from '@/pages/DigitalTwin';
import { EventTimeline } from '@/pages/EventTimeline';
import { Analytics } from '@/pages/Analytics';
import { Settings } from '@/pages/Settings';

export function App() {
  // Connect WebSocket for real-time telemetry
  useWebSocket();

  return (
    <Router>
      <div className="flex h-screen w-screen overflow-hidden bg-[#080c14] text-slate-100 font-sans select-none">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex flex-col flex-1 h-full w-full overflow-hidden">
          {/* Top Header Bar */}
          <TopBar />

          {/* Page Router */}
          <main className="flex-1 h-full w-full overflow-hidden">
            <Routes>
              <Route path="/" element={<MissionControl />} />
              <Route path="/map" element={<LiveMap />} />
              <Route path="/fleet" element={<Fleet />} />
              <Route path="/ai" element={<AIIntelligence />} />
              <Route path="/planner" element={<MissionPlanner />} />
              <Route path="/coverage" element={<PersistentCoverage />} />
              <Route path="/twin" element={<DigitalTwin />} />
              <Route path="/timeline" element={<EventTimeline />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>

        {/* Global Toast Notification System */}
        <Toaster
          theme="dark"
          position="bottom-right"
          toastOptions={{
            style: {
              background: '#0d1421',
              border: '1px solid #1e293b',
              color: '#f1f5f9',
              fontSize: '12px',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
