import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './index.css';

const API_URL = 'http://localhost:8000';

const SearchBar = ({ onSearchResults }) => {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        setIsLoading(true);
        try {
            const response = await axios.get(`${API_URL}/api/judgments/search`, {
                params: { q: query }
            });
            onSearchResults(response.data);
        } catch (error) {
            console.error("Error searching judgments:", error);
            onSearchResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4 text-gray-700">On-Demand Precedent Search</h2>
            <form onSubmit={handleSearch} className="flex gap-2">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., Evidentiary value of a retracted confession"
                    className="flex-grow p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                />
                <button
                    type="submit"
                    disabled={isLoading}
                    className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300 transition-colors"
                >
                    {isLoading ? 'Searching...' : 'Search'}
                </button>
            </form>
        </div>
    );
};

const JudgmentCard = ({ judgment }) => (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-4 transition-transform hover:scale-[1.01]">
        <h3 className="text-xl font-bold text-blue-800">{judgment.case_title} ({judgment.year})</h3>
        <p className="text-sm text-gray-500 mb-2">{judgment.citation}</p>
        <p className="font-semibold text-gray-700 mt-3">Key Takeaway:</p>
        <p className="text-gray-600 leading-relaxed">{judgment.key_takeaway}</p>
    </div>
);

const AlertsDisplay = ({ alerts }) => (
    <div className="mt-2 mb-6">
        <h2 className="text-2xl font-bold mb-4 text-red-700">Proactive Pitfall Analysis</h2>
        {alerts.length === 0 ? (
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-r-lg shadow">
                <p className="font-bold">All Clear</p>
                <p>No procedural pitfalls detected for this case yet.</p>
            </div>
        ) : (
            alerts.map(alert => (
                <div key={alert.id} className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-r-lg mb-4 shadow animate-pulse-once">
                    <p className="font-bold">{alert.title}</p>
                    <p>{alert.message}</p>
                </div>
            ))
        )}
    </div>
);

export default function App() {
    const [searchResults, setSearchResults] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [activeCase, setActiveCase] = useState(null);

    const setupDemoCase = useCallback(async () => {
        try {
            const incidentDate = new Date();
            incidentDate.setDate(incidentDate.getDate() - 2); // 2 days ago
            const firDate = new Date();

            const caseData = {
                case_number: `DEMO-${Date.now()}`,
                fir_details: { "offense": "BNS Section 84" },
                incident_date: incidentDate.toISOString(),
                fir_date: firDate.toISOString(),
            };
            const response = await axios.post(`${API_URL}/api/cases`, caseData);
            const newCase = response.data;
            setActiveCase(newCase);
            setAlerts(newCase.alerts || []);
        } catch (error) {
            console.error("Error setting up demo case:", error.response ? error.response.data : error.message);
        }
    }, []);

    useEffect(() => {
        setupDemoCase();
    }, [setupDemoCase]);

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm sticky top-0 z-10">
                <div className="container mx-auto px-6 py-4">
                    <h1 className="text-3xl font-bold text-gray-800">NYAYA AI - Judicial Intelligence Engine</h1>
                </div>
            </header>
            <main className="container mx-auto p-6">
                 <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl mx-auto">
                    {activeCase && (
                        <div className="mb-6 pb-6 border-b">
                           <div className="flex justify-between items-center">
                             <h2 className="text-xl font-semibold">Active Case: <span className="font-mono text-blue-600">{activeCase.case_number}</span></h2>
                             <button onClick={setupDemoCase} className="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 rounded-lg">Create New Demo Case</button>
                           </div>
                            <AlertsDisplay alerts={alerts} />
                        </div>
                    )}
                    <SearchBar onSearchResults={setSearchResults} />
                    <div>
                        {searchResults.length > 0 && searchResults.map(judgment => (
                            <JudgmentCard key={judgment.id} judgment={judgment} />
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}

