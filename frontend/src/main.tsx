import React, { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart3,
  CheckCircle2,
  FileText,
  LogOut,
  Pencil,
  RefreshCw,
  Trash2,
  UploadCloud,
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

type User = {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
};

type DocumentStatus = "uploaded" | "processing" | "processed" | "failed";

type BusinessDocument = {
  id: number;
  original_filename: string;
  content_type: string;
  file_size: number;
  status: DocumentStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

type DocumentDetail = BusinessDocument & {
  extracted_text_preview: string | null;
};

type Stats = {
  total_documents: number;
  uploaded_documents: number;
  processing_documents: number;
  processed_documents: number;
  failed_documents: number;
};

const emptyStats: Stats = {
  total_documents: 0,
  uploaded_documents: 0,
  processing_documents: 0,
  processed_documents: 0,
  failed_documents: 0,
};

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("synapse_token") || "");
  const [user, setUser] = useState<User | null>(null);
  const [documents, setDocuments] = useState<BusinessDocument[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
  const [stats, setStats] = useState<Stats>(emptyStats);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@synapse.ai");
  const [password, setPassword] = useState("strong-password");
  const [fullName, setFullName] = useState("Demo User");
  const [file, setFile] = useState<File | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const authHeaders = useMemo(
    () => ({
      Authorization: `Bearer ${token}`,
    }),
    [token],
  );

  useEffect(() => {
    if (token) {
      void loadWorkspace();
    }
  }, [token]);

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, options);
    if (!response.ok) {
      let message = `Request failed with ${response.status}`;
      try {
        const body = await response.json();
        message = body.detail || message;
      } catch {
        // keep default message
      }
      throw new Error(message);
    }
    if (response.status === 204) {
      return undefined as T;
    }
    return response.json() as Promise<T>;
  }

  async function loadWorkspace() {
    setError("");
    const [me, docs, dashboardStats] = await Promise.all([
      request<User>("/auth/me", { headers: authHeaders }),
      request<BusinessDocument[]>("/documents", { headers: authHeaders }),
      request<Stats>("/dashboard/stats", { headers: authHeaders }),
    ]);
    setUser(me);
    setDocuments(docs);
    setStats(dashboardStats);
    if (selectedDocument && !docs.some((doc) => doc.id === selectedDocument.id)) {
      setSelectedDocument(null);
    }
  }

  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      if (authMode === "register") {
        await request<User>("/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, full_name: fullName }),
        });
      }

      const result = await request<{ access_token: string; user: User }>("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("synapse_token", result.access_token);
      setToken(result.access_token);
      setUser(result.user);
      setNotice("Signed in successfully.");
    } catch (authError) {
      setError(authError instanceof Error ? authError.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a PDF, DOCX, CSV, or TXT file first.");
      return;
    }
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const payload = new FormData();
      payload.append("file", file);
      await request("/documents/upload", {
        method: "POST",
        headers: authHeaders,
        body: payload,
      });
      setFile(null);
      setNotice("Document uploaded and processed.");
      await loadWorkspace();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function viewDocument(documentId: number) {
    setBusy(true);
    setError("");
    try {
      const detail = await request<DocumentDetail>(`/documents/${documentId}`, { headers: authHeaders });
      setSelectedDocument(detail);
      setRenameValue(detail.original_filename);
    } catch (viewError) {
      setError(viewError instanceof Error ? viewError.message : "Could not load document");
    } finally {
      setBusy(false);
    }
  }

  async function renameDocument() {
    if (!selectedDocument) return;
    setBusy(true);
    setError("");
    try {
      await request<BusinessDocument>(`/documents/${selectedDocument.id}`, {
        method: "PATCH",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ original_filename: renameValue }),
      });
      setNotice("Document name updated.");
      await loadWorkspace();
      await viewDocument(selectedDocument.id);
    } catch (renameError) {
      setError(renameError instanceof Error ? renameError.message : "Rename failed");
    } finally {
      setBusy(false);
    }
  }

  async function deleteDocument(documentId: number) {
    const confirmed = window.confirm("Delete this document and its stored file?");
    if (!confirmed) return;
    setBusy(true);
    setError("");
    try {
      await request(`/documents/${documentId}`, {
        method: "DELETE",
        headers: authHeaders,
      });
      setNotice("Document deleted.");
      if (selectedDocument?.id === documentId) setSelectedDocument(null);
      await loadWorkspace();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    localStorage.removeItem("synapse_token");
    setToken("");
    setUser(null);
    setDocuments([]);
    setSelectedDocument(null);
    setStats(emptyStats);
    setNotice("Signed out.");
  }

  if (!token) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <div>
            <p className="eyebrow">SynapseAI</p>
            <h1>Business Copilot Workspace</h1>
            <p className="supporting-copy">
              Upload business documents, process them into searchable intelligence, and manage the workspace
              from one focused dashboard.
            </p>
          </div>
          <form className="auth-form" onSubmit={handleAuth}>
            <div className="segmented">
              <button type="button" className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>
                Login
              </button>
              <button
                type="button"
                className={authMode === "register" ? "active" : ""}
                onClick={() => setAuthMode("register")}
              >
                Register
              </button>
            </div>
            {authMode === "register" && (
              <label>
                Full name
                <input value={fullName} onChange={(event) => setFullName(event.target.value)} />
              </label>
            )}
            <label>
              Email
              <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label>
              Password
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            <button className="primary-action" disabled={busy}>
              {busy ? "Working..." : authMode === "login" ? "Login" : "Create account"}
            </button>
            <Feedback notice={notice} error={error} />
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">SynapseAI</p>
          <h1>Business Copilot</h1>
        </div>
        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#documents">Documents</a>
          <a href="#preview">Preview</a>
        </nav>
        <button className="ghost-action" onClick={logout}>
          <LogOut size={16} /> Logout
        </button>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Workspace</p>
            <h2>{user?.full_name || user?.email}</h2>
          </div>
          <button className="icon-action" title="Refresh dashboard" onClick={loadWorkspace} disabled={busy}>
            <RefreshCw size={18} />
          </button>
        </header>

        <Feedback notice={notice} error={error} />

        <section id="dashboard" className="stats-grid">
          <StatCard label="Total" value={stats.total_documents} icon={<BarChart3 size={18} />} />
          <StatCard label="Processed" value={stats.processed_documents} icon={<CheckCircle2 size={18} />} />
          <StatCard label="Uploaded" value={stats.uploaded_documents} icon={<UploadCloud size={18} />} />
          <StatCard label="Failed" value={stats.failed_documents} icon={<FileText size={18} />} />
        </section>

        <section id="documents" className="two-column">
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Ingestion</p>
                <h3>Upload Document</h3>
              </div>
            </div>
            <form className="upload-zone" onSubmit={uploadDocument}>
              <UploadCloud size={28} />
              <input
                type="file"
                accept=".pdf,.docx,.csv,.txt"
                onChange={(event: ChangeEvent<HTMLInputElement>) => setFile(event.target.files?.[0] || null)}
              />
              <p>{file ? file.name : "PDF, DOCX, CSV, or TXT"}</p>
              <button className="primary-action" disabled={busy || !file}>
                Upload
              </button>
            </form>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Library</p>
                <h3>Documents</h3>
              </div>
            </div>
            <div className="document-list">
              {documents.length === 0 ? (
                <p className="empty-state">No documents uploaded yet.</p>
              ) : (
                documents.map((document) => (
                  <article key={document.id} className="document-row">
                    <div>
                      <strong>{document.original_filename}</strong>
                      <span>
                        {formatBytes(document.file_size)} • <StatusBadge status={document.status} />
                      </span>
                    </div>
                    <div className="row-actions">
                      <button className="icon-action" title="View document" onClick={() => viewDocument(document.id)}>
                        <FileText size={16} />
                      </button>
                      <button className="icon-action danger" title="Delete document" onClick={() => deleteDocument(document.id)}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>
        </section>

        <section id="preview" className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Document Intelligence</p>
              <h3>{selectedDocument ? selectedDocument.original_filename : "Select a document"}</h3>
            </div>
          </div>
          {selectedDocument ? (
            <div className="preview-layout">
              <div className="rename-row">
                <input value={renameValue} onChange={(event) => setRenameValue(event.target.value)} />
                <button className="secondary-action" onClick={renameDocument} disabled={busy}>
                  <Pencil size={16} /> Rename
                </button>
              </div>
              <pre>{selectedDocument.extracted_text_preview || "No extracted text preview is available yet."}</pre>
            </div>
          ) : (
            <p className="empty-state">Open a document to inspect extracted text and test edit/delete flows.</p>
          )}
        </section>
      </section>
    </main>
  );
}

function Feedback({ notice, error }: { notice: string; error: string }) {
  if (!notice && !error) return null;
  return <div className={error ? "feedback error" : "feedback success"}>{error || notice}</div>;
}

function StatCard({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <article className="stat-card">
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function StatusBadge({ status }: { status: DocumentStatus }) {
  return <span className={`status ${status}`}>{status}</span>;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

createRoot(document.getElementById("root")!).render(<App />);
