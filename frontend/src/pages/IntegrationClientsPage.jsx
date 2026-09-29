import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import IntegrationNavigation from "../ui/IntegrationNavigation.jsx";
import { request } from "../api.js";

const emptyClient = {
  client_id: "",
  description: "",
  api_key: "",
  plant_code: "",
  line_code: "",
  station_code: "",
  machine_code: "",
  source_system: "",
  is_active: true,
};

const generateApiKey = () => {
  const values = new Uint8Array(24);
  crypto.getRandomValues(values);
  return Array.from(values, (value) => value.toString(16).padStart(2, "0")).join("");
};

export default function IntegrationClientsPage({
  auth,
  onLogout,
  tenantId,
  setTenantId,
  csrfToken,
  t,
  lang,
  setLang,
  theme,
  setTheme,
}) {
  const [clients, setClients] = useState([]);
  const [masters, setMasters] = useState({ plants: [], lines: [], cells: [], cell_lines: [] });
  const [selectedClient, setSelectedClient] = useState(null);
  const [form, setForm] = useState(emptyClient);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastIssuedKey, setLastIssuedKey] = useState("");

  const canAdmin = useMemo(() => auth.permissions?.includes("production.admin"), [auth]);
  const currentTenant = tenantId || auth.tenant_id || "DEFAULT";

  const loadClients = async () => {
    if (!canAdmin) return;
    const [data, masterData] = await Promise.all([request("/production-ingest-clients", { tenantId: currentTenant }), request("/production-ingest-clients/master-data", { tenantId: currentTenant })]);
    setClients(data); setMasters(masterData);
  };

  useEffect(() => {
    loadClients().catch(() => {});
  }, [canAdmin, currentTenant]);

  const resetEditor = () => {
    setSelectedClient(null);
    setForm(emptyClient);
    setEditorMode("idle");
  };

  const openCreate = () => {
    setLastIssuedKey("");
    setStatus("");
    setForm({ ...emptyClient, api_key: generateApiKey() });
    setSelectedClient(null);
    setEditorMode("create");
  };

  const handleSelectClient = (client) => {
    setLastIssuedKey("");
    setStatus("");
    setSelectedClient(client);
    setForm({
      client_id: client.client_id,
      description: client.description,
      api_key: "",
      plant_code: client.plant_code || "",
      line_code: client.line_code || "",
      station_code: client.station_code || "",
      machine_code: client.machine_code || "",
      source_system: client.source_system || "",
      is_active: client.is_active,
    });
    setEditorMode("edit");
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      const payload = { ...form, client_id: form.client_id.trim(), description: form.description.trim() };
      await request("/production-ingest-clients", {
        method: "POST",
        data: payload,
        tenantId: currentTenant,
        csrfToken,
      });
      setLastIssuedKey(payload.api_key);
      setStatus(t("integrations.created"));
      setSelectedClient(null);
      setEditorMode("create");
      setForm({ ...emptyClient, api_key: generateApiKey() });
      await loadClients();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!selectedClient) return;
    setStatus("");
    setLoading(true);
    try {
      const payload = {
        description: form.description.trim(),
        plant_code: form.plant_code || null,
        line_code: form.line_code || null,
        station_code: form.station_code || null,
        machine_code: form.machine_code || null,
        source_system: form.source_system || null,
        is_active: form.is_active,
      };
      if (form.api_key) {
        payload.api_key = form.api_key;
      }
      await request(`/production-ingest-clients/${selectedClient.client_id}`, {
        method: "PATCH",
        data: payload,
        tenantId: currentTenant,
        csrfToken,
      });
      setLastIssuedKey(form.api_key || "");
      setForm((current) => ({ ...current, api_key: "" }));
      setStatus(form.api_key ? t("integrations.updatedWithKey") : t("integrations.updated"));
      await loadClients();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedClient) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/production-ingest-clients/${selectedClient.client_id}`, {
        method: "DELETE",
        tenantId: currentTenant,
        csrfToken,
      });
      setLastIssuedKey("");
      resetEditor();
      await loadClients();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleClientActive = async (event, client) => {
    event.stopPropagation();
    setLoading(true);
    setStatus("");
    try {
      const isActive = !client.is_active;
      await request(`/production-ingest-clients/${client.client_id}`, {
        method: "PATCH",
        data: { is_active: isActive },
        tenantId: currentTenant,
        csrfToken,
      });
      if (selectedClient?.client_id === client.client_id) {
        setSelectedClient({ ...selectedClient, is_active: isActive });
        setForm((current) => ({ ...current, is_active: isActive }));
      }
      await loadClients();
      setStatus(isActive ? "Cliente activado" : "Cliente desactivado");
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
      active="integrations"
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
            <h2>{t("integrations.title")}</h2>
            <p>{t("integrations.subtitle")}</p>
          </div>
          <div className="page-header-meta">
            <div className="badge">{t("common.tenant")}: {currentTenant}</div>
          </div>
        </div>
      </div>
      <IntegrationNavigation active="clients" />

      <div className="crud-layout">
        <div className="crud-grid">
          <div className="card crud-card crud-list-card">
            <div className="crud-card-header">
              <div>
                <h3>{t("common.list")}</h3>
                <p>{t("integrations.listHint")}</p>
              </div>
              <div className="row-space">
                {canAdmin ? (
                  <button className="secondary" type="button" onClick={openCreate}>
                    {t("integrations.new")}
                  </button>
                ) : null}
                <div className="crud-card-metric">{clients.length}</div>
              </div>
            </div>
            <div className="table-shell">
              <table className="table">
                <thead>
                  <tr>
                    <th>{t("integrations.clientId")}</th>
                    <th>{t("common.description")}</th>
                    <th>{t("reports.lineCode")}</th>
                    <th>{t("common.status")}</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr
                      key={client.client_id}
                      onClick={() => handleSelectClient(client)}
                      className={selectedClient?.client_id === client.client_id ? "active" : ""}
                    >
                      <td>{client.client_id}</td>
                      <td>{client.description}</td>
                      <td>{client.line_code || "-"}</td>
                      <td>
                        <span className={`status-chip ${client.is_active ? "ok" : ""}`}>
                          {client.is_active ? t("integrations.active") : t("integrations.inactive")}
                        </span>
                      </td>
                      <td>
                        {canAdmin ? (
                          <div className="table-actions">
                            <button className="ghost compact" type="button" disabled={loading} onClick={(event) => { event.stopPropagation(); handleSelectClient(client); }}>Editar</button>
                            <button className="secondary compact" type="button" disabled={loading} onClick={(event) => toggleClientActive(event, client)}>
                              {client.is_active ? "Desactivar" : "Activar"}
                            </button>
                          </div>
                        ) : null}
                      </td>
                    </tr>
                  ))}
                  {!clients.length ? (
                    <tr>
                      <td colSpan="5">
                        <div className="empty-state table-empty-state">{t("integrations.empty")}</div>
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card crud-card crud-editor-card">
            <div className="crud-card-header">
              <div>
                <h3>{editorMode === "edit" ? t("integrations.edit") : t("integrations.new")}</h3>
                <p>{t("integrations.editorHint")}</p>
              </div>
              <div className="crud-card-metric">{editorMode === "edit" ? "API" : "NEW"}</div>
            </div>
            {!canAdmin && <p className="muted">{t("integrations.noAccess")}</p>}
            {editorMode === "idle" ? (
              <div className="empty-state">{t("integrations.ready")}</div>
            ) : (
              <>
                {selectedClient ? <div className="editor-banner">{t("integrations.clientId")}: {selectedClient.client_id}</div> : null}
                {lastIssuedKey ? (
                  <div className="editor-banner">
                    <strong>{t("integrations.generatedKey")}:</strong> <code>{lastIssuedKey}</code>
                  </div>
                ) : null}
                <form
                  onSubmit={selectedClient ? (event) => { event.preventDefault(); handleUpdate(); } : handleCreate}
                  className="form"
                >
                  <div className="production-form-grid">
                    <div className="field">
                      <label>{t("integrations.clientId")}</label>
                      <input
                        value={form.client_id}
                        onChange={(event) => setForm({ ...form, client_id: event.target.value })}
                        required
                        disabled={!!selectedClient}
                      />
                    </div>
                    <div className="field">
                      <label>{t("common.description")}</label>
                      <input
                        value={form.description}
                        onChange={(event) => setForm({ ...form, description: event.target.value })}
                        required
                      />
                    </div>
                    <div className="field">
                      <label>{t("integrations.apiKey")}</label>
                      <input
                        value={form.api_key}
                        onChange={(event) => setForm({ ...form, api_key: event.target.value })}
                        placeholder={selectedClient ? t("integrations.keepKey") : ""}
                        required={!selectedClient}
                      />
                    </div>
                    <div className="field">
                      <label>{t("reports.plantCode")}</label>
                      <select required value={form.plant_code} onChange={(event) => setForm({ ...form, plant_code: event.target.value })}><option value="">Selecciona</option>{masters.plants.map((x) => <option key={x.id} value={x.id}>{x.id} — {x.description}</option>)}</select>
                    </div>
                    <div className="field">
                      <label>{t("reports.lineCode")}</label>
                      <select required value={form.line_code} onChange={(event) => setForm({ ...form, line_code: event.target.value, machine_code: "" })}><option value="">Selecciona</option>{masters.lines.map((x) => <option key={x.id} value={x.id}>{x.id} — {x.description}</option>)}</select>
                    </div>
                    <div className="field">
                      <label>{t("reports.stationCode")}</label>
                      <input value={form.station_code} onChange={(event) => setForm({ ...form, station_code: event.target.value })} />
                    </div>
                    <div className="field">
                      <label>Celda / máquina</label>
                      <select required value={form.machine_code} onChange={(event) => setForm({ ...form, machine_code: event.target.value })}><option value="">Selecciona</option>{masters.cells.filter((x) => !form.line_code || masters.cell_lines.some((link) => link.cell_id === x.id && link.line_id === form.line_code)).map((x) => <option key={x.id} value={x.id}>{x.id} — {x.description}</option>)}</select>
                    </div>
                    <div className="field">
                      <label>{t("integrations.sourceSystem")}</label>
                      <input value={form.source_system} onChange={(event) => setForm({ ...form, source_system: event.target.value })} />
                    </div>
                  </div>

                  <div className="stack-actions">
                    <button
                      className="secondary"
                      type="button"
                      onClick={() => setForm((current) => ({ ...current, api_key: generateApiKey() }))}
                    >
                      {t("integrations.generateKey")}
                    </button>
                  </div>

                  {!selectedClient ? (
                    <div className="editor-actions compact-end">
                      <button className="ghost" type="button" onClick={resetEditor}>
                        {t("common.cancel")}
                      </button>
                      <button className="primary" type="submit" disabled={!canAdmin || loading}>
                        {t("common.create")}
                      </button>
                    </div>
                  ) : (
                    <div className="editor-actions">
                      <button className="danger" type="button" onClick={handleDelete} disabled={!canAdmin || loading}>
                        {t("common.delete")}
                      </button>
                      <button className="secondary" type="button" onClick={handleUpdate} disabled={!canAdmin || loading}>
                        {t("common.update")}
                      </button>
                    </div>
                  )}
                </form>
              </>
            )}
          </div>
        </div>
      </div>

      {status ? <div className="notice">{status}</div> : null}
    </Layout>
  );
}
