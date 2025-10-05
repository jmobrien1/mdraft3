import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [requirements, setRequirements] = useState([]);
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/documents`);
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert(`✅ Extracted ${response.data.requirements_extracted} requirements!`);
      loadDocuments();
      loadDocument(response.data.document_id);
    } catch (error) {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const loadDocument = async (docId) => {
    setLoading(true);
    try {
      const [docResponse, statsResponse] = await Promise.all([
        axios.get(`${API_URL}/documents/${docId}`),
        axios.get(`${API_URL}/documents/${docId}/stats`)
      ]);

      setSelectedDoc(docResponse.data.document);
      setRequirements(docResponse.data.requirements);
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Error loading document:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateRequirement = async (reqId, status) => {
    try {
      await axios.patch(`${API_URL}/requirements/${reqId}`, null, {
        params: { status, validated_by: 'user' }
      });

      setRequirements(requirements.map(req =>
        req.id === reqId ? { ...req, status } : req
      ));

      if (selectedDoc) {
        const statsResponse = await axios.get(`${API_URL}/documents/${selectedDoc.id}/stats`);
        setStats(statsResponse.data);
      }
    } catch (error) {
      alert(`❌ Error: ${error.message}`);
    }
  };

  const getClassificationBadge = (classification) => {
    const colors = {
      PERFORMANCE_REQUIREMENT: '#10b981',
      COMPLIANCE_REQUIREMENT: '#f59e0b',
      DELIVERABLE_REQUIREMENT: '#3b82f6'
    };

    return (
      <span style={{
        backgroundColor: colors[classification] || '#6b7280',
        color: 'white',
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '600'
      }}>
        {classification?.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="app">
      <header className="header">
        <h1>📄 RFP Requirement Extractor</h1>
        <p>AI-powered requirement extraction from RFP documents</p>
      </header>

      <div className="main-content">
        <div className="sidebar">
          <div className="upload-section">
            <label htmlFor="file-upload" className="upload-button">
              {uploading ? '⏳ Uploading...' : '📤 Upload Document'}
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".txt,.pdf,.docx"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
          </div>

          <div className="documents-list">
            <h3>Documents</h3>
            {documents.length === 0 && <p className="empty-state">No documents yet</p>}
            {documents.map(doc => (
              <div
                key={doc.id}
                className={`document-item ${selectedDoc?.id === doc.id ? 'active' : ''}`}
                onClick={() => loadDocument(doc.id)}
              >
                <div className="doc-name">{doc.filename}</div>
                <div className="doc-date">{new Date(doc.uploaded_at).toLocaleDateString()}</div>
                <div className="doc-status">{doc.status}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="content-area">
          {!selectedDoc ? (
            <div className="empty-state-large">
              <h2>Welcome! 👋</h2>
              <p>Upload a document to get started</p>
              <p>Supported formats: PDF, DOCX, TXT</p>
            </div>
          ) : loading ? (
            <div className="loading">Loading...</div>
          ) : (
            <>
              <div className="document-header">
                <h2>{selectedDoc.filename}</h2>
                {stats && (
                  <div className="stats">
                    <div className="stat">
                      <span className="stat-label">Total</span>
                      <span className="stat-value">{stats.total}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Performance</span>
                      <span className="stat-value">{stats.performance}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Compliance</span>
                      <span className="stat-value">{stats.compliance}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Deliverable</span>
                      <span className="stat-value">{stats.deliverable}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Validated</span>
                      <span className="stat-value">{stats.validated}</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="requirements-list">
                {requirements.length === 0 ? (
                  <p className="empty-state">No requirements found</p>
                ) : (
                  requirements.map(req => (
                    <div key={req.id} className="requirement-card">
                      <div className="requirement-header">
                        {getClassificationBadge(req.classification)}
                        <span className="confidence">
                          {Math.round(parseFloat(req.ai_confidence_score || 0) * 100)}% confidence
                        </span>
                      </div>
                      <div className="requirement-text">{req.clean_text || req.raw_text}</div>
                      <div className="requirement-meta">
                        <span>{req.source_section}</span>
                        <div className="actions">
                          {req.status === 'ai_extracted' && (
                            <>
                              <button
                                className="btn-validate"
                                onClick={() => updateRequirement(req.id, 'human_validated')}
                              >
                                ✓ Validate
                              </button>
                              <button
                                className="btn-reject"
                                onClick={() => updateRequirement(req.id, 'rejected')}
                              >
                                ✗ Reject
                              </button>
                            </>
                          )}
                          {req.status === 'human_validated' && (
                            <span className="status-badge validated">✓ Validated</span>
                          )}
                          {req.status === 'rejected' && (
                            <span className="status-badge rejected">✗ Rejected</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
