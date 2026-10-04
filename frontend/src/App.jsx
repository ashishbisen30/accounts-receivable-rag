import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { 
  DollarSign, 
  AlertTriangle, 
  FileText, 
  Users, 
  Send, 
  Bot, 
  User, 
  BookOpen, 
  RefreshCw 
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [customerSummary, setCustomerSummary] = useState([]);
  const [overdueInvoices, setOverdueInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello! I am your Accounts Receivable Assistant. Ask me anything about customer balances, overdue invoices, or company payment policies.' }
  ]);
  const [retrievedEvidence, setRetrievedEvidence] = useState([]);
  const [askingAssistant, setAskingAssistant] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [summaryRes, overdueRes] = await Promise.all([
        axios.get(`${API_BASE}/customers/summary`),
        axios.get(`${API_BASE}/invoices/overdue`)
      ]);
      setCustomerSummary(summaryRes.data.data || summaryRes.data.customers || summaryRes.data || []);
      setOverdueInvoices(overdueRes.data.data || overdueRes.data.overdue_invoices || overdueRes.data || []);
    } catch (err) {
      console.error('Error fetching dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalOutstanding = customerSummary.reduce((acc, curr) => acc + (curr.total_outstanding || 0), 0);
  const totalOverdue = overdueInvoices.reduce((acc, curr) => acc + (curr.amount || curr.balance || 0), 0);
  const numOverdueInvoices = overdueInvoices.length;

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || askingAssistant) return;

    const userQuery = chatInput;
    setChatInput('');
    setMessages((prev) => [...prev, { role: 'user', text: userQuery }]);
    setAskingAssistant(true);

    try {
      const response = await axios.post(`${API_BASE}/assistant/query`, { question: userQuery });
      const botResponse = response.data.answer || response.data.response || 'No response returned.';
      const sources = response.data.sources || response.data.evidence || [];

      setMessages((prev) => [...prev, { role: 'assistant', text: botResponse }]);
      if (sources.length > 0) {
        setRetrievedEvidence(sources);
      }
    } catch (error) {
      console.error('Assistant error:', error);
      setMessages((prev) => [...prev, { role: 'assistant', text: 'Sorry, I encountered an error communicating with the API.' }]);
    } finally {
      setAskingAssistant(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Accounts Receivable Dashboard</h1>
            <p className="text-slate-500 text-sm">Financial Analytics & AI Policy Assistant</p>
          </div>
          <button 
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Total Outstanding</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">${totalOutstanding.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
              <DollarSign className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Total Overdue Amount</p>
              <h3 className="text-2xl font-bold text-red-600 mt-1">${totalOverdue.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-red-50 text-red-600 rounded-lg">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Overdue Invoices</p>
              <h3 className="text-2xl font-bold text-amber-600 mt-1">{numOverdueInvoices}</h3>
            </div>
            <div className="p-3 bg-amber-50 text-amber-600 rounded-lg">
              <FileText className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Main Content Grid: Customer Table & AI Chat */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Customer Balances & Evidence (7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-slate-600" />
                <h2 className="text-lg font-semibold text-slate-800">Customer Outstanding Balances</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-slate-600">
                      <th className="p-3 font-medium">Customer Name</th>
                      <th className="p-3 font-medium text-right">Outstanding</th>
                      <th className="p-3 font-medium text-right">Overdue</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {customerSummary.map((cust, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 transition">
                        <td className="p-3 font-medium text-slate-800">{cust.customer_name || cust.name}</td>
                        <td className="p-3 text-right">${(cust.total_outstanding || 0).toLocaleString()}</td>
                        <td className="p-3 text-right text-red-600 font-medium">${(cust.overdue_amount || 0).toLocaleString()}</td>
                      </tr>
                    ))}
                    {customerSummary.length === 0 && (
                      <tr>
                        <td colSpan="3" className="p-4 text-center text-slate-400">No customer records found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Policy & Evidence Viewer */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-5 h-5 text-indigo-600" />
                <h2 className="text-lg font-semibold text-slate-800">Retrieved Policy & Evidence Sources</h2>
              </div>
              {retrievedEvidence.length > 0 ? (
                <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                  {retrievedEvidence.map((ev, i) => (
                    <div key={i} className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-lg text-xs space-y-1">
                      <div className="flex justify-between font-semibold text-indigo-900">
                        <span>Source: {ev.source || 'Policy Document'}</span>
                      </div>
                      <p className="text-slate-700">{ev.text || ev.content || JSON.stringify(ev)}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 italic">Ask a policy question in the assistant chat to view cited evidence snippets.</p>
              )}
            </div>
          </div>

          {/* AI Chat Window (5 Cols) */}
          <div className="lg:col-span-5 bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col h-[600px]">
            <div className="flex items-center gap-2 pb-4 border-b border-slate-100">
              <Bot className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-semibold text-slate-800">AI Financial Assistant</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-3 my-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 flex-shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}
                  <div className={`p-3 rounded-lg text-sm max-w-[85%] ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-br-none' 
                      : 'bg-slate-100 text-slate-800 rounded-bl-none'
                  }`}>
                    {msg.role === 'user' ? (
                      msg.text
                    ) : (
                      <div className="prose prose-sm max-w-none text-slate-800 dark:prose-invert">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 flex-shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}
              {askingAssistant && (
                <div className="text-xs text-slate-400 italic flex items-center gap-2">
                  <Bot className="w-4 h-4 animate-bounce text-indigo-500" />
                  Analyzing database & policy vectors...
                </div>
              )}
            </div>

            <form onSubmit={handleSendMessage} className="flex gap-2 pt-2 border-t border-slate-100">
              <input 
                type="text" 
                value={chatInput} 
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask about overdue balances or late fee policies..."
                className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button 
                type="submit" 
                disabled={askingAssistant}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 flex items-center justify-center"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>

        </div>
      </div>
    </div>
  );
}