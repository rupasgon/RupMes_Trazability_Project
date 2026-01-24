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
      await loadRoles();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRole = async (role) => {
    setSelectedRole(role);
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
      <div className="section-head">
        <div>
          <h2>{t("roles.title")}</h2>
          <p className="muted">{t("roles.subtitle")}</p>
        </div>
        <div className="badge">{t("common.tenant")}: {auth.tenant_id}</div>
      </div>

      <div className="grid two">
        <div className="card">
          <h3>{t("common.list")}</h3>
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

        <div className="card">
          <h3>{t("roles.new")}</h3>
          {!canWrite && <p className="muted">{t("roles.noWrite")}</p>}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("fields.roleId")}</label>
              <input
                value={form.role_id}
                onChange={(event) => setForm({ ...form, role_id: event.target.value })}
                required
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
            <button className="primary" type="submit" disabled={!canWrite || loading}>
              {t("common.create")}
            </button>
          </form>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("roles.edit")}</h3>
        {!selectedRole ? (
          <p className="muted">{t("roles.selectToEdit")}</p>
        ) : (
          <>
            <p className="muted">{t("common.role")}: {selectedRole.role_id}</p>
            <div className="field">
              <label>{t("fields.description")}</label>
              <input
                value={form.description_role}
                onChange={(event) => setForm({ ...form, description_role: event.target.value })}
              />
            </div>
            <div className="row-space">
              <button className="secondary" onClick={handleUpdateRole} disabled={!canWrite || loading}>
                {t("common.update")}
              </button>
              <button className="danger" onClick={handleDeleteRole} disabled={!canWrite || loading}>
                {t("common.delete")}
              </button>
            </div>
          </>
        )}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("roles.permissions")}</h3>
        {!selectedRole ? (
          <p className="muted">{t("roles.selectToPerms")}</p>
        ) : (
          <>
            <p className="muted">{t("common.role")}: {selectedRole.role_id}</p>
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
            <button className="secondary" onClick={handleSavePermissions} disabled={!canWrite || loading}>
              {t("common.update")}
            </button>
          </>
        )}
        {status ? <div className="notice">{status}</div> : null}
      </div>
    </Layout>
  );
}
