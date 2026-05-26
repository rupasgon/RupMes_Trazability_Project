import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyCell = { cell_id: "", description_cell: "" };

export default function CellsPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [cells, setCells] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyCell);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const canWrite = useMemo(() => auth.permissions?.includes("masters.write"), [auth]);

  const loadCells = async () => {
    const data = await request("/cells", { tenantId });
    setCells(data);
  };

  useEffect(() => {
    loadCells().catch(() => {});
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/cells", {
        method: "POST",
        data: form,
        tenantId,
        csrfToken,
      });
      setForm(emptyCell);
      setEditorMode("idle");
      await loadCells();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
    setEditorMode("edit");
    setForm({ cell_id: row.cell_id, description_cell: row.description_cell });
  };

  const handleUpdate = async () => {
    if (!selected) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/cells/${selected.cell_id}`, {
        method: "PATCH",
        data: { description_cell: form.description_cell },
        tenantId,
        csrfToken,
      });
      await loadCells();
      setStatus(t("masters.cells.updated"));
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
      await request(`/cells/${selected.cell_id}`, {
        method: "DELETE",
        tenantId,
        csrfToken,
      });
      setSelected(null);
      setForm(emptyCell);
      setEditorMode("idle");
      await loadCells();
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
      active="cells"
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
            <h2>{t("masters.cells.title")}</h2>
            <p>{t("masters.cells.subtitle")}</p>
          </div>
        </div>
      </div>

      <div className="crud-grid">
        <div className="card crud-card crud-list-card">
          <div className="crud-card-header">
            <div>
              <h3>{t("common.list")}</h3>
              <p>{t("masters.cells.subtitle")}</p>
            </div>
            <div className="row-space">
              {canWrite ? (
                <button className="secondary" type="button" onClick={() => { setSelected(null); setForm(emptyCell); setStatus(""); setEditorMode("create"); }}>
                  {t("masters.cells.new")}
                </button>
              ) : null}
              <div className="crud-card-metric">{cells.length}</div>
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
                {cells.map((row) => (
                  <tr
                    key={row.cell_id}
                    onClick={() => handleSelect(row)}
                    className={selected?.cell_id === row.cell_id ? "active" : ""}
                  >
                    <td>{row.cell_id}</td>
                    <td>{row.description_cell}</td>
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
                <h3>{editorMode === "edit" ? t("masters.cells.edit") : t("masters.cells.new")}</h3>
                <p>{editorMode === "edit" ? t("masters.cells.selectToEdit") : t("masters.cells.new")}</p>
              </div>
            </div>
            {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
            {editorMode === "idle" ? (
              <div className="empty-state">{t("masters.cells.selectToEdit")}</div>
            ) : (
              <>
            {selected ? <div className="editor-banner">{t("fields.cellId")}: {selected.cell_id}</div> : null}
            <form onSubmit={selected ? (event) => { event.preventDefault(); handleUpdate(); } : handleCreate} className="form">
              <div className="field">
                <label>{t("fields.cellId")}</label>
                <input value={form.cell_id} onChange={(e) => setForm({ ...form, cell_id: e.target.value })} disabled={!!selected} />
              </div>
              <div className="field">
                <label>{t("fields.description")}</label>
                <input value={form.description_cell} onChange={(e) => setForm({ ...form, description_cell: e.target.value })} />
              </div>
              <div className={`editor-actions ${selected ? "" : "compact-end"}`}>
                {selected ? (
                  <button className="danger" type="button" onClick={handleDelete} disabled={!canWrite || loading}>{t("common.delete")}</button>
                ) : (
                  <button className="ghost" type="button" onClick={() => { setEditorMode("idle"); setForm(emptyCell); setStatus(""); }}>
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
