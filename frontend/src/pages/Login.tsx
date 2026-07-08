import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, User, AlertTriangle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  
  const isSessionExpired = searchParams.get('expired') === 'true';

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      username: '',
      password: ''
    }
  });

  const onSubmit = async (data: any) => {
    setLoading(true);
    const toastId = toast.loading('Authenticating secure keys...');
    try {
      await login(data.username, data.password);
      toast.success('Authentication clearance approved.', { id: toastId });
      navigate('/dashboard');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Key authorization failed.';
      toast.error(errorMsg, { id: toastId });
      logger.error("Authentication error: {}", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid text-gray-100 flex flex-col items-center justify-center p-6 relative scanline">
      {/* Glow Effects */}
      <div className="absolute inset-0 bg-aurora-cyan z-0 pointer-events-none" />
      
      <div className="w-full max-w-md relative z-10">
        <div className="absolute inset-0 bg-cyan-500/5 blur-3xl rounded-3xl" />
        
        <div className="glass-panel p-8 border border-cyan-500/20 shadow-[0_0_50px_rgba(6,182,212,0.05)] relative">
          
          {/* Top Shield Emblem */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 rounded-full bg-cyan-950/50 border border-cyan-500/30 flex items-center justify-center mb-3 shadow-glow-cyan animate-pulse-slow">
              <Shield className="w-8 h-8 text-cyan-400" />
            </div>
            <h2 className="text-xl font-bold tracking-widest text-white uppercase">SENTINEL ACCESS PORTAL</h2>
            <p className="text-[10px] text-gray-500 font-mono mt-1 tracking-wider">CYBER INTELLIGENCE AGENCY CLEARANCE REQUIRED</p>
          </div>

          {/* Session Expired Prompt */}
          {isSessionExpired && (
            <div className="mb-6 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 flex items-start space-x-2 text-yellow-400 font-mono text-xs">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>CLEARANCE EXPIRED. PLEASE SIGN IN AGAIN TO ACQUIRE NEW OPERATIONAL TOKEN.</span>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-[10px] font-mono tracking-widest text-gray-400 uppercase mb-1.5">
                OPERATOR USERNAME
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  {...register('username', { required: 'Username key required.' })}
                  placeholder="Enter administrator username"
                  className="w-full pl-10 pr-4 py-3 bg-gray-950/80 border border-gray-800 rounded-lg text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-cyan-500/80 focus:shadow-glow-cyan transition-all duration-300 font-mono"
                />
              </div>
              {errors.username && (
                <span className="text-[10px] font-mono text-rose-500 mt-1 block">{errors.username.message}</span>
              )}
            </div>

            <div>
              <label className="block text-[10px] font-mono tracking-widest text-gray-400 uppercase mb-1.5">
                CLEARANCE CRYPTO KEY (PASSWORD)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  {...register('password', { required: 'Clearance key required.' })}
                  placeholder="••••••••••••••"
                  className="w-full pl-10 pr-4 py-3 bg-gray-950/80 border border-gray-800 rounded-lg text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-cyan-500/80 focus:shadow-glow-cyan transition-all duration-300 font-mono"
                />
              </div>
              {errors.password && (
                <span className="text-[10px] font-mono text-rose-500 mt-1 block">{errors.password.message}</span>
              )}
            </div>

            {/* Warning Message */}
            <div className="p-3 bg-gray-900/60 rounded border border-gray-800 text-[10px] text-gray-500 font-mono leading-normal leading-relaxed">
              WARNING: Access to this terminal is tracked. All operations, coordinates, and uploads are logged in secure server audit chains under national surveillance protocols. Unauthenticated attempts are reportable.
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-cyan-500 hover:bg-cyan-400 disabled:bg-cyan-800 py-3 rounded-lg text-xs font-bold text-gray-950 tracking-widest uppercase transition-all duration-300 shadow-glow-cyan hover:shadow-[0_0_20px_rgba(6,182,212,0.6)]"
            >
              {loading ? 'ACQUIRING CLEARANCE...' : 'AUTHORIZE CONNECT'}
            </button>
          </form>

          {/* Seeding credentials prompt helper */}
          <div className="mt-6 border-t border-gray-900 pt-4 flex flex-col items-center">
            <span className="text-[9px] font-mono text-cyan-500/60 uppercase tracking-widest mb-1.5">
              SEED CLEARANCE CREDENTIALS
            </span>
            <div className="text-[10px] font-mono text-gray-500 space-x-3">
              <span>USER: <strong className="text-cyan-400">admin</strong></span>
              <span>PASS: <strong className="text-cyan-400">admin123</strong></span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
import { logger } from '../utils/mockLogger';
