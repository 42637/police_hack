import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Eye, ShieldAlert, Cpu, Database, ChevronRight, Play } from 'lucide-react';
import { motion } from 'framer-motion';

export const Landing: React.FC = () => {
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Stats Counters
  const [platesProcessed, setPlatesProcessed] = useState(0);
  const [clonesFound, setClonesFound] = useState(0);
  
  useEffect(() => {
    let frameId: number;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Resize canvas
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particles representing vehicle nodes
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
      color: string;
    }> = [];

    for (let i = 0; i < 40; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        radius: Math.random() * 2 + 1,
        color: Math.random() > 0.5 ? '#06b6d4' : '#10b981',
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw Grid dot overlay
      ctx.fillStyle = 'rgba(6, 182, 212, 0.03)';
      const dotSpacing = 30;
      for (let x = 0; x < canvas.width; x += dotSpacing) {
        for (let y = 0; y < canvas.height; y += dotSpacing) {
          ctx.fillRect(x, y, 1.5, 1.5);
        }
      }

      // Draw Particles and connection lines
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.shadowBlur = 8;
        ctx.shadowColor = p.color;
        ctx.fill();
        ctx.shadowBlur = 0; // reset
      });

      // Connect nodes within threshold
      ctx.lineWidth = 0.5;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 180) {
            const alpha = (1 - dist / 180) * 0.12;
            ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      frameId = requestAnimationFrame(animate);
    };

    animate();

    // Stats animation timers
    const timer1 = setInterval(() => {
      setPlatesProcessed((prev) => (prev < 14245 ? prev + 121 : 14245));
    }, 15);
    
    const timer2 = setInterval(() => {
      setClonesFound((prev) => (prev < 87 ? prev + 1 : 87));
    }, 25);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', resizeCanvas);
      clearInterval(timer1);
      clearInterval(timer2);
    };
  }, []);

  return (
    <div className="min-h-screen bg-cyber-bg relative flex flex-col items-center justify-between text-gray-100 overflow-hidden font-sans">
      {/* Background Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />
      
      {/* Aurora overlays */}
      <div className="absolute inset-0 bg-aurora-cyan z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-aurora-purple z-0 pointer-events-none" />

      {/* Top Bar Navigation */}
      <header className="w-full max-w-7xl h-20 flex items-center justify-between px-6 z-10">
        <div className="flex items-center space-x-2">
          <Shield className="w-8 h-8 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
          <span className="font-bold tracking-widest text-lg text-white uppercase font-mono">SENTINEL AI</span>
        </div>
        <div>
          <button 
            onClick={() => navigate('/login')}
            className="border border-cyan-500/30 hover:border-cyan-400 bg-cyan-950/20 px-5 py-2 rounded-lg text-sm font-semibold text-cyan-400 tracking-wider transition-all duration-300 hover:shadow-glow-cyan"
          >
            ENTER PLATFORM
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="w-full max-w-7xl flex-1 flex flex-col lg:flex-row items-center justify-center px-6 py-12 gap-12 z-10">
        <div className="flex-1 space-y-6 text-center lg:text-left">
          <div className="inline-flex items-center space-x-2 bg-cyan-950/30 border border-cyan-500/20 px-3.5 py-1.5 rounded-full text-xs font-mono tracking-widest text-cyan-400 uppercase">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>POLICE CYBER OPERATIONS // PROTOCOL v4.1</span>
          </div>
          
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-none text-white uppercase">
            AI-Powered <br className="hidden sm:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">
              Vehicle Intelligence
            </span> <br />
            & Clone Detection
          </h2>
          
          <p className="text-gray-400 text-base max-w-xl mx-auto lg:mx-0 font-light leading-relaxed">
            Enterprise CCTV video analytics and clone plate intelligence engine. Instantly detect duplicate license numbers operating concurrently using advanced spatial-temporal algorithms and multi-modal Gemini auditing.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
            <button 
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto bg-cyan-500 hover:bg-cyan-400 px-8 py-4 rounded-xl text-sm font-bold text-gray-950 tracking-wider shadow-glow-cyan transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <span>ACCESS OPERATIONS HUB</span>
              <ChevronRight className="w-4 h-4" />
            </button>
            <a 
              href="#features" 
              className="w-full sm:w-auto border border-gray-800 hover:border-gray-700 bg-gray-900/30 hover:bg-gray-900/50 px-8 py-4 rounded-xl text-sm font-bold text-gray-300 tracking-wider transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <span>EXPLORE PLATFORM PIPELINE</span>
            </a>
          </div>

          {/* Quick Metrics display */}
          <div className="grid grid-cols-2 gap-4 pt-6 border-t border-gray-900 max-w-md mx-auto lg:mx-0">
            <div>
              <p className="text-3xl font-black text-white font-mono tracking-tight">{platesProcessed.toLocaleString()}+</p>
              <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Surveillance Plotted</p>
            </div>
            <div>
              <p className="text-3xl font-black text-rose-500 font-mono tracking-tight">{clonesFound}</p>
              <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Active Clones Intercepted</p>
            </div>
          </div>
        </div>

        {/* Hero Interactive Terminal Graphic */}
        <div className="flex-1 w-full max-w-lg relative">
          <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 to-emerald-500/10 blur-2xl rounded-3xl" />
          
          <div className="glass-panel p-6 border border-cyan-500/20 space-y-4 shadow-[0_0_50px_rgba(6,182,212,0.1)] relative">
            {/* Terminal Top Window Controls */}
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <span className="text-[10px] font-mono text-gray-500 tracking-widest pl-2">ACTIVE CAMERA STREAM [AP-VIJ-04]</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse shadow-glow-cyan"></span>
            </div>

            {/* Simulated Live Video Processing Panel */}
            <div className="aspect-video bg-gray-950 border border-gray-800 rounded-lg relative overflow-hidden flex items-center justify-center group">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,rgba(0,0,0,0.8)_100%)] z-10" />
              <div className="absolute inset-0 cyber-grid opacity-30" />
              
              {/* Scanline line */}
              <div className="absolute inset-x-0 top-0 h-[2px] bg-cyan-500/40 animate-scanline shadow-glow-cyan z-10" />

              {/* Bounding box mock overlay */}
              <div className="absolute border-2 border-emerald-400 top-[20%] left-[25%] w-[45%] h-[55%] flex flex-col justify-between p-1 z-10">
                <span className="bg-emerald-400 text-gray-950 text-[9px] px-1 font-mono font-bold self-start rounded">
                  VEHICLE // CONF 98.4%
                </span>
                <span className="border border-emerald-400 border-dashed text-emerald-300 text-[8px] p-0.5 font-mono self-end rounded bg-gray-950/80">
                  PLATE: AP31CV1234
                </span>
              </div>

              {/* Surrounding HUD details */}
              <div className="absolute top-2 left-2 text-[8px] font-mono text-cyan-400 bg-gray-950/80 px-1 py-0.5 rounded border border-cyan-800/30">
                CAM_AZIMUTH: 184.22
              </div>
              <div className="absolute bottom-2 left-2 text-[8px] font-mono text-gray-500 bg-gray-950/80 px-1 py-0.5 rounded">
                FPS: 30.00 // LATENCY: 42ms
              </div>

              {/* Overlay Play Symbol */}
              <div className="z-10 w-12 h-12 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-400/30 rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 hover:scale-105">
                <Play className="w-5 h-5 text-cyan-400 fill-cyan-400/20" />
              </div>
            </div>

            {/* Extraction Metadata list */}
            <div className="space-y-2 font-mono">
              <div className="flex justify-between text-xs border-b border-gray-900 pb-1.5">
                <span className="text-gray-500">PLATE ID</span>
                <span className="text-cyan-400 font-bold">AP31CV1234</span>
              </div>
              <div className="flex justify-between text-xs border-b border-gray-900 pb-1.5">
                <span className="text-gray-500">VISUAL DETAILS</span>
                <span className="text-emerald-400 font-bold">Red Maruti Swift</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">THREAT RISK INDEX</span>
                <span className="text-rose-500 font-bold tracking-widest animate-pulse">[ CRITICAL CLONE ALERT ]</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Feature Timeline Section */}
      <section id="features" className="w-full border-t border-gray-900 bg-gray-950/40 py-20 z-10">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          <div className="text-center max-w-xl mx-auto space-y-3">
            <h3 className="text-2xl font-black uppercase tracking-widest text-cyan-400">SURVEILLANCE PROCESS PIPELINE</h3>
            <p className="text-gray-500 text-xs tracking-wider uppercase font-mono">From Video Feed to Intelligence Prosecution</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-panel p-6 border-l-2 border-l-cyan-400 space-y-3">
              <div className="w-10 h-10 bg-cyan-950/40 border border-cyan-800/30 rounded-lg flex items-center justify-center text-cyan-400">
                <Play className="w-5 h-5" />
              </div>
              <h4 className="text-md font-bold text-white uppercase font-mono">1. Video Extraction</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Applies Laplacian filters across CCTV videos to extract the sharpest and clearest frame for plate character OCR parsing.
              </p>
            </div>

            <div className="glass-panel p-6 border-l-2 border-l-cyan-400 space-y-3">
              <div className="w-10 h-10 bg-cyan-950/40 border border-cyan-800/30 rounded-lg flex items-center justify-center text-cyan-400">
                <Eye className="w-5 h-5" />
              </div>
              <h4 className="text-md font-bold text-white uppercase font-mono">2. YOLOv11 & OCR</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Slices visual vehicle coordinates and extracts alphanumeric text tokens from the number plate using PaddleOCR text bounding.
              </p>
            </div>

            <div className="glass-panel p-6 border-l-2 border-l-purple-400 space-y-3">
              <div className="w-10 h-10 bg-purple-950/40 border border-purple-800/30 rounded-lg flex items-center justify-center text-purple-400">
                <Cpu className="w-5 h-5" />
              </div>
              <h4 className="text-md font-bold text-white uppercase font-mono">3. Multi-Modal Auditing</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Queries Gemini multi-modal API to analyze the vehicle's model, color, and brand, comparing details directly with original frames.
              </p>
            </div>

            <div className="glass-panel p-6 border-l-2 border-l-rose-500 space-y-3">
              <div className="w-10 h-10 bg-rose-950/40 border border-rose-800/30 rounded-lg flex items-center justify-center text-rose-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h4 className="text-md font-bold text-white uppercase font-mono">4. Spatio-Temporal logs</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Calculates travel speed matrices between check stations. Triggers alarms if travel times imply physically impossible speed values.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full h-16 border-t border-gray-900 bg-gray-950 flex items-center justify-center text-gray-600 text-xs font-mono tracking-widest z-10">
        SENTINEL AI // ALL OPERATIONAL RIGHTS RESERVED [ 2026 ]
      </footer>
    </div>
  );
};
