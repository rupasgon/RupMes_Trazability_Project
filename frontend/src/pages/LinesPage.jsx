import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyLine = { line_id: "", description_line: "" };

export default function LinesPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [lines, setLines] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyLine);
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
      await loadLines();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
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
      <div className="section-head">
        <div>
          <h2>{t("masters.lines.title")}</h2>
          <p className="muted">{t("masters.lines.subtitle")}</p>
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

        <div className="card">
          <h3>{t("masters.lines.new")}</h3>
          {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("fields.lineId")}</label>
              <input value={form.line_id} onChange={(e) => setForm({ ...form, line_id: e.target.value })} />
            </div>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_line} onChange={(e) => setForm({ ...form, description_line: e.target.value })} />
            </div>
            <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
          </form>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("masters.lines.edit")}</h3>
        {!selected ? (
          <p className="muted">{t("masters.lines.selectToEdit")}</p>
        ) : (
          <>
            <p className="muted">{t("fields.lineId")}: {selected.line_id}</p>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_line} onChange={(e) => setForm({ ...form, description_line: e.target.value })} />
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
