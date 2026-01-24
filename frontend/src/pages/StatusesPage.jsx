import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyStatus = { status_id: "", description_status: "" };

export default function StatusesPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [statuses, setStatuses] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyStatus);
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
      await loadStatuses();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
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
      <div className="section-head">
        <div>
          <h2>{t("masters.statuses.title")}</h2>
          <p className="muted">{t("masters.statuses.subtitle")}</p>
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

        <div className="card">
          <h3>{t("masters.statuses.new")}</h3>
          {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("fields.statusId")}</label>
              <input value={form.status_id} onChange={(e) => setForm({ ...form, status_id: e.target.value })} />
            </div>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_status} onChange={(e) => setForm({ ...form, description_status: e.target.value })} />
            </div>
            <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
          </form>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("masters.statuses.edit")}</h3>
        {!selected ? (
          <p className="muted">{t("masters.statuses.selectToEdit")}</p>
        ) : (
          <>
            <p className="muted">{t("fields.statusId")}: {selected.status_id}</p>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_status} onChange={(e) => setForm({ ...form, description_status: e.target.value })} />
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
