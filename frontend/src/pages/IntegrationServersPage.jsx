import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import IntegrationNavigation from "../ui/IntegrationNavigation.jsx";
import { request } from "../api.js";

const emptyServer = { server_id: "", description: "", protocol: "oracle_apex", base_url: "", api_endpoint: "/scm/workOrderLine", auth_type: "oauth2_client_credentials", secret_ref: "", oauth_client_id: "", oauth_client_secret: "", token_url: "", oauth_scope: "", token_refresh_buffer_seconds: 60, timeout_seconds: 30, verify_tls: true, is_active: true };
const emptyRule = { rule_id: "", description: "", server_id: "", dispatch_interval_seconds: 30, batch_size: 100, max_retries: 5, lot_mask: "", is_active: true, report_filter: '{"result":"OK"}', mapping_config: '{"item":"product_code","lot":"generated_lot","quantity":"count"}' };

export default function IntegrationServersPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [servers, setServers] = useState([]);
  const [rules, setRules] = useState([]);
  const [server, setServer] = useState(emptyServer);
  const [rule, setRule] = useState(emptyRule);
  const [selectedServer, setSelectedServer] = useState(null);
  const [selectedRule, setSelectedRule] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const canAdmin = useMemo(() => auth.permissions?.includes("production.admin"), [auth]);
  const currentTenant = tenantId || auth.tenant_id || "DEFAULT";

  const load = async () => {
    const [serverRows, ruleRows] = await Promise.all([
      request("/integration-servers", { tenantId: currentTenant }),
      request("/integration-delivery-rules", { tenantId: currentTenant }),
    ]);
    setServers(serverRows);
    setRules(ruleRows);
  };

  useEffect(() => { if (canAdmin) load().catch((error) => setStatus(error.message)); }, [canAdmin, currentTenant]);

  const saveServer = async (event) => {
    event.preventDefault(); setLoading(true); setStatus("");
    try {
      const data = { ...server, timeout_seconds: Number(server.timeout_seconds), token_refresh_buffer_seconds: Number(server.token_refresh_buffer_seconds) };
      const path = selectedServer ? `/integration-servers/${selectedServer.server_id}` : "/integration-servers";
      if (selectedServer) delete data.server_id;
      await request(path, { method: selectedServer ? "PATCH" : "POST", data, tenantId: currentTenant, csrfToken });
      setServer(emptyServer); setSelectedServer(null); await load(); setStatus(selectedServer ? "Servidor ERP actualizado" : "Servidor ERP creado");
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const saveRule = async (event) => {
    event.preventDefault(); setLoading(true); setStatus("");
    try {
      const data = { ...rule, server_id: Number(rule.server_id), dispatch_interval_seconds: Number(rule.dispatch_interval_seconds), batch_size: Number(rule.batch_size), max_retries: Number(rule.max_retries), lot_mask: rule.lot_mask || null, report_filter: JSON.parse(rule.report_filter || "{}"), mapping_config: JSON.parse(rule.mapping_config || "{}") };
      const path = selectedRule ? `/integration-delivery-rules/${selectedRule.rule_id}` : "/integration-delivery-rules";
      if (selectedRule) delete data.rule_id;
      await request(path, { method: selectedRule ? "PATCH" : "POST", data, tenantId: currentTenant, csrfToken });
      setRule(emptyRule); setSelectedRule(null); await load(); setStatus(selectedRule ? "Regla de envío actualizada" : "Regla de envío creada");
    } catch (error) { setStatus(error.message || "El JSON de filtro o mapeo no es válido"); } finally { setLoading(false); }
  };

  const remove = async (path) => {
    if (!window.confirm("¿Eliminar esta configuración?")) return;
    try { await request(path, { method: "DELETE", tenantId: currentTenant, csrfToken }); await load(); } catch (error) { setStatus(error.message); }
  };

  const toggleRuleActive = async (item) => {
    setLoading(true); setStatus("");
    try {
      const isActive = !item.is_active;
      await request(`/integration-delivery-rules/${item.rule_id}`, {
        method: "PATCH",
        data: { is_active: isActive },
        tenantId: currentTenant,
        csrfToken,
      });
      await load();
      setStatus(isActive ? "Regla activada" : "Regla desactivada");
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const toggleServerActive = async (item) => {
    setLoading(true); setStatus("");
    try {
      const isActive = !item.is_active;
      await request(`/integration-servers/${item.server_id}`, {
        method: "PATCH",
        data: { is_active: isActive },
        tenantId: currentTenant,
        csrfToken,
      });
      await load();
      setStatus(isActive ? "Servidor ERP activado" : "Servidor ERP desactivado");
    } catch (error) { setStatus(error.message); } finally { setLoading(false); }
  };

  const testServer = async (item) => {
    setLoading(true); setStatus("");
    try {
      const result = await request(`/integration-servers/${item.server_id}/test`, { method: "POST", tenantId: currentTenant, csrfToken });
      setStatus(`Conexión correcta: token OAuth obtenido${result.expires_in ? ` (caduca en ${result.expires_in} s)` : ""}.`);
    } catch (error) { setStatus(`Prueba de conexión fallida: ${error.message}`); } finally { setLoading(false); }
  };

  const editServer = (item) => {
    setSelectedServer(item);
    setServer({ ...emptyServer, ...item, base_url: item.base_url || "", secret_ref: item.secret_ref || "" });
    setStatus("");
  };

  const editRule = (item) => {
    setSelectedRule(item);
    setRule({ ...emptyRule, ...item, server_id: String(item.server_id), report_filter: JSON.stringify(item.report_filter || {}, null, 2), mapping_config: JSON.stringify(item.mapping_config || {}, null, 2), lot_mask: item.lot_mask || "" });
    setStatus("");
  };

  return <Layout auth={auth} onLogout={onLogout} active="integrations" tenantId={tenantId} setTenantId={setTenantId} lang={lang} setLang={setLang} t={t} theme={theme} setTheme={setTheme}>
    <div className="page-header-shell"><div className="card page-header"><div className="page-header-copy"><h2>Servidores ERP y reglas de envío</h2><p>RupMes selecciona reportes ya almacenados y los entrega a cada destino externo.</p></div><div className="page-header-meta"><div className="badge">{t("common.tenant")}: {currentTenant}</div></div></div></div>
    <IntegrationNavigation active="servers" />
    {!canAdmin ? <p className="notice">No tienes permiso para administrar integraciones.</p> : <div className="crud-grid">
      <section className="card crud-card">
        <div className="crud-card-header"><div><h3>Servidores ERP</h3><p>Destino reutilizable. Las credenciales OAuth se cifran antes de guardarse y nunca vuelven a mostrarse.</p></div><div className="crud-card-metric">{servers.length}</div></div>
        <form className="form" onSubmit={saveServer}><div className="production-form-grid">
          <div className="field"><label>ID</label><input required disabled={!!selectedServer} value={server.server_id} onChange={(event) => setServer({ ...server, server_id: event.target.value })} placeholder="ORACLE_BMW" /></div>
          <div className="field"><label>Descripción</label><input required value={server.description} onChange={(event) => setServer({ ...server, description: event.target.value })} /></div>
          <div className="field"><label>Protocolo</label><select value={server.protocol} onChange={(event) => setServer({ ...server, protocol: event.target.value })}><option value="oracle_apex">Oracle APEX</option><option value="http">HTTP API</option><option value="sftp">SFTP</option></select></div>
          <div className="field"><label>Autenticación</label><select value={server.auth_type} onChange={(event) => setServer({ ...server, auth_type: event.target.value })}><option value="oauth2_client_credentials">OAuth2 Client Credentials</option><option value="bearer_token">Bearer token</option><option value="none">Sin autenticación</option></select></div>
          <div className="field"><label>URL base</label><input value={server.base_url} onChange={(event) => setServer({ ...server, base_url: event.target.value })} placeholder="https://erp.example/ords/apps" /></div>
          <div className="field"><label>Endpoint de envío</label><input value={server.api_endpoint} onChange={(event) => setServer({ ...server, api_endpoint: event.target.value })} placeholder="/scm/workOrderLine" /></div>
          <div className="field"><label>Referencia a secreto</label><input value={server.secret_ref} onChange={(event) => setServer({ ...server, secret_ref: event.target.value })} placeholder="ORACLE_BMW_OAUTH" /></div>
          {server.auth_type === "oauth2_client_credentials" && <><div className="field"><label>Client ID OAuth2</label><input value={server.oauth_client_id} onChange={(event) => setServer({ ...server, oauth_client_id: event.target.value })} placeholder={selectedServer?.credentials_configured ? "Configurado; escribe otro para reemplazarlo" : "Client ID de Oracle"} /></div><div className="field"><label>Client secret OAuth2</label><input type="password" autoComplete="new-password" value={server.oauth_client_secret} onChange={(event) => setServer({ ...server, oauth_client_secret: event.target.value })} placeholder={selectedServer?.credentials_configured ? "Configurado; deja vacío para conservarlo" : "Client secret de Oracle"} /></div><div className="field"><label>URL de token OAuth2</label><input required value={server.token_url} onChange={(event) => setServer({ ...server, token_url: event.target.value })} placeholder="https://erp.example/ords/apps/oauth/token" /></div><div className="field"><label>Scope OAuth2 (opcional)</label><input value={server.oauth_scope} onChange={(event) => setServer({ ...server, oauth_scope: event.target.value })} /></div><div className="field"><label>Margen renovación token (s)</label><input type="number" min="0" value={server.token_refresh_buffer_seconds} onChange={(event) => setServer({ ...server, token_refresh_buffer_seconds: event.target.value })} /></div></>}
          <div className="field"><label>Timeout (s)</label><input type="number" min="1" value={server.timeout_seconds} onChange={(event) => setServer({ ...server, timeout_seconds: event.target.value })} /></div>
        </div><div className="editor-actions compact-end">{selectedServer && <button className="ghost" type="button" onClick={() => { setSelectedServer(null); setServer(emptyServer); }}>Cancelar</button>}<button className="primary" disabled={loading}>{selectedServer ? "Guardar servidor ERP" : "Crear servidor ERP"}</button></div></form>
        <div className="table-shell"><table className="table"><thead><tr><th>ID</th><th>Destino</th><th>Protocolo</th><th>Credenciales</th><th>Estado</th><th /></tr></thead><tbody>{servers.map((item) => <tr key={item.id}><td>{item.server_id}</td><td>{item.description}</td><td>{item.protocol}</td><td>{item.auth_type === "oauth2_client_credentials" ? <span className={`status-chip ${item.credentials_configured ? "ok" : ""}`}>{item.credentials_configured ? "Configuradas" : "Pendientes"}</span> : "-"}</td><td><span className={`status-chip ${item.is_active ? "ok" : ""}`}>{item.is_active ? "Activo" : "Inactivo"}</span></td><td><div className="table-actions"><button className="ghost compact" type="button" onClick={() => editServer(item)}>Editar</button><button className="secondary compact" type="button" disabled={loading || !item.credentials_configured} onClick={() => testServer(item)}>Probar conexión</button><button className="secondary compact" type="button" disabled={loading} onClick={() => toggleServerActive(item)}>{item.is_active ? "Desactivar" : "Activar"}</button><button className="danger compact" type="button" onClick={() => remove(`/integration-servers/${item.server_id}`)}>Eliminar</button></div></td></tr>)}{!servers.length && <tr><td colSpan="6"><div className="empty-state table-empty-state">Crea un destino ERP antes de definir una regla de envío.</div></td></tr>}</tbody></table></div>
      </section>
      <section className="card crud-card">
        <div className="crud-card-header"><div><h3>Reglas de envío</h3><p>Seleccionan registros de <code>production_report</code>, construyen el lote y los preparan para el destino ERP.</p></div><div className="crud-card-metric">{rules.length}</div></div>
        <form className="form" onSubmit={saveRule}><div className="production-form-grid">
          <div className="field"><label>ID regla</label><input required disabled={!!selectedRule} value={rule.rule_id} onChange={(event) => setRule({ ...rule, rule_id: event.target.value })} placeholder="BMW_OK_TO_ORACLE" /></div>
          <div className="field"><label>Descripción</label><input required value={rule.description} onChange={(event) => setRule({ ...rule, description: event.target.value })} /></div>
          <div className="field"><label>Servidor destino</label><select required value={rule.server_id} onChange={(event) => setRule({ ...rule, server_id: event.target.value })}><option value="">Selecciona</option>{servers.filter((item) => item.is_active).map((item) => <option key={item.id} value={item.id}>{item.server_id}</option>)}</select></div>
          <div className="field"><label>Intervalo de envío (s)</label><input type="number" min="1" value={rule.dispatch_interval_seconds} onChange={(event) => setRule({ ...rule, dispatch_interval_seconds: event.target.value })} /></div>
          <div className="field"><label>Tamaño de lote</label><input type="number" min="1" value={rule.batch_size} onChange={(event) => setRule({ ...rule, batch_size: event.target.value })} /></div>
          <div className="field"><label>Reintentos máximos</label><input type="number" min="0" value={rule.max_retries} onChange={(event) => setRule({ ...rule, max_retries: event.target.value })} /></div>
          <div className="field"><label>Máscara de lote</label><input value={rule.lot_mask} onChange={(event) => setRule({ ...rule, lot_mask: event.target.value })} placeholder="ESSVIND-DCS-BMW-WIP-{date}-{sequence}" /></div>
          <div className="field"><label>Filtro de reportes (JSON)</label><textarea value={rule.report_filter} onChange={(event) => setRule({ ...rule, report_filter: event.target.value })} /></div>
          <div className="field"><label>Mapeo ERP (JSON)</label><textarea value={rule.mapping_config} onChange={(event) => setRule({ ...rule, mapping_config: event.target.value })} /></div>
        </div><div className="editor-actions compact-end">{selectedRule && <button className="ghost" type="button" onClick={() => { setSelectedRule(null); setRule(emptyRule); }}>Cancelar</button>}<button className="primary" disabled={loading || !servers.some((item) => item.is_active)}>{selectedRule ? "Guardar regla de envío" : "Crear regla de envío"}</button></div></form>
        <div className="table-shell"><table className="table"><thead><tr><th>Regla</th><th>Destino</th><th>Lote</th><th>Estado</th><th /></tr></thead><tbody>{rules.map((item) => <tr key={item.id}><td>{item.rule_id}</td><td>{item.server_code}</td><td>{item.lot_mask || "-"}</td><td><span className={`status-chip ${item.is_active ? "ok" : ""}`}>{item.is_active ? "Activa" : "Inactiva"}</span></td><td><div className="table-actions"><button className="ghost compact" type="button" onClick={() => editRule(item)}>Editar</button><button className="secondary compact" type="button" disabled={loading} onClick={() => toggleRuleActive(item)}>{item.is_active ? "Desactivar" : "Activar"}</button><button className="danger compact" type="button" onClick={() => remove(`/integration-delivery-rules/${item.rule_id}`)}>Eliminar</button></div></td></tr>)}{!rules.length && <tr><td colSpan="5"><div className="empty-state table-empty-state">No hay reglas configuradas.</div></td></tr>}</tbody></table></div>
      </section>
    </div>}
    {status ? <div className="notice">{status}</div> : null}
  </Layout>;
}
