import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyRoute = { routing_id: "", description_routing: "", line_id: "" };
const emptyProcess = { process_id: "", description: "", cell_id: "", sequence: 1, is_required: true, result_schema: [] };
const emptyModel = { model_id: "", is_active: true };
const emptyField = { code: "", label: "", type: "text", required: false, allowed_values: "" };

export default function RoutingsPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [routings, setRoutings] = useState([]);
  const [models, setModels] = useState([]);
  const [lines, setLines] = useState([]);
  const [cells, setCells] = useState([]);
  const [selected, setSelected] = useState(null);
  const [definition, setDefinition] = useState(null);
  const [routeForm, setRouteForm] = useState(emptyRoute);
  const [processForm, setProcessForm] = useState(emptyProcess);
  const [modelForm, setModelForm] = useState(emptyModel);
  const [fieldForm, setFieldForm] = useState(emptyField);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const canWrite = useMemo(() => auth.permissions?.includes("routings.write"), [auth]);

  const loadRoutings = async () => setRoutings(await request("/routings", { tenantId }));
  const loadDefinition = async (routingId) => setDefinition(await request(`/routings/${routingId}/definition`, { tenantId }));

  useEffect(() => {
    loadRoutings().catch(() => {});
    request("/models", { tenantId }).then(setModels).catch(() => {});
    request("/lines", { tenantId }).then(setLines).catch(() => {});
    request("/cells", { tenantId }).then(setCells).catch(() => {});
  }, [tenantId]);

  const selectRouting = async (routing) => {
    setSelected(routing);
    setRouteForm({ routing_id: routing.routing_id, description_routing: routing.description_routing, line_id: routing.line_id || "" });
    setEditorMode("edit");
    setStatus("");
    try { await loadDefinition(routing.routing_id); } catch (error) { setStatus(error.message); }
  };

  const createRouting = async (event) => {
    event.preventDefault();
    setLoading(true); setStatus("");
    try {
      const route = await request("/routings", { method: "POST", data: routeForm, tenantId, csrfToken });
      await loadRoutings();
      await selectRouting(route);
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const updateRouting = async () => {
    if (!selected) return;
    setLoading(true); setStatus("");
    try {
      await request(`/routings/${selected.routing_id}`, { method: "PATCH", data: { description_routing: routeForm.description_routing, line_id: routeForm.line_id }, tenantId, csrfToken });
      await loadRoutings(); await loadDefinition(selected.routing_id);
      setStatus("Routing actualizado");
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const deleteRouting = async () => {
    if (!selected) return;
    setLoading(true); setStatus("");
    try {
      await request(`/routings/${selected.routing_id}`, { method: "DELETE", tenantId, csrfToken });
      setSelected(null); setDefinition(null); setRouteForm(emptyRoute); setEditorMode("idle"); await loadRoutings();
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const addField = () => {
    if (!fieldForm.code.trim() || !fieldForm.label.trim()) { setStatus("Indica el código y la etiqueta del campo"); return; }
    if (fieldForm.type === "select" && !fieldForm.allowed_values.trim()) { setStatus("Un campo de lista necesita valores permitidos"); return; }
    if (processForm.result_schema.some((field) => field.code === fieldForm.code.trim())) { setStatus("El código de campo ya existe en este proceso"); return; }
    const field = {
      code: fieldForm.code.trim(), label: fieldForm.label.trim(), type: fieldForm.type, required: fieldForm.required,
      allowed_values: fieldForm.type === "select" ? fieldForm.allowed_values.split(",").map((value) => value.trim()).filter(Boolean) : [],
    };
    setProcessForm((current) => ({ ...current, result_schema: [...current.result_schema, field] }));
    setFieldForm(emptyField); setStatus("");
  };

  const createProcess = async (event) => {
    event.preventDefault();
    if (!selected) return;
    setLoading(true); setStatus("");
    try {
      await request(`/routings/${selected.routing_id}/processes`, { method: "POST", data: processForm, tenantId, csrfToken });
      setProcessForm({ ...emptyProcess, sequence: (definition?.processes.length || 0) + 2 });
      await loadDefinition(selected.routing_id);
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const deleteProcess = async (process) => {
    if (!selected) return;
    setLoading(true); setStatus("");
    try { await request(`/routings/${selected.routing_id}/processes/${process.process_id}`, { method: "DELETE", tenantId, csrfToken }); await loadDefinition(selected.routing_id); }
    catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const addModel = async (event) => {
    event.preventDefault();
    if (!selected) return;
    setLoading(true); setStatus("");
    try {
      await request("/routing-models", { method: "POST", data: { ...modelForm, routing_id: selected.routing_id }, tenantId, csrfToken });
      setModelForm(emptyModel); await loadDefinition(selected.routing_id);
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const deleteModel = async (model) => {
    if (!selected) return;
    setLoading(true); setStatus("");
    try { await request(`/routing-models/${model.model_id}`, { method: "DELETE", tenantId, csrfToken }); await loadDefinition(selected.routing_id); }
    catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  return (
    <Layout auth={auth} onLogout={onLogout} active="routings" tenantId={tenantId} setTenantId={setTenantId} lang={lang} setLang={setLang} t={t} theme={theme} setTheme={setTheme}>
      <div className="page-header-shell"><div className="card page-header"><div className="page-header-copy"><h2>Routings</h2><p>Define el flujo de procesos por referencia y los resultados que debe registrar cada operación.</p></div></div></div>
      <div className="crud-grid">
        <div className="card crud-card crud-list-card"><div className="crud-card-header"><div><h3>Routings</h3><p>Selecciona una ruta para configurar sus modelos y el flujo de celdas.</p></div><div className="row-space"><button className="secondary" type="button" disabled={!canWrite} onClick={() => { setSelected(null); setDefinition(null); setRouteForm(emptyRoute); setEditorMode("create"); setStatus(""); }}>Nueva ruta</button><div className="crud-card-metric">{routings.length}</div></div></div><div className="table-shell"><table className="table"><thead><tr><th>ID</th><th>Línea</th><th>Descripción</th></tr></thead><tbody>{routings.map((row) => <tr key={row.routing_id} className={selected?.routing_id === row.routing_id ? "active" : ""} onClick={() => selectRouting(row)}><td>{row.routing_id}</td><td>{row.line_id || "-"}</td><td>{row.description_routing}</td></tr>)}{!routings.length ? <tr><td colSpan="3"><div className="empty-state table-empty-state">Todavía no hay routings creados.</div></td></tr> : null}</tbody></table></div></div>
        <div className="crud-stack"><div className="card crud-card crud-editor-card"><div className="crud-card-header"><div><h3>{editorMode === "edit" ? "Routing seleccionado" : "Nueva ruta"}</h3><p>Selecciona la línea que contendrá este routing.</p></div></div>{editorMode === "idle" ? <div className="empty-state">Selecciona o crea un routing.</div> : <form className="form" onSubmit={selected ? (event) => { event.preventDefault(); updateRouting(); } : createRouting}><div className="field"><label>ID routing</label><input required value={routeForm.routing_id} disabled={!!selected} onChange={(event) => setRouteForm({ ...routeForm, routing_id: event.target.value })} /></div><div className="field"><label>Línea</label><select required value={routeForm.line_id} onChange={(event) => setRouteForm({ ...routeForm, line_id: event.target.value })}><option value="">Selecciona una línea</option>{lines.map((line) => <option key={line.line_id} value={line.line_id}>{line.line_id} · {line.description_line}</option>)}</select></div><div className="field"><label>Descripción</label><input required value={routeForm.description_routing} onChange={(event) => setRouteForm({ ...routeForm, description_routing: event.target.value })} /></div><div className="editor-actions">{selected ? <button className="danger" type="button" disabled={!canWrite || loading} onClick={deleteRouting}>Eliminar</button> : <button className="ghost" type="button" onClick={() => setEditorMode("idle")}>Cancelar</button>}<button className={selected ? "secondary" : "primary"} type="submit" disabled={!canWrite || loading}>{selected ? "Guardar" : "Crear"}</button></div></form>}</div></div>
      </div>
      {selected && definition ? <div className="crud-grid routing-detail-grid">
        <div className="card crud-card"><div className="crud-card-header"><div><h3>Modelos asignados</h3><p>Selecciona uno de los modelos maestros que debe seguir este routing.</p></div><div className="crud-card-metric">{definition.models.length}</div></div><form className="inline-form" onSubmit={addModel}><select required value={modelForm.model_id} onChange={(event) => setModelForm({ ...modelForm, model_id: event.target.value })}><option value="">Selecciona un modelo</option>{models.filter((model) => !definition.models.some((assigned) => assigned.model_id === model.model_id)).map((model) => <option key={model.model_id} value={model.model_id}>{model.model_id} · {model.description_model}</option>)}</select><button className="secondary" type="submit" disabled={!canWrite || loading}>Asignar</button></form><div className="chip-list">{definition.models.map((model) => <span className="status-chip" key={model.model_id}>{model.model_id}<button type="button" disabled={!canWrite || loading} onClick={() => deleteModel(model)}>x</button></span>)}{!definition.models.length ? <div className="empty-state">Sin modelos asignados.</div> : null}</div></div>
        <div className="card crud-card"><div className="crud-card-header"><div><h3>Flujo de celdas y procesos</h3><p>Ordena las celdas por las que pasa el modelo y define los campos de cada proceso.</p></div><div className="crud-card-metric">{definition.processes.length}</div></div><div className="routing-process-list">{definition.processes.map((process) => <div className="routing-process" key={process.process_id}><div><strong>{process.sequence}. {process.description}</strong><span>{process.cell_id} · {process.process_id} · {process.is_required ? "Obligatorio" : "Opcional"}</span><div className="chip-list">{process.result_schema.map((field) => <span className="status-chip" key={field.code}>{field.label}: {field.type}{field.required ? " *" : ""}</span>)}</div></div><button className="danger compact" type="button" disabled={!canWrite || loading} onClick={() => deleteProcess(process)}>Eliminar</button></div>)}{!definition.processes.length ? <div className="empty-state">Añade la primera celda y proceso del routing.</div> : null}</div><form className="form routing-process-form" onSubmit={createProcess}><div className="production-form-grid"><div className="field"><label>Celda</label><select required value={processForm.cell_id} onChange={(event) => setProcessForm({ ...processForm, cell_id: event.target.value })}><option value="">Selecciona una celda</option>{cells.map((cell) => <option key={cell.cell_id} value={cell.cell_id}>{cell.cell_id} · {cell.description_cell}</option>)}</select></div><div className="field"><label>ID proceso</label><input required value={processForm.process_id} onChange={(event) => setProcessForm({ ...processForm, process_id: event.target.value })} /></div><div className="field"><label>Descripción</label><input required value={processForm.description} onChange={(event) => setProcessForm({ ...processForm, description: event.target.value })} /></div><div className="field"><label>Orden</label><input type="number" min="1" required value={processForm.sequence} onChange={(event) => setProcessForm({ ...processForm, sequence: Number(event.target.value) })} /></div></div><label className="checkbox-item"><input type="checkbox" checked={processForm.is_required} onChange={(event) => setProcessForm({ ...processForm, is_required: event.target.checked })} /><span>Proceso obligatorio</span></label><div className="field-builder"><strong>Campos de resultado</strong><div className="production-form-grid"><input placeholder="Código" value={fieldForm.code} onChange={(event) => setFieldForm({ ...fieldForm, code: event.target.value })} /><input placeholder="Etiqueta" value={fieldForm.label} onChange={(event) => setFieldForm({ ...fieldForm, label: event.target.value })} /><select value={fieldForm.type} onChange={(event) => setFieldForm({ ...fieldForm, type: event.target.value })}><option value="text">Texto</option><option value="number">Número</option><option value="integer">Entero</option><option value="boolean">Sí / No</option><option value="select">Lista</option><option value="date">Fecha</option><option value="datetime">Fecha y hora</option></select>{fieldForm.type === "select" ? <input placeholder="Valores, separados por coma" value={fieldForm.allowed_values} onChange={(event) => setFieldForm({ ...fieldForm, allowed_values: event.target.value })} /> : null}</div><label className="checkbox-item"><input type="checkbox" checked={fieldForm.required} onChange={(event) => setFieldForm({ ...fieldForm, required: event.target.checked })} /><span>Campo obligatorio</span></label><button className="ghost" type="button" onClick={addField}>Añadir campo</button><div className="chip-list">{processForm.result_schema.map((field) => <span className="status-chip" key={field.code}>{field.label}<button type="button" onClick={() => setProcessForm((current) => ({ ...current, result_schema: current.result_schema.filter((item) => item.code !== field.code) }))}>x</button></span>)}</div></div><div className="editor-actions compact-end"><button className="primary" type="submit" disabled={!canWrite || loading}>Añadir proceso</button></div></form></div>
      </div> : null}
      {status ? <div className="notice">{status}</div> : null}
    </Layout>
  );
}
