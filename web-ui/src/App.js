import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import MCPChat from './components/MCPChat';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ThreatIntel from './pages/ThreatIntel';
import { AuthProvider, useAuth } from './context/AuthContext';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="min-h-screen bg-thunder-900 flex items-center justify-center text-slate-400">Loading...</div>;
    if (!user) return <Navigate to="/login" replace />;
    return children;
};

const Alerts = () => <div className="card"><h1 className="text-2xl font-bold text-white mb-4">Alerts</h1><p className="text-slate-400">No active alerts.</p></div>;
const Data = () => <div className="card"><h1 className="text-2xl font-bold text-white mb-4">Data Explorer</h1><p className="text-slate-400">Connect to OpenSearch...</p></div>;
const Settings = () => <div className="card"><h1 className="text-2xl font-bold text-white mb-4">Settings</h1><p className="text-slate-400">System configuration...</p></div>;

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={
                        <ProtectedRoute>
                            <Layout />
                        </ProtectedRoute>
                    }>
                        <Route index element={<Dashboard />} />
                        <Route path="chat" element={<MCPChat />} />
                        <Route path="alerts" element={<Alerts />} />
                        <Route path="data" element={<ThreatIntel />} />
                        <Route path="settings" element={<Settings />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
