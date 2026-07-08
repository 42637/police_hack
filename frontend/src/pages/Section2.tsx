import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiClient } from '../api/client';
import { 
  Upload, Search, CheckCircle, AlertTriangle, 
  Binary, FileVideo, Eye, Crosshair, ArrowRight
} from 'lucide-react';
import toast from 'react-hot-toast';

export const Section2: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [targetPlate, setTargetPlate] = useState('TS09EX5678');
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [selectedFrame, setSelectedFrame] = useState<string | null>(null);

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': [] },
    multiple: false
  });

  const handleSearch = async () => {
    if (!file) {
      toast.error('Please upload a CCTV video first.');
      return;
    }
    if (!targetPlate.trim()) {
      toast.error('Please enter a target number plate.');
      return;
    }

    setResult(null);
    setSelectedFrame(null);
    setProcessing(true);
    const toastId = toast.loading('Executing computer vision target search...');

    const formData = new FormData();
    formData.append('video', file);
    formData.append('target_plate', targetPlate.replace(" ", "").toUpperCase());

    try {
      const response = await apiClient.post('/detections/search-vehicle', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
      if (response.data.annotated_frame_path) {
        setSelectedFrame(response.data.annotated_frame_path);
      }
      toast.success(`Search completed. Found ${response.data.matches_found} matches.`, { id: toastId });
    } catch (err: any) {
      toast.error('Target search failed during vision processing.', { id: toastId });
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="border-b border-gray-800 pb-4">
        <h2 className="text-xl font-bold tracking-wider text-white uppercase font-mono">TARGET VEHICLE SEARCH</h2>
        <p className="text-xs text-gray-500 font-mono uppercase font-semibold">SECTION 2 // COMPUTER VISION PLOTTING CORE</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Left Search criteria panel */}
        <div className="space-y-6">
          <div className="glass-panel p-5 border border-cyan-500/5 space-y-4">
            <h3 className="text-xs font-bold tracking-widest text-cyan-400 uppercase font-mono">1. RUN CONFIGURATION</h3>
            
            {/* File Upload */}
            <div 
              {...getRootProps()} 
              className={`border border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-300 ${
                isDragActive ? 'border-cyan-400 bg-cyan-950/10' : 'border-gray-800 hover:border-cyan-500/40 bg-gray-950/40'
              }`}
            >
              <input {...getInputProps()} />
              <FileVideo className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              {file ? (
                <div className="text-xs font-mono">
                  <p className="text-cyan-300 font-bold uppercase">{file.name}</p>
                  <p className="text-gray-500 mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
              ) : (
                <div className="text-xs">
                  <p className="text-gray-300">Drag CCTV clip or click to browse</p>
                  <p className="text-gray-600 mt-1 font-mono">Supported format: MP4 / AVI</p>
                </div>
              )}
            </div>

            {/* Target input */}
            <div>
              <label className="block text-[10px] font-mono tracking-widest text-gray-500 uppercase mb-1.5">
                TARGET NUMBER PLATE QUERY
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={targetPlate}
                  onChange={(e) => setTargetPlate(e.target.value)}
                  placeholder="e.g. TS09EX5678"
                  className="w-full pl-3 pr-10 py-2.5 bg-gray-950 border border-gray-800 rounded-lg text-xs font-mono text-cyan-400 focus:outline-none focus:border-cyan-500/80 focus:shadow-glow-cyan"
                />
                <Crosshair className="absolute right-3 top-2.5 w-4 h-4 text-cyan-500/60 animate-pulse" />
              </div>
            </div>

            <button
              onClick={handleSearch}
              disabled={processing || !file}
              className="w-full bg-cyan-500 hover:bg-cyan-400 disabled:bg-cyan-950 py-3 rounded-lg text-xs font-bold text-gray-950 tracking-widest uppercase transition-all duration-300 shadow-glow-cyan"
            >
              {processing ? 'EXECUTING YOLO SCAN...' : 'LAUNCH INTEGRAL SEARCH'}
            </button>
          </div>

          {/* Quick Help Tips */}
          <div className="p-4 bg-gray-950/40 border border-gray-900 rounded-lg space-y-2">
            <span className="text-[9px] font-mono text-cyan-500/60 uppercase tracking-widest block font-bold">
              SURVEILLANCE RADAR SPECS
            </span>
            <p className="text-[10px] font-mono text-gray-500 leading-normal leading-relaxed">
              The search module parses the video frame-by-frame, extracts bounding targets via <strong className="text-cyan-400">YOLOv11</strong>, feeds crops to the OCR engine, and computes character sequence match indices.
            </p>
          </div>
        </div>

        {/* Right Search Results panel */}
        <div className="xl:col-span-2 space-y-6">
          
          {/* Loading state */}
          {processing && (
            <div className="glass-panel p-12 border border-cyan-500/10 flex flex-col items-center justify-center space-y-4">
              <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin shadow-glow-cyan"></div>
              <span className="font-mono text-xs text-cyan-400 tracking-widest uppercase animate-pulse">
                INTELLIGENT YOLO STREAM PARSING...
              </span>
            </div>
          )}

          {/* Result view */}
          {result && (
            <div className="space-y-6">
              
              {/* Highlight match details banner */}
              <div className={`p-4 rounded-lg border flex justify-between items-center ${
                result.matches_found > 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-rose-500/10 border-rose-500/30'
              }`}>
                <div className="flex items-center space-x-3 font-mono text-xs">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center ${
                    result.matches_found > 0 ? 'bg-emerald-950/80 border border-emerald-500/30 text-emerald-400' : 'bg-rose-950/80 border border-rose-500/30 text-rose-400'
                  }`}>
                    <Search className="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white uppercase">
                      TARGET MATCH SEARCH: {result.matches_found > 0 ? 'RESOLVED' : 'NO INTERCEPT'}
                    </h3>
                    <p className="text-[9px] text-gray-500 uppercase mt-0.5">
                      Target Plate: {result.target_plate} // Total cars cropped: {result.total_vehicles_detected}
                    </p>
                  </div>
                </div>

                <div className="text-right font-mono">
                  <span className="text-[9px] text-gray-400 uppercase block">MATCHES LOCATED</span>
                  <span className={`text-2xl font-black block ${result.matches_found > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {result.matches_found}
                  </span>
                </div>
              </div>

              {/* Annotated image frame */}
              <div className="glass-panel p-5 border border-gray-800 space-y-3">
                <span className="text-xs font-bold font-mono tracking-widest text-cyan-400 block uppercase">
                  VISION FEED OVERLAY (GREEN BOUNDS DETECTED TARGET)
                </span>
                <div className="aspect-video bg-gray-950 border border-gray-800 rounded-lg overflow-hidden relative">
                  <img 
                    src={`http://localhost:8000/${selectedFrame || result.annotated_frame_path}`} 
                    alt="Surveillance Feed Overlay" 
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2 left-2 bg-gray-950/80 px-2 py-0.5 rounded text-[8px] font-mono text-cyan-400 border border-cyan-800/30 uppercase">
                    YOLO CAMERA OVERLAY LIVE
                  </div>
                </div>
              </div>

              {/* Individual vehicles crops details list */}
              <div className="space-y-3">
                <span className="text-xs font-bold font-mono tracking-widest text-gray-400 block uppercase">
                  RESOLVED VEHICLE SEGMENTATION LOGS (CLICK CARD TO SWITCH OVERLAY TIMESTAMP)
                </span>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.detections?.map((det: any) => (
                    <div 
                      key={det.idx} 
                      onClick={() => {
                        if (det.annotated_frame_path) {
                          setSelectedFrame(det.annotated_frame_path);
                        }
                      }}
                      className={`glass-panel p-4 border flex space-x-4 hover:border-cyan-500/50 transition-all duration-300 cursor-pointer ${
                        selectedFrame === det.annotated_frame_path
                          ? 'border-cyan-400 bg-cyan-950/20 shadow-glow-cyan'
                          : det.is_matched
                          ? 'border-emerald-500/30 bg-emerald-950/5 shadow-glow-green'
                          : 'border-gray-800'
                      }`}
                    >
                      <div className="w-24 h-24 bg-gray-950 border border-gray-800 rounded overflow-hidden flex items-center justify-center shrink-0">
                        <img 
                          src={`http://localhost:8000/${det.crop_path}`} 
                          alt="Crop" 
                          className="w-full h-full object-cover"
                        />
                      </div>
                      
                      <div className="font-mono text-xs flex-1 flex flex-col justify-between">
                        <div>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase inline-block mb-1.5 ${
                            det.is_matched ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-950' : 'bg-gray-900 text-gray-500 border border-gray-800'
                          }`}>
                            {det.is_matched ? 'TARGET DETECTED' : `VEHICLE #${det.idx + 1}`}
                          </span>
                          <h4 className="text-white font-bold block font-mono">OCR READ: {det.ocr_text}</h4>
                          <span className="text-[10px] text-gray-500 block">
                            Type: <span className="text-cyan-400 capitalize">{det.vehicle_type || 'car'}</span> // OCR Conf: {Math.round(det.plate_confidence * 100)}%
                          </span>
                          {det.timestamp && (
                            <span className="text-[10px] text-cyan-400 block font-bold mt-1 font-mono uppercase tracking-widest">
                              SPOTTED AT: {det.timestamp}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex justify-between items-center pt-2 border-t border-gray-900/50">
                          <span className="text-[9px] text-gray-500 uppercase font-mono">SIMILARITY INDEX</span>
                          <span className={`font-bold ${det.is_matched ? 'text-emerald-400' : 'text-gray-400'}`}>
                            {Math.round(det.similarity_score * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* Dormant state */}
          {!file && !result && !processing && (
            <div className="glass-panel p-12 border border-gray-800 text-center flex flex-col items-center justify-center h-[50vh] space-y-4">
              <Crosshair className="w-12 h-12 text-gray-700" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-gray-300 uppercase font-mono">VISION PLOTTER STANDBY</h4>
                <p className="text-xs text-gray-500 max-w-sm font-mono uppercase">Upload surveillance clip and enter plate number keys to perform target intercept checks.</p>
              </div>
            </div>
          )}

        </div>

      </div>

    </div>
  );
};
