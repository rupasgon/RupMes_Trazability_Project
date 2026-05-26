import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyRole = { role_id: "", description_role: "" };

export default function RolesPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [selectedPermissions, setSelectedPermissions] = useState([]);
  const [form, setForm] = useState(emptyRole);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const canWrite = useMemo(() => auth.permissions?.includes("roles.write"), [auth]);

  const loadRoles = async () => {
    const data = await request("/roles", { tenantId });
    setRoles(data);
  };

  const loadPermissions = async () => {
    const data = await request("/permissions", { tenantId });
    setPermissions(data);
  };

  useEffect(() => {
    loadRoles().catch(() => {});
    loadPermissions().catch(() => {});
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/roles", {
        method: "POST",
        data: form,
        tenantId,
        csrfToken,
      });
      setForm(emptyRole);
      setEditorMode("idle");
      await loadRoles();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRole = async (role) => {
    setSelectedRole(role);
    setEditorMode("edit");
    setForm({ role_id: role.role_id, description_role: role.description_role });
    setStatus("");
    try {
      const rolePerms = await request(`/roles/${role.role_id}/permissions`, { tenantId });
      setSelectedPermissions(rolePerms);
    } catch (error) {
      setSelectedPermissions([]);
    }
  };

  const handleSavePermissions = async () => {
    if (!selectedRole) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/roles/${selectedRole.role_id}/permissions`, {
        method: "PUT",
        data: { permission_ids: selectedPermissions },
        tenantId,
        csrfToken,
      });
      setStatus(t("roles.permissionsUpdated"));
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRole = async () => {
    if (!selectedRole) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/roles/${selectedRole.role_id}`, {
        method: "PATCH",
        data: { description_role: form.description_role },
        tenantId,
        csrfToken,
      });
      await loadRoles();
      setStatus(t("roles.roleUpdated"));
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRole = async () => {
    if (!selectedRole) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/roles/${selectedRole.role_id}`, {
        method: "DELETE",
        tenantId,
        csrfToken,
      });
      setSelectedRole(null);
      setSelectedPermissions([]);
      setEditorMode("idle");
      setForm(emptyRole);
      await loadRoles();
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
      active="roles"
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
            <h2>{t("roles.title")}</h2>
            <p>{t("roles.subtitle")}</p>
          </div>
          <div className="page-header-meta">
            <div className="badge">{t("common.tenant")}: {auth.tenant_id}</div>
          </div>
        </div>
      </div>

      <div className="crud-layout">
        <div className="crud-grid">
          <div className="card crud-card crud-list-card">
            <div className="crud-card-header">
              <div>
                <h3>{t("common.list")}</h3>
                <p>{t("roles.subtitle")}</p>
              </div>
              <div className="row-space">
                {canWrite ? (
                  <button
                    className="secondary"
                    type="button"
                    onClick={() => {
                      setSelectedRole(null);
                      setSelectedPermissions([]);
                      setForm(emptyRole);
                      setStatus("");
                      setEditorMode("create");
                    }}
                  >
                    {t("roles.new")}
                  </button>
                ) : null}
                <div className="crud-card-metric">{roles.length}</div>
              </div>
            </div>
            <div className="table-shell">
              <table className="table">
                <thead>
                  <tr>
                    <th>{t("common.role")}</th>
                    <th>{t("common.description")}</th>
                  </tr>
                </thead>
                <tbody>
                  {roles.map((role) => (
                    <tr
                      key={role.role_id}
                      onClick={() => handleSelectRole(role)}
                      className={selectedRole?.role_id === role.role_id ? "active" : ""}
                    >
                      <td>{role.role_id}</td>
                      <td>{role.description_role}</td>
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
                  <h3>{editorMode === "edit" ? t("roles.edit") : t("roles.new")}</h3>
                  <p>{editorMode === "edit" ? t("roles.selectToEdit") : t("roles.new")}</p>
                </div>
              </div>
              {!canWrite && <p className="muted">{t("roles.noWrite")}</p>}
              {editorMode === "idle" ? (
                <div className="empty-state">{t("roles.selectToEdit")}</div>
              ) : (
                <>
              {selectedRole ? <div className="editor-banner">{t("common.role")}: {selectedRole.role_id}</div> : null}
              <form onSubmit={selectedRole ? (event) => { event.preventDefault(); handleUpdateRole(); } : handleCreate} className="form">
                <div className="field">
                  <label>{t("fields.roleId")}</label>
                  <input
                    value={form.role_id}
                    onChange={(event) => setForm({ ...form, role_id: event.target.value })}
                    required
                    disabled={!!selectedRole}
                  />
                </div>
                <div className="field">
                  <label>{t("fields.description")}</label>
                  <input
                    value={form.description_role}
                    onChange={(event) => setForm({ ...form, description_role: event.target.value })}
                    required
                  />
                </div>
                <div className={`editor-actions ${selectedRole ? "" : "compact-end"}`}>
                  {selectedRole ? (
                    <button className="danger" type="button" onClick={handleDeleteRole} disabled={!canWrite || loading}>
                      {t("common.delete")}
                    </button>
                  ) : (
                    <button
                      className="ghost"
                      type="button"
                      onClick={() => {
                        setEditorMode("idle");
                        setForm(emptyRole);
                        setStatus("");
                      }}
                    >
                      {t("common.cancel")}
                    </button>
                  )}
                  <button className={selectedRole ? "secondary" : "primary"} type="submit" disabled={!canWrite || loading}>
                    {selectedRole ? t("common.update") : t("common.create")}
                  </button>
                </div>
              </form>
                </>
              )}
            </div>

            <div className="card crud-card">
              <div className="crud-card-header">
                <div>
                  <h3>{t("roles.permissions")}</h3>
                  <p>{t("roles.selectToPerms")}</p>
                </div>
              </div>
              {!selectedRole ? (
                <div className="empty-state">{t("roles.selectToPerms")}</div>
              ) : (
                <>
                  <div className="editor-banner">{t("common.role")}: {selectedRole.role_id}</div>
                  <div className="checkbox-panel">
                    <div className="checkbox-list">
                      {permissions.map((permission) => (
                        <label key={permission.permission_id} className="checkbox-item">
                          <input
                            type="checkbox"
                            checked={selectedPermissions.includes(permission.permission_id)}
                            onChange={(event) => {
                              if (event.target.checked) {
                                setSelectedPermissions([...selectedPermissions, permission.permission_id]);
                              } else {
                                setSelectedPermissions(
                                  selectedPermissions.filter((p) => p !== permission.permission_id)
                                );
                              }
                            }}
                          />
                          {permission.permission_id}
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="editor-actions compact-end">
                    <button className="secondary" onClick={handleSavePermissions} disabled={!canWrite || loading}>
                      {t("common.update")}
                    </button>
                  </div>
                </>
              )}
              {status ? <div className="notice">{status}</div> : null}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
