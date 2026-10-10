import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyStatus = { status_id: "", description_status: "" };

export default function StatusesPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [statuses, setStatuses] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyStatus);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const canWrite = useMemo(() => auth.permissions?.includes("masters.write"), [auth]);

  const loadStatuses = async () => {
    const data = await request("/statuses", { tenantId });
    setStatuses(data);
  };

  useEffect(() => {
    loadStatuses().catch(() => {});
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/statuses", {
        method: "POST",
        data: form,
        tenantId,
        csrfToken,
      });
      setForm(emptyStatus);
      setEditorMode("idle");
      await loadStatuses();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
    setEditorMode("edit");
    setForm({ status_id: row.status_id, description_status: row.description_status });
  };

  const handleUpdate = async () => {
    if (!selected) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/statuses/${selected.status_id}`, {
        method: "PATCH",
        data: { description_status: form.description_status },
        tenantId,
        csrfToken,
      });
      await loadStatuses();
      setStatus(t("masters.statuses.updated"));
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
      await request(`/statuses/${selected.status_id}`, {
        method: "DELETE",
        tenantId,
        csrfToken,
      });
      setSelected(null);
      setForm(emptyStatus);
      setEditorMode("idle");
      await loadStatuses();
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
      active="statuses"
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
            <h2>{t("masters.statuses.title")}</h2>
            <p>{t("masters.statuses.subtitle")}</p>
          </div>
        </div>
      </div>

      <div className="crud-grid">
        <div className="card crud-card crud-list-card">
          <div className="crud-card-header">
            <div>
              <h3>{t("common.list")}</h3>
              <p>{t("masters.statuses.subtitle")}</p>
            </div>
            <div className="row-space">
              {canWrite ? (
                <button className="secondary" type="button" onClick={() => { setSelected(null); setForm(emptyStatus); setStatus(""); setEditorMode("create"); }}>
                  {t("masters.statuses.new")}
                </button>
              ) : null}
              <div className="crud-card-metric">{statuses.length}</div>
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
                {statuses.map((row) => (
                  <tr
                    key={row.status_id}
                    onClick={() => handleSelect(row)}
                    className={selected?.status_id === row.status_id ? "active" : ""}
                  >
                    <td>{row.status_id}</td>
                    <td>{row.description_status}</td>
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
                <h3>{editorMode === "edit" ? t("masters.statuses.edit") : t("masters.statuses.new")}</h3>
                <p>{editorMode === "edit" ? t("masters.statuses.selectToEdit") : t("masters.statuses.new")}</p>
              </div>
            </div>
            {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
            {editorMode === "idle" ? (
              <div className="empty-state">{t("masters.statuses.selectToEdit")}</div>
            ) : (
              <>
            {selected ? <div className="editor-banner">{t("fields.statusId")}: {selected.status_id}</div> : null}
            <form onSubmit={selected ? (event) => { event.preventDefault(); handleUpdate(); } : handleCreate} className="form">
              <div className="field">
                <label>{t("fields.statusId")}</label>
                <input value={form.status_id} onChange={(e) => setForm({ ...form, status_id: e.target.value })} disabled={!!selected} />
              </div>
              <div className="field">
                <label>{t("fields.description")}</label>
                <input value={form.description_status} onChange={(e) => setForm({ ...form, description_status: e.target.value })} />
              </div>
              <div className={`editor-actions ${selected ? "" : "compact-end"}`}>
                {selected ? (
                  <button className="danger" type="button" onClick={handleDelete} disabled={!canWrite || loading}>{t("common.delete")}</button>
                ) : (
                  <button className="ghost" type="button" onClick={() => { setEditorMode("idle"); setForm(emptyStatus); setStatus(""); }}>
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
