import React, { useState } from 'react';
import { Shield, Bell, Terminal, Activity, Menu, X, Hexagon, Command } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

const navGroups = [
  { label: 'Command', to: '/', icon: Command },
  { label: 'Operations', items: [
    { to: '/soar', label: 'Automated Responses' },
    { to: '/investigations', label: 'Case Files' },
    { to: '/incidents', label: 'Active Anomalies' },
    { to: '/alerts', label: 'Critical Alerts' }
  ]},
  { label: 'Intelligence', items: [
    { to: '/hunting', label: 'Adversary Intel' },
    { to: '/iocs', label: 'Intel Feeds' },
    { to: '/entities', label: 'Asset Management' }
  ]},
  { label: 'Analytics', items: [
    { to: '/graph', label: 'Nexus Map' },
    { to: '/mitre', label: 'Tactics Matrix' },
    { to: '/behavior', label: 'Baseline Analytics' }
  ]},
  { label: 'System', items: [
    { to: '/collectors', label: 'Sensors' },
    { to: '/scenarios', label: 'Simulations' },
    { to: '/training', label: 'Academy' },
    { to: '/reports', label: 'Dossiers' },
    { to: '/settings', label: 'Configuration' }
  ]}
];

export const Navbar: React.FC = () => {
  const [openGroup, setOpenGroup] = useState<string | null>(null);

  return (
    <header className="h-14 bg-[#0a0a0a] border-b border-[#333333] px-6 flex items-center justify-between sticky top-0 z-50 font-mono text-sm">
      <div className="flex items-center gap-8 h-full">
        <Link to="/" className="flex items-center gap-3 group">
          <Hexagon className="w-6 h-6 text-[#00ff9d] group-hover:text-white transition-colors" />
          <span className="font-bold text-lg tracking-widest text-white uppercase">Specter</span>
        </Link>
        
        <nav className="hidden md:flex items-center h-full gap-1">
          {navGroups.map((group) => (
            group.items ? (
              <div 
                key={group.label} 
                className="relative h-full flex items-center px-4 cursor-pointer text-[#888888] hover:text-[#00ff9d] transition-colors"
                onMouseEnter={() => setOpenGroup(group.label)}
                onMouseLeave={() => setOpenGroup(null)}
              >
                <span className="uppercase tracking-wider text-[11px] font-semibold">{group.label}</span>
                {openGroup === group.label && (
                  <div className="absolute top-14 left-0 w-48 bg-[#111111] border border-[#333333] py-2 shadow-none z-50">
                    {group.items.map(item => (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                          `block px-4 py-2 text-xs uppercase tracking-wide transition-colors ${
                            isActive ? 'text-[#00ff9d] bg-[#1a1a1a]' : 'text-[#888888] hover:text-white hover:bg-[#222222]'
                          }`
                        }
                      >
                        {item.label}
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <NavLink 
                key={group.label} 
                to={group.to}
                className={({ isActive }) =>
                  `h-full flex items-center px-4 uppercase tracking-wider text-[11px] font-semibold transition-colors ${
                    isActive ? 'text-[#00ff9d] border-b-2 border-[#00ff9d]' : 'text-[#888888] hover:text-white'
                  }`
                }
              >
                {group.label}
              </NavLink>
            )
          ))}
        </nav>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1 bg-[#1a1a1a] border border-[#333] text-[10px] uppercase text-[#888]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#00ff9d] animate-pulse"></span>
          SYS.NOMINAL
        </div>

        <Link to="/alerts" className="text-[#888888] hover:text-white transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </Link>

        <Link to="/hunting" className="text-[#888888] hover:text-[#00ff9d] transition-colors">
          <Terminal className="w-4 h-4" />
        </Link>

        <div className="flex items-center gap-2 pl-4 border-l border-[#333]">
          <div className="w-7 h-7 bg-[#222] border border-[#444] flex items-center justify-center text-xs font-bold text-white">
            AD
          </div>
        </div>
      </div>
    </header>
  );
};
