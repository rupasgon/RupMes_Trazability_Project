import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyLine = { line_id: "", description_line: "" };

export default function LinesPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [lines, setLines] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyLine);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const canWrite = useMemo(() => auth.permissions?.includes("masters.write"), [auth]);

  const loadLines = async () => {
    const data = await request("/lines", { tenantId });
    setLines(data);
  };

  useEffect(() => {
    loadLines().catch(() => {});
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/lines", {
        method: "POST",
        data: form,
        tenantId,
        csrfToken,
      });
      setForm(emptyLine);
      setEditorMode("idle");
      await loadLines();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
    setEditorMode("edit");
    setForm({ line_id: row.line_id, description_line: row.description_line });
  };

  const handleUpdate = async () => {
    if (!selected) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/lines/${selected.line_id}`, {
        method: "PATCH",
        data: { description_line: form.description_line },
        tenantId,
        csrfToken,
      });
      await loadLines();
      setStatus(t("masters.lines.updated"));
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selected) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/lines/${selected.line_id}`, {
        method: "DELETE",
        tenantId,
        csrfToken,
      });
      setSelected(null);
      setForm(emptyLine);
      setEditorMode("idle");
      await loadLines();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      auth={auth}
      onLogout={onLogout}
      active="lines"
      tenantId={tenantId}
      setTenantId={setTenantId}
      lang={lang}
      setLang={setLang}
      t={t}
      theme={theme}
      setTheme={setTheme}
    >
      <div className="page-header-shell">
        <div className="card page-header">
          <div className="page-header-copy">
            <h2>{t("masters.lines.title")}</h2>
            <p>{t("masters.lines.subtitle")}</p>
          </div>
        </div>
      </div>

      <div className="crud-grid">
        <div className="card crud-card crud-list-card">
          <div className="crud-card-header">
            <div>
              <h3>{t("common.list")}</h3>
              <p>{t("masters.lines.subtitle")}</p>
            </div>
            <div className="row-space">
              {canWrite ? (
                <button className="secondary" type="button" onClick={() => { setSelected(null); setForm(emptyLine); setStatus(""); setEditorMode("create"); }}>
                  {t("masters.lines.new")}
                </button>
              ) : null}
              <div className="crud-card-metric">{lines.length}</div>
            </div>
          </div>
          <div className="table-shell">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.id")}</th>
                  <th>{t("common.description")}</th>
                </tr>
              </thead>
              <tbody>
                {lines.map((row) => (
                  <tr
                    key={row.line_id}
                    onClick={() => handleSelect(row)}
                    className={selected?.line_id === row.line_id ? "active" : ""}
                  >
                    <td>{row.line_id}</td>
                    <td>{row.description_line}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="crud-stack">
          <div className="card crud-card crud-editor-card">
            <div className="crud-card-header">
              <div>
                <h3>{editorMode === "edit" ? t("masters.lines.edit") : t("masters.lines.new")}</h3>
                <p>{editorMode === "edit" ? t("masters.lines.selectToEdit") : t("masters.lines.new")}</p>
              </div>
            </div>
            {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
            {editorMode === "idle" ? (
              <div className="empty-state">{t("masters.lines.selectToEdit")}</div>
            ) : (
              <>
            {selected ? <div className="editor-banner">{t("fields.lineId")}: {selected.line_id}</div> : null}
            <form onSubmit={selected ? (event) => { event.preventDefault(); handleUpdate(); } : handleCreate} className="form">
              <div className="field">
                <label>{t("fields.lineId")}</label>
                <input value={form.line_id} onChange={(e) => setForm({ ...form, line_id: e.target.value })} disabled={!!selected} />
              </div>
              <div className="field">
                <label>{t("fields.description")}</label>
                <input value={form.description_line} onChange={(e) => setForm({ ...form, description_line: e.target.value })} />
              </div>
              <div className={`editor-actions ${selected ? "" : "compact-end"}`}>
                {selected ? (
                  <button className="danger" type="button" onClick={handleDelete} disabled={!canWrite || loading}>{t("common.delete")}</button>
                ) : (
                  <button className="ghost" type="button" onClick={() => { setEditorMode("idle"); setForm(emptyLine); setStatus(""); }}>
                    {t("common.cancel")}
                  </button>
                )}
                <button className={selected ? "secondary" : "primary"} type="submit" disabled={!canWrite || loading}>{selected ? t("common.update") : t("common.create")}</button>
              </div>
            </form>
              </>
            )}
            {status ? <div className="notice">{status}</div> : null}
          </div>
        </div>
      </div>
    </Layout>
  );
}
