import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { 
  ShieldAlert, Play, AlertTriangle, Eye, 
  MapPin, CheckCircle, Clock, TrendingUp, AlertCircle
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.get('/dashboard/stats');
        setData(response.data);
      } catch (err: any) {
        toast.error('Failed to update control room statistics.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
    // Poll stats every 30 seconds for live cybersecurity dashboard feel
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] space-y-4">
        <div className="w-10 h-10 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin shadow-glow-cyan"></div>
        <span className="font-mono text-[10px] text-gray-500 tracking-widest uppercase">SYNCING COMMAND DATABASES...</span>
      </div>
    );
  }

  const { stats, weekly_trend, risk_distribution, categories, recent_detections, recent_alerts, heatmap } = data;

  const COLORS = ['#10b981', '#eab308', '#ef4444', '#a855f7']; // Green, Yellow, Red, Purple

  return (
    <div className="space-y-6">
      
      {/* Top Intelligence Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-gray-800 pb-4 gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white uppercase font-mono">CONTROL ROOM FEED</h2>
          <p className="text-xs text-gray-500 font-mono uppercase">REAL-TIME CCTV INTELLIGENCE MATRIX // AP STATE COMMAND</p>
        </div>
        <div className="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping shadow-glow-green"></span>
          <span className="text-[10px] font-mono text-emerald-400 font-semibold tracking-wider">ALL DETECTORS ONLINE [ 100% ]</span>
        </div>
      </div>

      {/* Main Stats Counters Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        
        {/* Today's Uploads */}
        <div className="glass-panel p-4 border border-cyan-500/10 flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-mono text-gray-500 tracking-wider uppercase">TODAY'S UPLOADS</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-white font-mono tracking-tight">{stats.today_uploads}</h3>
            <p className="text-[9px] font-mono text-gray-500 mt-1 uppercase">CCTV stream clips</p>
          </div>
        </div>

        {/* Vehicles Detected */}
        <div className="glass-panel p-4 border border-cyan-500/10 flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-mono text-gray-500 tracking-wider uppercase">VEHICLES PLOTTED</span>
            <Eye className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-white font-mono tracking-tight">{stats.vehicles_detected}</h3>
            <p className="text-[9px] font-mono text-gray-500 mt-1 uppercase">Total crops resolved</p>
          </div>
        </div>

        {/* Cloned Vehicles */}
        <div className="glass-panel p-4 border border-rose-500/10 flex flex-col justify-between hover:border-rose-500/30 transition-all duration-300 bg-rose-950/5">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-mono text-rose-400 tracking-wider uppercase">CLONE ALERTS</span>
            <ShieldAlert className="w-4 h-4 text-rose-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]" />
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-rose-500 font-mono tracking-tight">{stats.cloned_vehicles}</h3>
            <p className="text-[9px] font-mono text-gray-500 mt-1 uppercase">Plate duplicates flagged</p>
          </div>
        </div>

        {/* High Risk Targets */}
        <div className="glass-panel p-4 border border-yellow-500/10 flex flex-col justify-between hover:border-yellow-500/30 transition-all duration-300 bg-yellow-950/5">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-mono text-yellow-400 tracking-wider uppercase">HIGH RISK PLATES</span>
            <AlertTriangle className="w-4 h-4 text-yellow-500" />
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-yellow-500 font-mono tracking-tight">{stats.high_risk_vehicles}</h3>
            <p className="text-[9px] font-mono text-gray-500 mt-1 uppercase">Critical intercept tasks</p>
          </div>
        </div>

        {/* Average Latency */}
        <div className="glass-panel p-4 border border-cyan-500/10 flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-mono text-gray-500 tracking-wider uppercase">AVG LATENCY</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-white font-mono tracking-tight">{stats.avg_processing_time}s</h3>
            <p className="text-[9px] font-mono text-gray-500 mt-1 uppercase">Compute parsing delay</p>
          </div>
        </div>

      </div>

      {/* Main Charts & Feeds Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Weekly Trend Area Chart */}
        <div className="lg:col-span-2 glass-panel p-5 border border-cyan-500/5 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold tracking-widest text-cyan-400 uppercase font-mono mb-4">WEEKLY SURVEILLANCE PLOT</h3>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weekly_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorUploads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={10} fontFamily="monospace" />
                <YAxis stroke="#6b7280" fontSize={10} fontFamily="monospace" />
                <Tooltip 
                  contentStyle={{ background: '#090d16', border: '1px solid rgba(6,182,212,0.3)', borderRadius: '6px' }}
                  labelStyle={{ color: '#9ca3af', fontSize: '11px', fontFamily: 'monospace' }}
                  itemStyle={{ color: '#06b6d4', fontSize: '12px', fontFamily: 'monospace' }}
                />
                <Area type="monotone" dataKey="uploads" stroke="#06b6d4" fillOpacity={1} fill="url(#colorUploads)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Level Pie Chart Breakdown */}
        <div className="glass-panel p-5 border border-cyan-500/5 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold tracking-widest text-cyan-400 uppercase font-mono mb-4">ALERTS THREAT CLASSIFICATION</h3>
          </div>
          
          <div className="h-48 w-full relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={risk_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {risk_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center Summary Text */}
            <div className="absolute text-center">
              <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest block">ALERTS</span>
              <span className="text-2xl font-bold font-mono text-white block">
                {risk_distribution.reduce((acc: number, cur: any) => acc + cur.value, 0)}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-4 border-t border-gray-900">
            {risk_distribution.map((item: any, index: number) => (
              <div key={item.name} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index] }}></span>
                <span className="text-gray-400">{item.name}:</span>
                <span className="text-white font-bold">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Checkpoint Hot Zones Map List & Live Alert Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recent Detections feed Table */}
        <div className="lg:col-span-2 glass-panel p-5 border border-cyan-500/5 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xs font-bold tracking-widest text-cyan-400 uppercase font-mono">LIVE DETECTION STREAM</h3>
            <span className="text-[9px] font-mono text-gray-500 uppercase">showing last 6 uploads</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500">
                  <th className="py-2.5 uppercase tracking-wider">CCTV CLIP</th>
                  <th className="py-2.5 uppercase tracking-wider">LOCATION</th>
                  <th className="py-2.5 uppercase tracking-wider">TIMESTAMP</th>
                  <th className="py-2.5 uppercase tracking-wider">VEHICLES</th>
                  <th className="py-2.5 uppercase tracking-wider">RISK THREAT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-900/50">
                {recent_detections.map((det: any) => (
                  <tr key={det._id} className="hover:bg-gray-900/20 transition-colors duration-200">
                    <td className="py-3 text-cyan-300 font-semibold">{det.video_name}</td>
                    <td className="py-3 text-gray-300 flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-gray-500" />
                      <span>{det.location}</span>
                    </td>
                    <td className="py-3 text-gray-500">{new Date(det.upload_time).toLocaleString().substring(11, 19)}</td>
                    <td className="py-3 text-cyan-400 font-bold">{det.vehicles?.length || 0}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                        det.max_risk_level === 'Critical' ? 'bg-red-500/10 text-red-500 border border-red-950 shadow-glow-red' :
                        det.max_risk_level === 'High' ? 'bg-orange-500/10 text-orange-400 border border-orange-950' :
                        det.max_risk_level === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-950' :
                        'bg-emerald-500/10 text-emerald-400 border border-emerald-950'
                      }`}>
                        {det.max_risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Intel Location Hotspot Panel */}
        <div className="glass-panel p-5 border border-cyan-500/5 flex flex-col justify-between">
          <div className="mb-4">
            <h3 className="text-xs font-bold tracking-widest text-cyan-400 uppercase font-mono">LOCATION RADAR MONITOR</h3>
            <p className="text-[9px] text-gray-500 font-mono uppercase mt-0.5">HIGH-VOLUME SUSPICIOUS CHECKPOINTS</p>
          </div>

          <div className="space-y-3.5 font-mono text-xs flex-1">
            {heatmap.map((node: any) => (
              <div key={node.name} className="flex justify-between items-center p-3 border border-gray-900 bg-gray-950/40 rounded-lg hover:border-gray-800 transition-all duration-300">
                <div className="space-y-1">
                  <span className="text-gray-300 font-semibold uppercase block">{node.name}</span>
                  <span className="text-[10px] text-gray-500 block">COORD: {node.lat.toFixed(4)}N, {node.lng.toFixed(4)}E</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-rose-500 font-black tracking-widest block bg-rose-500/10 px-2 py-0.5 rounded border border-rose-950">
                    +{node.intensity} ALERTS
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
