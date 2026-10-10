import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyPlant = { plant_id: "", description_plant: "" };

export default function PlantsPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [plants, setPlants] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyPlant);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const canWrite = useMemo(() => auth.permissions?.includes("masters.write"), [auth]);

  const loadPlants = async () => setPlants(await request("/plants", { tenantId }));
  useEffect(() => { loadPlants().catch(() => {}); }, [tenantId]);

  const createPlant = async (event) => {
    event.preventDefault(); setStatus(""); setLoading(true);
    try {
      await request("/plants", { method: "POST", data: form, tenantId, csrfToken });
      setForm(emptyPlant); setEditorMode("idle"); await loadPlants();
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const updatePlant = async () => {
    if (!selected) return;
    setStatus(""); setLoading(true);
    try {
      await request(`/plants/${selected.plant_id}`, { method: "PATCH", data: { description_plant: form.description_plant }, tenantId, csrfToken });
      await loadPlants(); setStatus(t("masters.plants.updated"));
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const deletePlant = async () => {
    if (!selected) return;
    setStatus(""); setLoading(true);
    try {
      await request(`/plants/${selected.plant_id}`, { method: "DELETE", tenantId, csrfToken });
      setSelected(null); setForm(emptyPlant); setEditorMode("idle"); await loadPlants();
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const selectPlant = (plant) => {
    setSelected(plant); setForm({ plant_id: plant.plant_id, description_plant: plant.description_plant }); setEditorMode("edit"); setStatus("");
  };

  return <Layout auth={auth} onLogout={onLogout} active="plants" tenantId={tenantId} setTenantId={setTenantId} lang={lang} setLang={setLang} t={t} theme={theme} setTheme={setTheme}>
    <div className="page-header-shell"><div className="card page-header"><div className="page-header-copy"><h2>{t("masters.plants.title")}</h2><p>{t("masters.plants.subtitle")}</p></div></div></div>
    <div className="crud-grid">
      <div className="card crud-card crud-list-card"><div className="crud-card-header"><div><h3>{t("common.list")}</h3><p>{t("masters.plants.subtitle")}</p></div><div className="row-space">{canWrite ? <button className="secondary" type="button" onClick={() => { setSelected(null); setForm(emptyPlant); setStatus(""); setEditorMode("create"); }}>{t("masters.plants.new")}</button> : null}<div className="crud-card-metric">{plants.length}</div></div></div><div className="table-shell"><table className="table"><thead><tr><th>{t("common.id")}</th><th>{t("common.description")}</th></tr></thead><tbody>{plants.map((plant) => <tr key={plant.plant_id} onClick={() => selectPlant(plant)} className={selected?.plant_id === plant.plant_id ? "active" : ""}><td>{plant.plant_id}</td><td>{plant.description_plant}</td></tr>)}</tbody></table></div></div>
      <div className="crud-stack"><div className="card crud-card crud-editor-card"><div className="crud-card-header"><div><h3>{editorMode === "edit" ? t("masters.plants.edit") : t("masters.plants.new")}</h3><p>{editorMode === "edit" ? t("masters.plants.selectToEdit") : t("masters.plants.new")}</p></div></div>{!canWrite ? <p className="muted">{t("common.noPermission")}</p> : null}{editorMode === "idle" ? <div className="empty-state">{t("masters.plants.selectToEdit")}</div> : <><>{selected ? <div className="editor-banner">{t("nav.plants")}: {selected.plant_id}</div> : null}</><form className="form" onSubmit={selected ? (event) => { event.preventDefault(); updatePlant(); } : createPlant}><div className="field"><label>{t("common.id")}</label><input value={form.plant_id} onChange={(event) => setForm({ ...form, plant_id: event.target.value })} disabled={!!selected} required /></div><div className="field"><label>{t("common.description")}</label><input value={form.description_plant} onChange={(event) => setForm({ ...form, description_plant: event.target.value })} required /></div><div className={`editor-actions ${selected ? "" : "compact-end"}`}>{selected ? <button className="danger" type="button" disabled={!canWrite || loading} onClick={deletePlant}>{t("common.delete")}</button> : <button className="ghost" type="button" onClick={() => { setEditorMode("idle"); setForm(emptyPlant); setStatus(""); }}>{t("common.cancel")}</button>}<button className={selected ? "secondary" : "primary"} type="submit" disabled={!canWrite || loading}>{selected ? t("common.update") : t("common.create")}</button></div></form></>}{status ? <div className="notice">{status}</div> : null}</div></div>
    </div>
  </Layout>;
}
