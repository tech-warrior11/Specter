import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const Settings: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await api.fetchApi<any>('/auth/me');
        setProfile(data);
      } catch (err) {
        console.error("Failed to fetch profile", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('Specter_token');
    localStorage.removeItem('Specter_user');
    localStorage.removeItem('Specter_role');
    navigate('/login');
  };

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
          <svg className="w-8 h-8 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Platform Settings
        </h1>
        <p className="text-[#888] mt-2">Manage your account profile and platform configuration.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-6 shadow-none">
          <h2 className="text-xl font-semibold text-slate-200 border-b border-[#333] pb-4 mb-4">User Profile</h2>
          {loading ? (
            <div className="animate-pulse flex space-x-4">
              <div className="flex-1 space-y-4 py-1">
                <div className="h-4 bg-[#111] rounded w-3/4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-[#111] rounded"></div>
                  <div className="h-4 bg-[#111] rounded w-5/6"></div>
                </div>
              </div>
            </div>
          ) : profile ? (
            <div className="space-y-4">
              <div>
                <span className="block text-sm text-slate-500">Username</span>
                <span className="text-lg text-slate-200">{profile.username}</span>
              </div>
              <div>
                <span className="block text-sm text-slate-500">Email</span>
                <span className="text-lg text-slate-200">{profile.email}</span>
              </div>
              <div>
                <span className="block text-sm text-slate-500">RBAC Role</span>
                <span className="inline-block mt-1 px-3 py-1 bg-cyan-500/20 text-cyan-400 text-sm rounded-full border border-cyan-500/30">
                  {profile.role}
                </span>
              </div>
            </div>
          ) : (
            <div className="text-red-400">Failed to load profile.</div>
          )}
        </div>

        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-6 shadow-none">
          <h2 className="text-xl font-semibold text-slate-200 border-b border-[#333] pb-4 mb-4">Session Management</h2>
          <p className="text-[#888] text-sm mb-6">
            You are currently signed in. If you are on a shared computer, ensure you sign out when finished.
          </p>
          <button 
            onClick={handleLogout}
            className="w-full sm:w-auto px-6 py-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 hover:text-red-300 border border-red-500/30 rounded-none transition-colors font-medium"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};
