import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Lock, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        if (login(email, password)) {
            navigate('/');
        } else {
            setError('Invalid credentials. Try admin/admin');
        }
    };

    return (
        <div className="min-h-screen bg-thunder-900 flex items-center justify-center p-4">
            <div className="bg-thunder-800 p-8 rounded-xl shadow-2xl border border-thunder-700 w-full max-w-md">
                <div className="flex flex-col items-center mb-8">
                    <div className="mb-6">
                        <img src="/logo.png" alt="ThunderX Logo" className="h-12 w-auto" />
                    </div>
                    <h1 className="text-2xl font-bold text-white">Welcome Back</h1>
                    <p className="text-slate-400">Sign in to ThunderX Console</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-3 rounded text-sm text-center">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Email Address</label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                            <input
                                type="text"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-thunder-900 border border-thunder-600 rounded-lg py-2.5 pl-10 pr-4 text-white focus:border-thunder-accent focus:ring-1 focus:ring-thunder-accent outline-none transition-all"
                                placeholder="admin"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-thunder-900 border border-thunder-600 rounded-lg py-2.5 pl-10 pr-4 text-white focus:border-thunder-accent focus:ring-1 focus:ring-thunder-accent outline-none transition-all"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-thunder-accent hover:bg-blue-600 text-white font-semibold py-2.5 rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                    >
                        Sign In
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
