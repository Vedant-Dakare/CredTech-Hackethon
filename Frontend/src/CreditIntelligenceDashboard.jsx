import React, { useState, useEffect, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
  ChevronDown, TrendingUp, AlertCircle, CheckCircle, Building2
} from 'lucide-react';

const CreditIntelligenceDashboard = () => {
  // State for companies list, selected company, and loading status
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch the list of companies
  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:5000/api/companies");
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setCompanies(data);
      if (data.length > 0) {
        // Automatically select the first company in the list
        fetchCompanyDetails(data[0].name);
      }
    } catch (e) {
      setError(e.message);
      console.error("Failed to fetch companies:", e);
    } finally {
      setLoading(false);
    }
  };

  // Function to fetch details for a specific company
  const fetchCompanyDetails = async (name) => {
    try {
      const res = await fetch(`http://localhost:5000/api/companies/${name}`);
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setSelectedCompany(data);
    } catch (e) {
      setError(e.message);
      console.error(`Failed to fetch company details for ${name}:`, e);
    }
  };

  // Effect to fetch initial data on component mount
  useEffect(() => {
    fetchCompanies();
  }, []);

  // Memoized functions for score styling to prevent re-computation
  const getScoreColor = useMemo(() => (score) => {
    if (score >= 80) return 'text-emerald-600';
    if (score >= 70) return 'text-amber-500';
    return 'text-red-500';
  }, []);

  const getScoreGradient = useMemo(() => (score) => {
    if (score >= 80) return 'from-emerald-400 to-emerald-600';
    if (score >= 70) return 'from-amber-400 to-amber-600';
    return 'from-red-400 to-red-600';
  }, []);

  // Handle company selection change
  const handleCompanyChange = (e) => {
    const name = e.target.value;
    fetchCompanyDetails(name);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-xl text-gray-700">Loading data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <p className="text-xl text-red-700">Error: {error}. Please ensure your backend is running at http://localhost:5000 and has data populated.</p>
      </div>
    );
  }

  if (!selectedCompany) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p className="text-xl text-slate-700">No company data available. Please check the backend and refresh.</p>
      </div>
    );
  }

  // Helper function to format market cap
  const formatMarketCap = (cap) => {
    if (cap >= 1e12) return `$${(cap / 1e12).toFixed(2)}T`;
    if (cap >= 1e9) return `$${(cap / 1e9).toFixed(2)}B`;
    if (cap >= 1e6) return `$${(cap / 1e6).toFixed(2)}M`;
    return `$${cap}`;
  };

  // Metric definitions to map to backend data
  const metrics = [
    { title: 'Revenue', key: 'revenue', color: 'emerald' },
    { title: 'Debt to Equity', key: 'debt_to_equity', color: 'blue' },
    { title: 'Profit Margin', key: 'profit_margin', color: 'green' },
    { title: 'Return on Equity', key: 'return_on_equity', color: 'purple' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              📊 Credit Intelligence Platform
            </h1>
            <div className="flex items-center gap-4">
              <div className="relative">
                <select
                  value={selectedCompany.name}
                  onChange={handleCompanyChange}
                  className="block w-full appearance-none bg-white border border-slate-300 rounded-md py-2 pl-3 pr-8 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  {companies.map((c) => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Company Info & Score Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Company Info */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6 transition-all hover:shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">{selectedCompany.name}</h2>
                <p className="text-sm text-slate-500">{selectedCompany.sector}</p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Market Cap:</span>
                <span className="font-medium">{formatMarketCap(selectedCompany.marketCap)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Last Updated:</span>
                <span className="font-medium">{selectedCompany.lastUpdated}</span>
              </div>
            </div>
          </div>

          {/* Main Score Display */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-lg border border-slate-200 p-6 transition-all hover:shadow-xl">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-slate-700 mb-4">Credit Intelligence Score</h3>
              <div className="relative">
                <div className={`w-32 h-32 mx-auto rounded-full bg-gradient-to-br ${getScoreGradient(selectedCompany.score)} flex items-center justify-center shadow-lg transform transition-transform hover:scale-105`}>
                  <span className="text-4xl font-bold text-white">{selectedCompany.score.toFixed(0)}</span>
                </div>
                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                  <span className={`bg-slate-100 text-xs px-3 py-1 rounded-full font-medium ${getScoreColor(selectedCompany.score)}`}>
                    {selectedCompany.score >= 80 ? 'Excellent' : selectedCompany.score >= 70 ? 'Good' : 'Fair'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 my-8">
          {metrics.map((metric, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg border border-slate-200 p-4 transition-all hover:shadow-xl hover:-translate-y-1">
              <div className="text-center">
                <h4 className="text-sm font-medium text-slate-600">{metric.title}</h4>
                <div className={`text-2xl font-bold text-${metric.color}-600`}>
                  {selectedCompany.metrics ? selectedCompany.metrics[metric.key] : 'N/A'}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Why This Score Section & Sentiment Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6 transition-all hover:shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-blue-500" />
              Why this score?
            </h3>
            <div className="space-y-3">
              {selectedCompany.scoreFactors.map((factor, index) => {
                const IconComponent = factor.positive ? CheckCircle : AlertCircle;
                return (
                  <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                    <IconComponent className={`w-5 h-5 mt-0.5 ${factor.positive ? 'text-emerald-500' : 'text-amber-500'}`} />
                    <span className="text-sm text-slate-700 leading-relaxed">{factor.text}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6 transition-all hover:shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Sentiment Analysis</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={selectedCompany.sentiment}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="category"
                    tick={{ fontSize: 12, fill: '#64748b' }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Bar dataKey="positive" fill="#10b981" name="Positive" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="negative" fill="#f59e0b" name="Negative" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Credit Trend Chart */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6 transition-all hover:shadow-xl">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            Credit Score Trend
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={selectedCompany.creditTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  stroke="#e2e8f0"
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  stroke="#e2e8f0"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                  formatter={(value, name) => [`${value.toFixed(1)}`, name]}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 4, fill: '#3b82f6' }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CreditIntelligenceDashboard;