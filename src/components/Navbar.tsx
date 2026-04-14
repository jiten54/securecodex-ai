import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, Search, Key, LogOut } from 'lucide-react';
import { cn } from '../lib/utils';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'AI Analysis', path: '/analysis', icon: Search },
    { name: 'API Keys', path: '/keys', icon: Key },
  ];

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('apiKey');
    window.location.href = '/login';
  };

  return (
    <nav className="fixed top-0 left-0 right-0 h-16 border-b border-border bg-background/80 backdrop-blur-md z-50 flex items-center justify-between px-6">
      <div className="flex items-center gap-2">
        <Shield className="w-8 h-8 text-white" />
        <span className="text-xl font-bold tracking-tight">SecureCodeX</span>
      </div>

      <div className="flex items-center gap-8">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-2 text-sm font-medium transition-colors hover:text-white",
              location.pathname === item.path ? "text-white" : "text-muted-foreground"
            )}
          >
            <item.icon className="w-4 h-4" />
            {item.name}
          </Link>
        ))}
      </div>

      <button
        onClick={handleLogout}
        className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-white transition-colors"
      >
        <LogOut className="w-4 h-4" />
        Logout
      </button>
    </nav>
  );
};

export default Navbar;
