import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, ShieldAlert, Activity, Settings, Database, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Layout = () => {
    const { logout, user } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-thunder-900 text-slate-300">
            {/* Sidebar */}
            <aside className="w-64 border-r border-thunder-700 bg-thunder-800 flex flex-col">
                <div className="h-16 flex items-center px-6 border-b border-thunder-700">
                    <Activity className="w-8 h-8 text-thunder-accent mr-3" />
                    <span className="text-xl font-bold text-white tracking-wide">ThunderX</span>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-2">
                    <NavItem to="/" icon={<LayoutDashboard size={20} />} label="Dashboard" />
                    <NavItem to="/chat" icon={<MessageSquare size={20} />} label="AI Investigator" />
                    <NavItem to="/alerts" icon={<ShieldAlert size={20} />} label="Alerts" />
                    <NavItem to="/data" icon={<Database size={20} />} label="Data Explorer" />
                </nav>

                <div className="p-4 border-t border-thunder-700">
                    <NavItem to="/settings" icon={<Settings size={20} />} label="Settings" />
                    <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-3 text-slate-400 hover:bg-thunder-700 hover:text-white rounded-lg transition-colors mt-2"
                    >
                        <LogOut size={20} className="mr-3" />
                        <span className="font-medium">Logout</span>
                    </button>
                    <div className="mt-4 px-4 text-xs text-slate-500">
                        Logged in as {user?.name}
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto bg-thunder-900">
                <div className="p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

const NavItem = ({ to, icon, label }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `flex items-center px-4 py-3 rounded-lg transition-all duration-200 ${isActive
                ? 'bg-thunder-accent text-white shadow-lg shadow-blue-500/20'
                : 'text-slate-400 hover:bg-thunder-700 hover:text-white'
            }`
        }
    >
        <span className="mr-3">{icon}</span>
        <span className="font-medium">{label}</span>
    </NavLink>
);

export default Layout;
