import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyCell = { cell_id: "", description_cell: "" };

export default function CellsPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [cells, setCells] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyCell);
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
      await loadCells();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
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
      <div className="section-head">
        <div>
          <h2>{t("masters.cells.title")}</h2>
          <p className="muted">{t("masters.cells.subtitle")}</p>
        </div>
      </div>

      <div className="grid two">
        <div className="card">
          <h3>{t("common.list")}</h3>
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

        <div className="card">
          <h3>{t("masters.cells.new")}</h3>
          {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("fields.cellId")}</label>
              <input value={form.cell_id} onChange={(e) => setForm({ ...form, cell_id: e.target.value })} />
            </div>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_cell} onChange={(e) => setForm({ ...form, description_cell: e.target.value })} />
            </div>
            <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
          </form>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("masters.cells.edit")}</h3>
        {!selected ? (
          <p className="muted">{t("masters.cells.selectToEdit")}</p>
        ) : (
          <>
            <p className="muted">{t("fields.cellId")}: {selected.cell_id}</p>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_cell} onChange={(e) => setForm({ ...form, description_cell: e.target.value })} />
            </div>
            <div className="row-space">
              <button className="secondary" onClick={handleUpdate} disabled={!canWrite || loading}>{t("common.update")}</button>
              <button className="danger" onClick={handleDelete} disabled={!canWrite || loading}>{t("common.delete")}</button>
            </div>
          </>
        )}
        {status ? <div className="notice">{status}</div> : null}
      </div>
    </Layout>
  );
}
