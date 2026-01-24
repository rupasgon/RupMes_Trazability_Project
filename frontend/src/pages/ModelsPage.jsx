import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyModel = { model_id: "", description_model: "" };

export default function ModelsPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [models, setModels] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyModel);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const canWrite = useMemo(() => auth.permissions?.includes("masters.write"), [auth]);

  const loadModels = async () => {
    const data = await request("/models", { tenantId });
    setModels(data);
  };

  useEffect(() => {
    loadModels().catch(() => {});
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/models", {
        method: "POST",
        data: form,
        tenantId,
        csrfToken,
      });
      setForm(emptyModel);
      await loadModels();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (row) => {
    setSelected(row);
    setForm({ model_id: row.model_id, description_model: row.description_model });
  };

  const handleUpdate = async () => {
    if (!selected) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/models/${selected.model_id}`, {
        method: "PATCH",
        data: { description_model: form.description_model },
        tenantId,
        csrfToken,
      });
      await loadModels();
      setStatus(t("masters.models.updated"));
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
      await request(`/models/${selected.model_id}`, {
        method: "DELETE",
        tenantId,
        csrfToken,
      });
      setSelected(null);
      setForm(emptyModel);
      await loadModels();
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
      active="models"
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
          <h2>{t("masters.models.title")}</h2>
          <p className="muted">{t("masters.models.subtitle")}</p>
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
              {models.map((row) => (
                <tr
                  key={row.model_id}
                  onClick={() => handleSelect(row)}
                  className={selected?.model_id === row.model_id ? "active" : ""}
                >
                  <td>{row.model_id}</td>
                  <td>{row.description_model}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>{t("masters.models.new")}</h3>
          {!canWrite && <p className="muted">{t("common.noPermission")}</p>}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("fields.modelId")}</label>
              <input value={form.model_id} onChange={(e) => setForm({ ...form, model_id: e.target.value })} />
            </div>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_model} onChange={(e) => setForm({ ...form, description_model: e.target.value })} />
            </div>
            <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
          </form>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("masters.models.edit")}</h3>
        {!selected ? (
          <p className="muted">{t("masters.models.selectToEdit")}</p>
        ) : (
          <>
            <p className="muted">{t("fields.modelId")}: {selected.model_id}</p>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input value={form.description_model} onChange={(e) => setForm({ ...form, description_model: e.target.value })} />
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
