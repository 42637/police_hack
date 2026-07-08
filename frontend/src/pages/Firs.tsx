import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { FileText, Download, MapPin, ClipboardList } from 'lucide-react';
import toast from 'react-hot-toast';

export const Firs: React.FC = () => {
  const [firs, setFirs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchFirs = async () => {
    try {
      const response = await apiClient.get('/firs');
      setFirs(response.data);
    } catch (err: any) {
      toast.error('Failed to load registered FIR records.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFirs();
  }, []);

  const handleDownloadPDF = async (firId: string, firNum: string) => {
    try {
      const response = await apiClient.get(`/firs/${firId}/pdf`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `FIR_${firNum}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      toast.success(`Downloaded FIR PDF: ${firNum}`);
    } catch (err) {
      toast.error('Failed to download FIR PDF.');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] space-y-4">
        <div className="w-10 h-10 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin shadow-glow-cyan"></div>
        <span className="font-mono text-[10px] text-gray-500 tracking-widest uppercase">SYNCING COMMAND DATABASES...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-gray-800 pb-4 gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white uppercase font-mono">FIRST INFORMATION REPORTS (FIR)</h2>
          <p className="text-xs text-gray-500 font-mono uppercase">LEGAL CRIMINOLOGY AUDITING RECORD SECTION // PRAKASAM POLICE</p>
        </div>
        <div className="flex items-center space-x-2 bg-cyan-500/10 border border-cyan-500/20 px-3 py-1.5 rounded">
          <ClipboardList className="w-4 h-4 text-cyan-400" />
          <span className="text-[10px] font-mono text-cyan-400 font-semibold tracking-wider uppercase">
            {firs.length} CASE ENTRIES SIGNED
          </span>
        </div>
      </div>

      {/* Main Table Panel */}
      <div className="glass-panel p-5 border border-cyan-500/5 flex flex-col justify-between">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500">
                <th className="py-2.5 uppercase tracking-wider">FIR NUMBER</th>
                <th className="py-2.5 uppercase tracking-wider">CLONED VEHICLE</th>
                <th className="py-2.5 uppercase tracking-wider">REGISTERED OWNER</th>
                <th className="py-2.5 uppercase tracking-wider">OFFENSE LOCATION</th>
                <th className="py-2.5 uppercase tracking-wider">REPORTED DATE</th>
                <th className="py-2.5 uppercase tracking-wider">RISK THREAT</th>
                <th className="py-2.5 uppercase tracking-wider text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-900/50">
              {firs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-500 uppercase tracking-widest text-[10px]">
                    No official FIR reports registered yet
                  </td>
                </tr>
              ) : (
                firs.map((fir: any) => (
                  <tr key={fir._id} className="hover:bg-gray-900/20 transition-colors duration-200">
                    <td className="py-3 text-cyan-300 font-bold flex items-center space-x-1.5">
                      <FileText className="w-3.5 h-3.5 text-cyan-500" />
                      <span>{fir.fir_number}</span>
                    </td>
                    <td className="py-3 text-white font-mono">
                      <span className="font-bold text-cyan-400 mr-2">{fir.registration_number}</span>
                      <span className="text-[10px] text-gray-500 uppercase">({fir.vehicle_color} {fir.vehicle_brand} {fir.vehicle_model})</span>
                    </td>
                    <td className="py-3 text-gray-300">{fir.owner_name}</td>
                    <td className="py-3 text-gray-300 flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-gray-500" />
                      <span>{fir.location}</span>
                    </td>
                    <td className="py-3 text-gray-500">{new Date(fir.reported_date).toLocaleString()}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                        fir.risk_level === 'Critical' ? 'bg-red-500/10 text-red-500 border border-red-950 shadow-glow-red' :
                        fir.risk_level === 'High' ? 'bg-orange-500/10 text-orange-400 border border-orange-950' :
                        fir.risk_level === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-950' :
                        'bg-emerald-500/10 text-emerald-400 border border-emerald-950'
                      }`}>
                        {fir.risk_level}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleDownloadPDF(fir._id, fir.fir_number)}
                        className="bg-cyan-500 hover:bg-cyan-400 text-gray-950 px-2.5 py-1 rounded text-[10px] font-bold tracking-wider uppercase transition-all duration-300 inline-flex items-center space-x-1 shadow-glow-cyan/20"
                      >
                        <Download className="w-3 h-3" />
                        <span>Download PDF</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
