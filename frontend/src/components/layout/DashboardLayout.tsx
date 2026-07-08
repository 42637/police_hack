import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, ShieldAlert, Binary, Bot, 
  Settings, ClipboardList, LogOut, ShieldAlert as ShieldIcon,
  Activity, Clock, FileText
} from 'lucide-react';

interface SidebarItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ to, icon, label, active }) => {
  return (
    <Link 
      to={to} 
      className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300 ${
        active 
          ? 'bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-400 shadow-glow-cyan' 
          : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/40'
      }`}
    >
      <span className={active ? "text-cyan-400" : "text-gray-400"}>{icon}</span>
      <span className="font-medium text-sm tracking-wider uppercase">{label}</span>
    </Link>
  );
};

export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toISOString().replace('T', ' ').substring(0, 19));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid text-gray-100 flex flex-col relative overflow-hidden scanline">
      {/* Top Header */}
      <header className="h-16 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md flex items-center justify-between px-6 z-20">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <ShieldIcon className="w-8 h-8 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-glow-green"></span>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-widest text-cyan-400 uppercase">SENTINEL AI</h1>
            <p className="text-[10px] text-gray-500 tracking-wider font-mono">CLONE VEHICLE INTELLIGENCE PLATFORM</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="hidden md:flex items-center space-x-2 text-xs font-mono text-gray-400 border border-gray-800 bg-gray-900/60 px-3 py-1.5 rounded">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>OPERATIONAL TIME [ {time} UTC ]</span>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-xs font-medium text-cyan-400">{user?.full_name}</p>
              <p className="text-[9px] font-mono text-emerald-400 tracking-widest uppercase">{user?.role} // LEVEL 01</p>
            </div>
            <div className="w-9 h-9 rounded-full border border-cyan-500/30 bg-cyan-950/60 flex items-center justify-center font-mono text-cyan-300 text-sm font-bold shadow-glow-cyan">
              {user?.username ? user.username.substring(0, 2).toUpperCase() : 'AD'}
            </div>
          </div>
        </div>
      </header>

      {/* Workspace Sidebar & Content */}
      <div className="flex flex-1 relative overflow-hidden z-10">
        <aside className="w-64 border-r border-gray-800 bg-gray-950/50 backdrop-blur-md flex flex-col justify-between p-4 shrink-0 hidden lg:flex">
          <div className="space-y-1.5">
            <div className="px-3 py-2">
              <span className="text-[10px] text-gray-500 font-mono tracking-widest uppercase">INTELLIGENCE TERMINAL</span>
            </div>
            
            <SidebarItem 
              to="/dashboard" 
              icon={<LayoutDashboard className="w-4 h-4" />} 
              label="Control Room" 
              active={location.pathname === '/dashboard'} 
            />
            <SidebarItem 
              to="/section1" 
              icon={<ShieldAlert className="w-4 h-4" />} 
              label="Clone Detection" 
              active={location.pathname === '/section1'} 
            />
            <SidebarItem 
              to="/section2" 
              icon={<Binary className="w-4 h-4" />} 
              label="Vehicle Search" 
              active={location.pathname === '/section2'} 
            />
            <SidebarItem 
              to="/section3" 
              icon={<Bot className="w-4 h-4 text-purple-400" />} 
              label="AI assistant" 
              active={location.pathname === '/section3'} 
            />
            <SidebarItem 
              to="/firs" 
              icon={<FileText className="w-4 h-4 text-cyan-400" />} 
              label="FIR Section" 
              active={location.pathname === '/firs'} 
            />
            
            <div className="px-3 py-2 pt-6">
              <span className="text-[10px] text-gray-500 font-mono tracking-widest uppercase">AUDITING & SETS</span>
            </div>
            <SidebarItem 
              to="/history" 
              icon={<ClipboardList className="w-4 h-4" />} 
              label="Audit logs" 
              active={location.pathname === '/history'} 
            />
            <SidebarItem 
              to="/settings" 
              icon={<Settings className="w-4 h-4" />} 
              label="Settings" 
              active={location.pathname === '/settings'} 
            />
          </div>

          <div className="pt-4 border-t border-gray-900">
            <button 
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-rose-400 hover:text-rose-300 hover:bg-rose-500/5 transition-all duration-300 border border-transparent hover:border-rose-950"
            >
              <LogOut className="w-4 h-4" />
              <span className="font-semibold text-xs tracking-wider uppercase">SECURE LOGOUT</span>
            </button>
          </div>
        </aside>

        {/* Mobile Navigation Header */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 h-16 bg-gray-950 border-t border-gray-800 flex items-center justify-around px-2 z-50">
          <Link to="/dashboard" className={`flex flex-col items-center text-xs ${location.pathname === '/dashboard' ? 'text-cyan-400' : 'text-gray-400'}`}>
            <LayoutDashboard className="w-5 h-5" />
            <span className="text-[9px] mt-0.5">Control</span>
          </Link>
          <Link to="/section1" className={`flex flex-col items-center text-xs ${location.pathname === '/section1' ? 'text-cyan-400' : 'text-gray-400'}`}>
            <ShieldAlert className="w-5 h-5" />
            <span className="text-[9px] mt-0.5">Clone</span>
          </Link>
          <Link to="/section2" className={`flex flex-col items-center text-xs ${location.pathname === '/section2' ? 'text-cyan-400' : 'text-gray-400'}`}>
            <Binary className="w-5 h-5" />
            <span className="text-[9px] mt-0.5">Search</span>
          </Link>
          <Link to="/section3" className={`flex flex-col items-center text-xs ${location.pathname === '/section3' ? 'text-cyan-400' : 'text-gray-400'}`}>
            <Bot className="w-5 h-5 text-purple-400" />
            <span className="text-[9px] mt-0.5">AI</span>
          </Link>
          <Link to="/firs" className={`flex flex-col items-center text-xs ${location.pathname === '/firs' ? 'text-cyan-400' : 'text-gray-400'}`}>
            <FileText className="w-5 h-5 text-cyan-400" />
            <span className="text-[9px] mt-0.5">FIR</span>
          </Link>
          <button onClick={handleLogout} className="flex flex-col items-center text-rose-400">
            <LogOut className="w-5 h-5" />
            <span className="text-[9px] mt-0.5">Logout</span>
          </button>
        </div>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 pb-24 lg:pb-8">
          {children}
        </main>
      </div>
    </div>
  );
};
