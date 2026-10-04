import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { ShieldAlert, Fingerprint, Activity, Eye, EyeOff } from 'lucide-react';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const data = await api.fetchApi<any>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      });

      if (data.access_token) {
        localStorage.setItem('Specter_token', data.access_token);
        localStorage.setItem('Specter_user', data.username);
        localStorage.setItem('Specter_role', data.role);
        navigate('/');
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during login.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex font-mono uppercase tracking-widest relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#111] hidden rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[#111] hidden rounded-full pointer-events-none" />
      
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 z-10">
        <div className="w-full max-w-md bg-white/5  border border-[#333] rounded-none p-10 shadow-none">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-[#111] blur-xl opacity-50 rounded-full" />
              <div className="w-16 h-16 bg-[#0a0a0a]   rounded-none flex items-center justify-center relative shadow-none transform rotate-3">
                <ShieldAlert className="w-8 h-8 text-white transform -rotate-3" />
              </div>
            </div>
          </div>
          <div className="text-center mb-10">
            <h1 className="text-4xl font-extrabold text-white tracking-tight">Specter</h1>
            <p className="text-[#00ff9d] mt-2 text-sm font-medium tracking-wide uppercase">Tactical Intelligence Node</p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-none mb-6 text-sm flex items-start gap-3">
              <Activity className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-[#00ff9d] uppercase tracking-wider mb-2">Operator ID</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Fingerprint className="h-5 w-5 text-[#00ff9d]" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#333] rounded-none pl-11 pr-4 py-3.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#00ff9d] focus:ring-1 focus:ring-indigo-500 transition-all"
                  placeholder="admin"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#00ff9d] uppercase tracking-wider mb-2">Access Code</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-[#333] rounded-none pl-4 pr-12 py-3.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#00ff9d] focus:ring-1 focus:ring-[#00ff9d] transition-all"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-[#888] hover:text-[#00ff9d] transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-4 bg-[#0a0a0a]   hover: hover: text-white font-semibold py-3.5 rounded-none shadow-none shadow-indigo-500/25 transition-all disabled:opacity-50 flex items-center justify-center transform active:scale-[0.98]"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Authenticating...</span>
                </div>
              ) : 'Initialize Session'}
            </button>
          </form>
        </div>
      </div>
      
      <div className="hidden lg:flex w-1/2 bg-[#0a0a0a] relative overflow-hidden items-center justify-center border-l border-[#222]">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTMwIDBoMzB2MzBIMzB6TTAgMzBoMzB2MzBIMHoiIGZpbGw9IiM0ZjQ2ZTUiIGZpbGwtb3BhY2l0eT0iMC4wNSIgZmlsbC1ydWxlPSJldmVub2RkIi8+PC9zdmc+')] opacity-50" />
        <div className="z-10 p-12 max-w-lg text-center">
          <div className="inline-block p-4 rounded-none bg-white/5  border border-[#333] mb-8">
            <Activity className="w-12 h-12 text-[#00ff9d]" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Command & Control Ready</h2>
          <p className="text-[#888] text-lg leading-relaxed">
            Monitor, analyze, and neutralize advanced persistent threats across your entire hybrid infrastructure with absolute precision.
          </p>
        </div>
      </div>
    </div>
  );
};
