import { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, ArrowRight, Database, Bot, X } from 'lucide-react';

export default function App() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // NEW: State to control our beautiful custom modal
  const [rejectModal, setRejectModal] = useState({ isOpen: false, recordId: null });

  // Fetch the data from your Django API
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/v1/ingestion/review/')
      .then(res => res.json())
      .then(data => {
        setRecords(data);
        setLoading(false);
      })
      .catch(err => console.error("Error fetching data:", err));
  }, []);

  // Sends the approval to the Django Immutable Ledger
  const handleApprove = (id) => {
    setRecords(records.filter(record => record.id !== id));
    fetch(`http://127.0.0.1:8000/api/v1/ingestion/approve/${id}/`, {
      method: 'PATCH',
    }).catch(err => console.error("Error approving record:", err));
  };

  // Simulates flagging a record for manual supervisor review
  const handleFlag = (id) => {
    alert(`Transaction #${id} has been escalated for Supervisor Review.`);
    setRecords(records.filter(record => record.id !== id));
  };

  // NEW: Opens the custom modal instead of the ugly browser alert
  const openRejectModal = (id) => {
    setRejectModal({ isOpen: true, recordId: id });
  };

  // NEW: Actually deletes the record when they click "Yes" inside the modal
  const confirmReject = () => {
    setRecords(records.filter(record => record.id !== rejectModal.recordId));
    setRejectModal({ isOpen: false, recordId: null });
    // In a production app, this would trigger a DELETE fetch request to the backend.
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-slate-500 animate-pulse flex items-center gap-2">
          <Database className="w-5 h-5" /> Syncing with Immutable Ledger...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8 relative">
      <div className="max-w-6xl mx-auto">
        
        {/* Header Section */}
        <div className="flex justify-between items-center mb-8 border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Data Normalization Queue</h1>
            <p className="text-slate-500 mt-1">Review and approve ingested vendor data for the audit ledger.</p>
          </div>
          <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full font-medium text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            {records.length} Records Pending
          </div>
        </div>

        {/* Empty State */}
        {records.length === 0 && (
          <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-slate-200">
            <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-slate-800">Queue Cleared</h3>
            <p className="text-slate-500">All data has been approved for the immutable ledger.</p>
          </div>
        )}

        {/* Data Cards Grid */}
        <div className="space-y-6">
          {records.map((record) => (
            <div key={record.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              
              {/* Card Header */}
              <div className="bg-slate-800 px-6 py-3 text-white flex justify-between items-center">
                <span className="font-medium text-sm text-slate-200">Transaction ID: #{record.id}</span>
                <span className="bg-slate-700 px-2 py-1 rounded text-xs tracking-wider">{record.scope_category}</span>
              </div>

              {/* Gemini AI Warning Banner */}
              {record.ai_audit_note && (
                <div className="mx-6 mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3 shadow-inner">
                  <Bot className="w-6 h-6 text-amber-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-sm font-bold text-amber-900 tracking-wide uppercase">AI Audit Flag</h4>
                    <p className="text-sm text-amber-800 mt-1 leading-relaxed">{record.ai_audit_note}</p>
                  </div>
                </div>
              )}

              {/* Card Body - Side by Side Comparison */}
              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                
                {/* Left Side: Messy Vault Data */}
                <div className="bg-red-50 p-4 rounded-lg border border-red-100 relative">
                  <span className="absolute -top-3 left-4 bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded">RAW PAYLOAD</span>
                  <pre className="text-xs text-red-900 mt-2 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(record.raw_payload_data, null, 2)}
                  </pre>
                </div>

                {/* Arrow Connector */}
                <div className="hidden md:flex justify-center -mx-4 z-10">
                  <div className="bg-white p-2 rounded-full shadow border border-slate-200">
                    <ArrowRight className="text-slate-400 w-6 h-6" />
                  </div>
                </div>

                {/* Right Side: Clean Ledger Data */}
                <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-100 relative">
                  <span className="absolute -top-3 left-4 bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-1 rounded">NORMALIZED LEDGER</span>
                  <div className="mt-3 space-y-2 text-sm text-emerald-900">
                    <p><span className="font-semibold">Source:</span> {record.emission_source}</p>
                    <p><span className="font-semibold">Date:</span> {record.activity_date_start}</p>
                    <p className="text-lg font-bold text-emerald-700 mt-2">
                      {record.normalized_value.toLocaleString()} {record.normalized_unit}
                    </p>
                  </div>
                </div>

              </div>

              {/* Card Footer - Action Buttons */}
              <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3 items-center">
                <button 
                  onClick={() => openRejectModal(record.id)}
                  className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  Reject
                </button>
                <button 
                  onClick={() => handleFlag(record.id)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Flag for Manual Review
                </button>
                <button 
                  onClick={() => handleApprove(record.id)}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors flex items-center gap-2 ml-2"
                >
                  <CheckCircle className="w-4 h-4" /> Approve & Lock
                </button>
              </div>

            </div>
          ))}
        </div>

      </div>

      {/* NEW: Custom Tailwind Reject Modal */}
      {rejectModal.isOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-opacity">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden transform transition-all">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <button onClick={() => setRejectModal({ isOpen: false, recordId: null })} className="text-slate-400 hover:text-slate-600">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Reject Data Record</h3>
              <p className="text-slate-600 leading-relaxed">
                Are you sure you want to reject transaction <span className="font-bold text-slate-800">#{rejectModal.recordId}</span>? 
                This action cannot be undone, and the data will be permanently purged from the review queue.
              </p>
            </div>
            <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
              <button 
                onClick={() => setRejectModal({ isOpen: false, recordId: null })} 
                className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={confirmReject} 
                className="px-5 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors"
              >
                Yes, Reject Record
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}