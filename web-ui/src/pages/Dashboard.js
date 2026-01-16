import React, { useState } from 'react';
import { ExternalLink, RefreshCw } from 'lucide-react';

const Dashboard = () => {
    // In a real setup, OpenSearch Dashboards would be on port 5601
    // We assume it's accessible via localhost or valid network path
    const DASHBOARD_URL = "http://localhost:5601/app/dashboards#/view/security-overview";

    const [isLoading, setIsLoading] = useState(true);

    return (
        <div className="space-y-6 h-full flex flex-col">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white">Security Overview</h1>
                    <p className="text-slate-400 mt-1">Real-time network security monitoring</p>
                </div>
                <div className="flex space-x-3">
                    <button
                        onClick={() => document.getElementById('os-dashboard').src = document.getElementById('os-dashboard').src}
                        className="flex items-center space-x-2 px-4 py-2 bg-thunder-800 hover:bg-thunder-700 text-white rounded-lg border border-thunder-600 transition-colors"
                    >
                        <RefreshCw size={16} />
                        <span>Refresh</span>
                    </button>
                    <a
                        href={DASHBOARD_URL}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center space-x-2 px-4 py-2 bg-thunder-accent hover:bg-blue-600 text-white rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                    >
                        <ExternalLink size={16} />
                        <span>Open Full Screen</span>
                    </a>
                </div>
            </div>

            <div className="flex-1 bg-thunder-800 rounded-xl border border-thunder-700 overflow-hidden relative shadow-2xl">
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-thunder-800 z-10">
                        <div className="flex flex-col items-center space-y-4">
                            <div className="w-12 h-12 border-4 border-thunder-accent border-t-transparent rounded-full animate-spin"></div>
                            <p className="text-slate-400">Loading OpenSearch Dashboards...</p>
                        </div>
                    </div>
                )}

                <iframe
                    id="os-dashboard"
                    title="OpenSearch Dashboards"
                    src="http://localhost:5601/app/dashboards?embed=true&_g=(filters:[],refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))"
                    className="w-full h-full border-0"
                    onLoad={() => setIsLoading(false)}
                />
            </div>
        </div>
    );
};

export default Dashboard;
