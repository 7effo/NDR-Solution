import React, { useState, useEffect } from 'react';
import { Shield, Search, Database } from 'lucide-react';

const ThreatIntel = () => {
    const [ip, setIp] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState({ total_iocs: 0 });

    useEffect(() => {
        // Fetch stats on mount
        fetch('http://localhost:7000/stats')
            .then(res => res.json())
            .then(data => setStats(data))
            .catch(err => console.log('Threat Intel Service offline?'));
    }, []);

    const handleLookup = async (e) => {
        e.preventDefault();
        if (!ip) return;

        setLoading(true);
        setResult(null);

        try {
            const response = await fetch(`http://localhost:7000/enrich/ip/${ip}`);
            const data = await response.json();
            setResult(data);
        } catch (error) {
            setResult({ error: "Could not connect to Threat Intel service" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-white mb-8">Threat Intelligence</h1>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="card flex items-center p-6 bg-thunder-800 border-thunder-700">
                    <div className="p-3 rounded-full bg-blue-500/20 mr-4">
                        <Database className="text-blue-500" size={24} />
                    </div>
                    <div>
                        <div className="text-sm text-slate-400">Total IOCs</div>
                        <div className="text-2xl font-bold text-white">{stats.total_iocs.toLocaleString()}</div>
                    </div>
                </div>
            </div>

            {/* Lookup Tool */}
            <div className="card p-6 bg-thunder-800 border border-thunder-700 max-w-2xl">
                <h3 className="text-xl font-semibold text-white mb-4">IP Reputation Lookup</h3>
                <form onSubmit={handleLookup} className="flex gap-4">
                    <input
                        type="text"
                        value={ip}
                        onChange={(e) => setIp(e.target.value)}
                        placeholder="Enter IP address (e.g., 1.2.3.4)"
                        className="flex-1 bg-thunder-900 border border-thunder-600 rounded-lg px-4 py-3 text-white focus:border-thunder-accent focus:outline-none"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-6 py-3 bg-thunder-accent hover:bg-blue-600 text-white rounded-lg font-medium transition-colors flex items-center"
                    >
                        {loading ? 'Checking...' : <Search size={20} className="mr-2" />}
                        {loading ? '' : 'Check'}
                    </button>
                </form>

                {result && (
                    <div className={`mt-6 p-4 rounded-lg border ${result.error ? 'bg-red-500/10 border-red-500/50' :
                            result.is_malicious ? 'bg-red-500/10 border-red-500/50' : 'bg-green-500/10 border-green-500/50'
                        }`}>
                        {result.error ? (
                            <p className="text-red-400">{result.error}</p>
                        ) : result.is_malicious ? (
                            <div>
                                <div className="flex items-center text-red-500 font-bold text-lg mb-2">
                                    <Shield className="mr-2" /> MALICIOUS DETECTED
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div className="text-slate-400">Source: <span className="text-white">{result.source}</span></div>
                                    <div className="text-slate-400">Confidence: <span className="text-white">{(result.confidence * 100).toFixed(0)}%</span></div>
                                    <div className="text-slate-400">Last Seen: <span className="text-white">{result.last_seen}</span></div>
                                    <div className="text-slate-400">Tags: <span className="text-white">{result.tags || 'None'}</span></div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center text-green-500 font-bold">
                                <Shield className="mr-2" /> No threats found for this IP
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ThreatIntel;
