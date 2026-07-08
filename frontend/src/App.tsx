import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Toaster } from 'react-hot-toast';

// Import Pages
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Section1 } from './pages/Section1';
import { Section2 } from './pages/Section2';
import { Section3 } from './pages/Section3';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Firs } from './pages/Firs';

// Protected Route Wrapper for security
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-cyber-bg flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-cyan-400/20 border-t-cyan-400 rounded-full animate-spin shadow-glow-cyan"></div>
          <span className="font-mono text-xs text-cyan-400 tracking-widest uppercase">INITIALIZING SENTINEL SECURE TERMINAL...</span>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <DashboardLayout>{children}</DashboardLayout>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Landing Page */}
          <Route path="/" element={<Landing />} />
          
          {/* Public Authentication Gate */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Intelligence Dashboard Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/section1" element={
            <ProtectedRoute>
              <Section1 />
            </ProtectedRoute>
          } />
          
          <Route path="/section2" element={
            <ProtectedRoute>
              <Section2 />
            </ProtectedRoute>
          } />
          
          <Route path="/section3" element={
            <ProtectedRoute>
              <Section3 />
            </ProtectedRoute>
          } />

          <Route path="/history" element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          } />

          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />

          <Route path="/firs" element={
            <ProtectedRoute>
              <Firs />
            </ProtectedRoute>
          } />
          
          {/* Catch-all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#0c0f1d',
              color: '#e2e8f0',
              border: '1px solid rgba(6,182,212,0.2)',
              fontFamily: 'Outfit, sans-serif',
              fontSize: '14px',
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
