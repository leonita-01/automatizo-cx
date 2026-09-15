import { useCallback, useEffect, useState } from "react";
import { BookOpen, FileUp, Pencil, Plus, Search, Trash2, X } from "lucide-react";

import { api } from "../services/api";


const EMPTY_FORM = {
  title: "",
  intent: "",
  keywords: "",
  content_en: "",
  content_de: "",
};


export default function KnowledgeCenter() {
  const [articles, setArticles] = useState([]);
  const [query, setQuery] = useState("");
  const [adminKey, setAdminKey] = useState(() => sessionStorage.getItem("cx-admin-key") || "");
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const loadArticles = useCallback(async (search = "") => {
    try {
      setArticles(await api.listArticles(search));
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    }
  }, []);

  useEffect(() => {
    loadArticles("");
  }, [loadArticles]);

  function updateAdminKey(value) {
    setAdminKey(value);
    sessionStorage.setItem("cx-admin-key", value);
  }

  function startEdit(article) {
    setEditingId(article.id);
    setForm({
      title: article.title,
      intent: article.intent,
      keywords: article.keywords.join(", "),
      content_en: article.content_en,
      content_de: article.content_de,
    });
    setShowEditor(true);
  }

  function closeEditor() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowEditor(false);
  }

  async function saveArticle(event) {
    event.preventDefault();
    setError("");
    const payload = {
      ...form,
      intent: form.intent.trim().toLowerCase().replaceAll(" ", "_"),
      keywords: form.keywords.split(",").map((item) => item.trim()).filter(Boolean),
    };
    try {
      if (editingId) {
        await api.updateArticle(editingId, payload, adminKey);
        setNotice("Knowledge article updated and audit event recorded.");
      } else {
        await api.createArticle(payload, adminKey);
        setNotice("Knowledge article created and available to the assistant.");
      }
      closeEditor();
      await loadArticles(query);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function deactivate(articleId) {
    if (!window.confirm("Deactivate this knowledge article?")) return;
    try {
      await api.deactivateArticle(articleId, adminKey);
      setNotice("Article deactivated. Existing audit history is preserved.");
      await loadArticles(query);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function importFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const result = await api.importArticles(file, adminKey);
      setNotice(`Imported ${result.imported}; skipped ${result.skipped}.`);
      await loadArticles(query);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      event.target.value = "";
    }
  }

  return (
    <section className="panel knowledge-panel">
      <div className="panel-heading">
        <div>
          <span className="heading-icon"><BookOpen size={20} /></span>
          <div><h2>Knowledge Management Center</h2><p>Govern approved bilingual support content</p></div>
        </div>
        <button className="primary-button" onClick={() => setShowEditor(true)}><Plus size={16} /> New article</button>
      </div>

      <div className="knowledge-toolbar">
        <div className="search-box"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === "Enter" && loadArticles(query)} placeholder="Search title, intent or content…" /></div>
        <input className="admin-key" type="password" value={adminKey} onChange={(event) => updateAdminKey(event.target.value)} placeholder="X-Admin-Key" aria-label="Administrator API key" />
        <label className="secondary-button upload-button"><FileUp size={16} /> Import JSON/CSV<input type="file" accept=".json,.csv" onChange={importFile} /></label>
      </div>

      {notice && <div className="inline-success">{notice}</div>}
      {error && <div className="inline-error">{error}</div>}

      <div className="article-table">
        <div className="table-row table-head"><span>Article</span><span>Intent</span><span>Languages</span><span>Actions</span></div>
        {articles.map((article) => (
          <div className="table-row" key={article.id}>
            <span><strong>{article.title}</strong><small>{article.keywords.slice(0, 4).join(" · ")}</small></span>
            <span><span className="intent-pill">{article.intent.replaceAll("_", " ")}</span></span>
            <span><span className="language-pill">EN</span> <span className="language-pill">DE</span></span>
            <span className="row-actions"><button onClick={() => startEdit(article)} title="Edit"><Pencil size={15} /></button><button onClick={() => deactivate(article.id)} title="Deactivate"><Trash2 size={15} /></button></span>
          </div>
        ))}
      </div>

      {showEditor && (
        <div className="modal-backdrop">
          <form className="article-editor" onSubmit={saveArticle}>
            <div className="modal-heading"><div><h3>{editingId ? "Edit knowledge article" : "Create knowledge article"}</h3><p>Both language variants are required for controlled multilingual support.</p></div><button type="button" onClick={closeEditor}><X size={19} /></button></div>
            <div className="form-grid"><label>Title<input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required /></label><label>Intent<input value={form.intent} onChange={(event) => setForm({ ...form, intent: event.target.value })} placeholder="technical_support" required /></label></div>
            <label>Keywords, comma separated<input value={form.keywords} onChange={(event) => setForm({ ...form, keywords: event.target.value })} required /></label>
            <label>English approved response<textarea rows="4" value={form.content_en} onChange={(event) => setForm({ ...form, content_en: event.target.value })} required /></label>
            <label>German approved response<textarea rows="4" value={form.content_de} onChange={(event) => setForm({ ...form, content_de: event.target.value })} required /></label>
            <div className="modal-actions"><button type="button" className="secondary-button" onClick={closeEditor}>Cancel</button><button className="primary-button">{editingId ? "Save changes" : "Create article"}</button></div>
          </form>
        </div>
      )}
    </section>
  );
}
