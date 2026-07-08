import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { ClipboardList, Shield, MapPin, Eye, Clock, Search, ShieldAlert } from 'lucide-react';
import toast from 'react-hot-toast';

export const History: React.FC = () => {
  const [detections, setDetections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get(`/detections?page=${page}&limit=10`);
        setDetections(response.data.detections);
        setTotal(response.data.total);
      } catch (err) {
        toast.error('Failed to load surveillance records.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [page]);

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="border-b border-gray-800 pb-4">
        <h2 className="text-xl font-bold tracking-wider text-white uppercase font-mono">AUDITING INTELLIGENCE REGISTRY</h2>
        <p className="text-xs text-gray-500 font-mono uppercase">SECURE VEHICLE LOGS & SURVEILLANCE PARITY DATA</p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
          <div className="w-10 h-10 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin shadow-glow-cyan"></div>
          <span className="font-mono text-[10px] text-gray-500 tracking-widest uppercase">PULLING ENCRYPTED AUDIT STRIPS...</span>
        </div>
      ) : (
        <div className="glass-panel p-6 border border-gray-800 space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2 font-mono text-xs text-cyan-400">
              <ClipboardList className="w-4.5 h-4.5" />
              <span className="font-bold uppercase">CCTV STREAM DISPATCH RECORDS</span>
            </div>
            <span className="text-[10px] font-mono text-gray-500 uppercase">{total} TOTAL ENTRIES LOGGED</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500">
                  <th className="py-3 uppercase tracking-wider">PARSE ID</th>
                  <th className="py-3 uppercase tracking-wider">CCTV STREAM</th>
                  <th className="py-3 uppercase tracking-wider">NODE LOCATION</th>
                  <th className="py-3 uppercase tracking-wider">RECORDED TIMESTAMP</th>
                  <th className="py-3 uppercase tracking-wider">VEHICLES PLOTTED</th>
                  <th className="py-3 uppercase tracking-wider">MAX RISK RATING</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-900/50">
                {detections.map((det) => (
                  <tr key={det._id} className="hover:bg-gray-900/25 transition-colors duration-200">
                    <td className="py-4 text-gray-500 font-mono text-[10px]">#{det._id.substring(18, 24).toUpperCase()}</td>
                    <td className="py-4 text-cyan-300 font-semibold">{det.video_name}</td>
                    <td className="py-4 text-gray-300">
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-3.5 h-3.5 text-gray-600" />
                        <span>{det.location}</span>
                      </div>
                    </td>
                    <td className="py-4 text-gray-400">{new Date(det.upload_time).toLocaleString()}</td>
                    <td className="py-4 text-cyan-400 font-bold">{det.vehicles_count || 1}</td>
                    <td className="py-4">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                        det.max_risk_level === 'Critical' ? 'bg-red-500/10 text-red-500 border border-red-950 shadow-glow-red animate-pulse' :
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

          {/* Pagination controls */}
          <div className="flex justify-between items-center pt-4 border-t border-gray-900 font-mono text-xs">
            <button
              onClick={() => setPage(p => Math.max(p - 1, 1))}
              disabled={page === 1}
              className="px-3.5 py-1.5 border border-gray-800 rounded bg-gray-950 text-gray-400 hover:text-white disabled:opacity-30 disabled:hover:text-gray-400 transition-all duration-200"
            >
              PREVIOUS
            </button>
            <span className="text-gray-500">PAGE {page} OF {Math.ceil(total / 10) || 1}</span>
            <button
              onClick={() => setPage(p => (p * 10 < total ? p + 1 : p))}
              disabled={page * 10 >= total}
              className="px-3.5 py-1.5 border border-gray-800 rounded bg-gray-950 text-gray-400 hover:text-white disabled:opacity-30 disabled:hover:text-gray-400 transition-all duration-200"
            >
              NEXT
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
