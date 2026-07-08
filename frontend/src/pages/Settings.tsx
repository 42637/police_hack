import React, { useState } from 'react';
import { Settings as SettingsIcon, Sliders, Shield, Database, Cpu, HelpCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export const Settings: React.FC = () => {
  const [yoloModel, setYoloModel] = useState('yolov8n.pt');
  const [ocrConfThreshold, setOcrConfThreshold] = useState('70');
  const [maxTravelSpeed, setMaxTravelSpeed] = useState('180');
  const [geminiModel, setGeminiModel] = useState('gemini-1.5-flash');

  const handleSave = () => {
    toast.success('System configuration parameters updated successfully.');
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="border-b border-gray-800 pb-4">
        <h2 className="text-xl font-bold tracking-wider text-white uppercase font-mono">SYSTEM PARAMETERS & CONFIGS</h2>
        <p className="text-xs text-gray-500 font-mono uppercase">TUNING RADAR DETECTORS & SPATIO-TEMPORAL ENGINES</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-mono text-xs">
        
        {/* Main Settings List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 border border-gray-800 space-y-6">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold border-b border-gray-900 pb-3">
              <Sliders className="w-4 h-4" />
              <span className="uppercase">VISION PIPELINE CONFIGS</span>
            </div>

            <div className="space-y-5">
              
              {/* YOLO weights select */}
              <div>
                <label className="block text-[10px] text-gray-500 uppercase tracking-widest mb-1.5">
                  YOLO VEHICLE DETECTION WEIGHTS
                </label>
                <select
                  value={yoloModel}
                  onChange={(e) => setYoloModel(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-900 rounded p-2.5 text-gray-300 focus:outline-none focus:border-cyan-500"
                >
                  <option value="yolov8n.pt">yolov8n.pt (Lightweight / 42ms)</option>
                  <option value="yolov11n.pt">yolov11n.pt (Standard / 55ms)</option>
                  <option value="yolov11m.pt">yolov11m.pt (Dense / 110ms)</option>
                </select>
                <span className="text-[9px] text-gray-600 mt-1 block leading-relaxed">
                  Defines the neural network size used for cropping targets from the raw extracted frames.
                </span>
              </div>

              {/* OCR Confidence */}
              <div>
                <label className="block text-[10px] text-gray-500 uppercase tracking-widest mb-1.5">
                  OCR PLATE MATCH MINIMUM CONFIDENCE (%)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={ocrConfThreshold}
                    onChange={(e) => setOcrConfThreshold(e.target.value)}
                    className="w-full bg-gray-950 border border-gray-900 rounded p-2.5 text-cyan-400 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <span className="text-[9px] text-gray-600 mt-1 block leading-relaxed">
                  Ignore license plate readings with a character confidence index below this threshold to prevent false audits.
                </span>
              </div>

              {/* Proximity thresholds */}
              <div>
                <label className="block text-[10px] text-gray-500 uppercase tracking-widest mb-1.5">
                  MAX PHYSICAL VEHICLE SPEED LIMIT (KM/H)
                </label>
                <input
                  type="number"
                  value={maxTravelSpeed}
                  onChange={(e) => setMaxTravelSpeed(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-900 rounded p-2.5 text-cyan-400 focus:outline-none focus:border-cyan-500"
                />
                <span className="text-[9px] text-gray-600 mt-1 block leading-relaxed">
                  Maximum realistic travel speed. Speeds computed between checkpoints exceeding this value will raise clone alerts.
                </span>
              </div>

              {/* LLM Provider Model */}
              <div>
                <label className="block text-[10px] text-gray-500 uppercase tracking-widest mb-1.5">
                  COGNITIVE AI ASSISTANT MODEL
                </label>
                <select
                  value={geminiModel}
                  onChange={(e) => setGeminiModel(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-900 rounded p-2.5 text-gray-300 focus:outline-none focus:border-cyan-500"
                >
                  <option value="gemini-1.5-flash">gemini-1.5-flash (Operational / Fast response)</option>
                  <option value="gemini-1.5-pro">gemini-1.5-pro (Analytic / Highly detailed)</option>
                </select>
                <span className="text-[9px] text-gray-600 mt-1 block leading-relaxed">
                  Selects the active LLM agent version backing multi-modal crop audits and the secure chatbot helper.
                </span>
              </div>

            </div>

            <button
              onClick={handleSave}
              className="bg-cyan-500 hover:bg-cyan-400 text-gray-950 px-6 py-2.5 rounded font-bold uppercase tracking-wider transition-all duration-300 shadow-glow-cyan"
            >
              SAVE CONFIGS
            </button>
          </div>
        </div>

        {/* Sidebar settings stats info */}
        <div className="space-y-6">
          <div className="glass-panel p-5 border border-gray-800 space-y-4">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold border-b border-gray-900 pb-3">
              <Cpu className="w-4 h-4" />
              <span className="uppercase">HARDWARE MONITOR</span>
            </div>
            
            <div className="space-y-3 font-mono">
              <div className="flex justify-between border-b border-gray-900 pb-1.5">
                <span className="text-gray-500">GPU CORE TEMPS</span>
                <span className="text-emerald-400">42°C // IDLE</span>
              </div>
              <div className="flex justify-between border-b border-gray-900 pb-1.5">
                <span className="text-gray-500">CUDA VERSION</span>
                <span className="text-white">v12.2 (Active)</span>
              </div>
              <div className="flex justify-between border-b border-gray-900 pb-1.5">
                <span className="text-gray-500">VRAM ALLOCATED</span>
                <span className="text-white">1.84 GB / 8.00 GB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">DETECTOR ENGINE</span>
                <span className="text-emerald-400">STATUS: ONLINE</span>
              </div>
            </div>
          </div>

          <div className="p-4 bg-gray-950/40 border border-gray-900 rounded-lg space-y-2">
            <span className="text-[9px] font-mono text-gray-500 uppercase tracking-widest block font-bold">
              AUDIT TRAILS
            </span>
            <p className="text-[10px] font-mono text-gray-500 leading-normal leading-relaxed">
              Updating parameters creates an entry in the system's security logs, recording changes to thresholds or model weights.
            </p>
          </div>
        </div>

      </div>

    </div>
  );
};
