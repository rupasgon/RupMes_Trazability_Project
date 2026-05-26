import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyUser = {
  id_user: "",
  name_user: "",
  mail_user: "",
  id_group: "USR",
  status_user: "ENB",
  password: "",
};

const emptyProfile = {
  name_user: "",
  mail_user: "",
  password: "",
};

const emptyGroup = {
  id_group: "",
  name_group: "",
  level_group: 1,
};

const emptyRole = {
  role_id: "",
  description_role: "",
};

const emptyTenant = {
  tenant_id: "",
  name_tenant: "",
  is_active: true,
};

const emptyBranding = {
  portal_title: "RupMes",
  logo_image: null,
};

const toDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Unable to read file"));
    reader.readAsDataURL(file);
  });

export default function UsersPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [groups, setGroups] = useState([]);
  const [userStatuses, setUserStatuses] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [myUser, setMyUser] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedRoles, setSelectedRoles] = useState([]);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [userForm, setUserForm] = useState(emptyUser);
  const [profileForm, setProfileForm] = useState(emptyProfile);
  const [groupForm, setGroupForm] = useState(emptyGroup);
  const [roleForm, setRoleForm] = useState(emptyRole);
  const [tenantForm, setTenantForm] = useState(emptyTenant);
  const [brandingForm, setBrandingForm] = useState(emptyBranding);
  const [view, setView] = useState("home");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const isAdmin = useMemo(() => auth.roles?.includes("ADM"), [auth]);
  const canWrite = useMemo(() => auth.permissions?.includes("users.write"), [auth]);
  const currentTenant = tenantId || auth.tenant_id || "DEFAULT";

  const loadUsers = async () => {
    if (!isAdmin) return;
    const data = await request("/users", { tenantId: currentTenant });
    setUsers(data);
  };

  const loadRoles = async () => {
    if (!isAdmin) return;
    const data = await request("/roles", { tenantId: currentTenant });
    setRoles(data);
  };

  const loadGroups = async () => {
    const data = await request("/groups", { tenantId: currentTenant });
    setGroups(data);
  };

  const loadUserStatuses = async () => {
    const data = await request("/user-statuses", { tenantId: currentTenant });
    setUserStatuses(data);
  };

  const loadMyUser = async () => {
    const data = await request("/users/me", { tenantId: currentTenant });
    setMyUser(data);
    setProfileForm({
      name_user: data.name_user,
      mail_user: data.mail_user,
      password: "",
    });
  };

  const loadTenants = async () => {
    if (!isAdmin) return;
    const data = await request("/tenants", { tenantId: currentTenant });
    setTenants(data);
  };

  const loadBranding = async () => {
    if (!isAdmin) return;
    const data = await request("/portal-settings", { tenantId: currentTenant });
    setBrandingForm({
      portal_title: data.portal_title || "RupMes",
      logo_image: data.logo_image || null,
    });
  };

  useEffect(() => {
    loadMyUser().catch(() => {});
    if (isAdmin) {
      loadGroups().catch(() => {});
      loadUserStatuses().catch(() => {});
      loadUsers().catch(() => {});
      loadRoles().catch(() => {});
      loadTenants().catch(() => {});
      loadBranding().catch(() => {});
    }
  }, [currentTenant, isAdmin]);

  const resetToHome = () => {
    setView("home");
    setSelectedUser(null);
    setSelectedTenant(null);
    setSelectedRoles([]);
    setUserForm(emptyUser);
    setGroupForm(emptyGroup);
    setRoleForm(emptyRole);
    setTenantForm(emptyTenant);
    setStatus("");
    if (myUser) {
      setProfileForm({
        name_user: myUser.name_user,
        mail_user: myUser.mail_user,
        password: "",
      });
    }
  };

  const openCreateUser = () => {
    setUserForm(emptyUser);
    setSelectedRoles(["USR"]);
    setStatus("");
    setView("create-user");
  };

  const openCreateGroup = () => {
    setGroupForm(emptyGroup);
    setStatus("");
    setView("create-group");
  };

  const openCreateRole = () => {
    setRoleForm(emptyRole);
    setStatus("");
    setView("create-role");
  };

  const openEditUser = async (user) => {
    setSelectedUser(user);
    setUserForm({
      ...emptyUser,
      id_user: user.id_user,
      name_user: user.name_user,
      mail_user: user.mail_user,
      id_group: user.id_group,
      status_user: user.status_user,
      password: "",
    });
    setStatus("");
    setView("edit-user");
    try {
      const roleIds = await request(`/users/${user.id_user}/roles`, { tenantId: currentTenant });
      setSelectedRoles(roleIds);
    } catch {
      setSelectedRoles([]);
    }
  };

  const openEditProfile = () => {
    if (!myUser) return;
    setProfileForm({
      name_user: myUser.name_user,
      mail_user: myUser.mail_user,
      password: "",
    });
    setStatus("");
    setView("edit-profile");
  };

  const openPortalSettings = async () => {
    setStatus("");
    await loadBranding().catch(() => {});
    setView("portal-settings");
  };

  const openTenantsHome = async () => {
    setStatus("");
    await loadTenants().catch(() => {});
    setView("tenants-home");
  };

  const openCreateTenant = () => {
    setTenantForm(emptyTenant);
    setSelectedTenant(null);
    setStatus("");
    setView("create-tenant");
  };

  const openEditTenant = (tenant) => {
    setSelectedTenant(tenant);
    setTenantForm({
      tenant_id: tenant.tenant_id,
      name_tenant: tenant.name_tenant,
      is_active: tenant.is_active,
    });
    setStatus("");
    setView("edit-tenant");
  };

  const handleCreateUser = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/users", {
        method: "POST",
        data: userForm,
        tenantId: currentTenant,
        csrfToken,
      });
      await loadUsers();
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (event) => {
    event.preventDefault();
    if (!selectedUser) return;
    setStatus("");
    setLoading(true);
    try {
      const payload = {
        name_user: userForm.name_user,
        mail_user: userForm.mail_user,
        id_group: userForm.id_group,
        status_user: userForm.status_user,
        password: userForm.password || undefined,
      };
      await request(`/users/${selectedUser.id_user}`, {
        method: "PATCH",
        data: payload,
        tenantId: currentTenant,
        csrfToken,
      });
      await request(`/users/${selectedUser.id_user}/roles`, {
        method: "PUT",
        data: { role_ids: selectedRoles },
        tenantId: currentTenant,
        csrfToken,
      });
      await loadUsers();
      if (selectedUser.id_user === auth.id_user) {
        await loadMyUser();
      }
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!selectedUser) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/users/${selectedUser.id_user}`, {
        method: "DELETE",
        tenantId: currentTenant,
        csrfToken,
      });
      await loadUsers();
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      const data = await request("/users/me", {
        method: "PATCH",
        data: {
          name_user: profileForm.name_user,
          mail_user: profileForm.mail_user,
          password: profileForm.password || undefined,
        },
        tenantId: currentTenant,
        csrfToken,
      });
      setMyUser(data);
      setProfileForm({
        name_user: data.name_user,
        mail_user: data.mail_user,
        password: "",
      });
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/groups", {
        method: "POST",
        data: { ...groupForm, level_group: Number(groupForm.level_group) },
        tenantId: currentTenant,
        csrfToken,
      });
      await loadGroups();
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRole = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/roles", {
        method: "POST",
        data: roleForm,
        tenantId: currentTenant,
        csrfToken,
      });
      await loadRoles();
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTenant = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/tenants", {
        method: "POST",
        data: tenantForm,
        tenantId: currentTenant,
        csrfToken,
      });
      await loadTenants();
      setView("tenants-home");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTenant = async (event) => {
    event.preventDefault();
    if (!selectedTenant) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/tenants/${selectedTenant.tenant_id}`, {
        method: "PATCH",
        data: {
          name_tenant: tenantForm.name_tenant,
          is_active: tenantForm.is_active,
        },
        tenantId: currentTenant,
        csrfToken,
      });
      await loadTenants();
      setView("tenants-home");
      setSelectedTenant(null);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBrandingSubmit = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/portal-settings", {
        method: "PUT",
        data: brandingForm,
        tenantId: currentTenant,
        csrfToken,
      });
      window.dispatchEvent(new Event("rupmes-branding-changed"));
      resetToHome();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogoChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const encoded = await toDataUrl(file);
      setBrandingForm((current) => ({ ...current, logo_image: encoded }));
    } catch (error) {
      setStatus(error.message);
    }
  };

  const renderShell = (title, subtitle, formContent, extraAction = null) => (
    <div className="crud-layout">
      <div className="card crud-card crud-editor-card" style={{ maxWidth: 920 }}>
        <div className="crud-card-header">
          <div>
            <h3>{title}</h3>
            <p>{subtitle}</p>
          </div>
        </div>
        <div className="editor-actions" style={{ marginTop: 0, marginBottom: 14 }}>
          <button className="ghost" type="button" onClick={resetToHome}>{t("common.cancel")}</button>
          {extraAction}
        </div>
        {formContent}
        {status ? <div className="notice">{status}</div> : null}
      </div>
    </div>
  );

  const renderAdminHome = () => (
    <div className="crud-layout">
      <div className="card crud-card crud-list-card">
        <div className="crud-card-header">
          <div>
            <h3>{t("common.list")}</h3>
            <p>{t("users.subtitle")}</p>
          </div>
          <div className="crud-card-metric">{users.length}</div>
        </div>
        <div className="row-space admin-action-bar" style={{ marginBottom: 14 }}>
          <div className="muted">{t("dashboard.roles")}: {roles.length} | {t("common.group")}: {groups.length} | {t("common.tenant")}: {tenants.length}</div>
          <div className="stack-actions">
            <button className="secondary" type="button" onClick={openCreateUser}>{t("users.new")}</button>
            <button className="secondary" type="button" onClick={openCreateGroup}>{t("admin.newGroup")}</button>
            <button className="secondary" type="button" onClick={openCreateRole}>{t("roles.new")}</button>
            <button className="secondary" type="button" onClick={openTenantsHome}>{t("admin.tenants")}</button>
            <button className="secondary" type="button" onClick={openPortalSettings}>{t("admin.branding")}</button>
          </div>
        </div>
        <div className="table-shell">
          <table className="table">
            <thead>
              <tr>
                <th>{t("common.user")}</th>
                <th>{t("common.name")}</th>
                <th>{t("common.email")}</th>
                <th>{t("common.role")}</th>
                <th>{t("common.group")}</th>
                <th>{t("common.status")}</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id_user} onClick={() => openEditUser(user)}>
                  <td>{user.id_user}</td>
                  <td>{user.name_user}</td>
                  <td>{user.mail_user}</td>
                  <td>{user.role_ids?.join(", ") || "-"}</td>
                  <td>{user.id_group}</td>
                  <td>
                    <span className={`status-chip ${user.status_user === "ENB" ? "ok" : "warn"}`}>
                      {user.status_user}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderProfileHome = () => (
    <div className="crud-layout">
      <div className="card crud-card crud-editor-card" style={{ maxWidth: 720 }}>
        <div className="crud-card-header">
          <div>
            <h3>{t("users.profileTitle")}</h3>
            <p>{t("users.profileSubtitle")}</p>
          </div>
        </div>
        {myUser ? (
          <div className="profile-summary">
            <div className="profile-grid">
              <div>
                <span className="muted">{t("common.user")}</span>
                <strong>{myUser.id_user}</strong>
              </div>
              <div>
                <span className="muted">{t("common.name")}</span>
                <strong>{myUser.name_user}</strong>
              </div>
              <div>
                <span className="muted">{t("common.email")}</span>
                <strong>{myUser.mail_user}</strong>
              </div>
              <div>
                <span className="muted">{t("common.group")}</span>
                <strong>{myUser.id_group}</strong>
              </div>
              <div>
                <span className="muted">{t("common.role")}</span>
                <strong>{myUser.role_ids?.join(", ") || "-"}</strong>
              </div>
              <div>
                <span className="muted">{t("common.status")}</span>
                <strong>{myUser.status_user}</strong>
              </div>
            </div>
            <div className="editor-actions compact-end">
              <button className="primary" type="button" onClick={openEditProfile}>{t("users.editProfile")}</button>
            </div>
          </div>
        ) : (
          <div className="muted">{t("common.loading")}</div>
        )}
      </div>
    </div>
  );

  const renderTenantsHome = () => (
    <div className="crud-layout">
      <div className="card crud-card crud-list-card">
        <div className="crud-card-header">
          <div>
            <h3>{t("tenants.title")}</h3>
            <p>{t("tenants.subtitle")}</p>
          </div>
          <div className="crud-card-metric">{tenants.length}</div>
        </div>
        <div className="editor-actions" style={{ marginTop: 0, marginBottom: 14 }}>
          <button className="ghost" type="button" onClick={resetToHome}>{t("common.cancel")}</button>
          <button className="secondary" type="button" onClick={openCreateTenant}>{t("tenants.new")}</button>
        </div>
        <div className="table-shell">
          <table className="table">
            <thead>
              <tr>
                <th>{t("common.id")}</th>
                <th>{t("common.name")}</th>
                <th>{t("common.status")}</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant) => (
                <tr key={tenant.tenant_id} onClick={() => openEditTenant(tenant)}>
                  <td>{tenant.tenant_id}</td>
                  <td>{tenant.name_tenant}</td>
                  <td>
                    <span className={`status-chip ${tenant.is_active ? "ok" : "warn"}`}>
                      {tenant.is_active ? "ACTIVE" : "INACTIVE"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {status ? <div className="notice">{status}</div> : null}
      </div>
    </div>
  );

  return (
    <Layout
      auth={auth}
      onLogout={onLogout}
      active="users"
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
            <h2>{t("users.title")}</h2>
            <p>{isAdmin ? t("users.subtitle") : t("users.profileSubtitle")}</p>
          </div>
          <div className="page-header-meta">
            <div className="badge">{t("common.tenant")}: {auth.tenant_id}</div>
          </div>
        </div>
      </div>

      {view === "home" ? (isAdmin ? renderAdminHome() : renderProfileHome()) : null}

      {view === "edit-profile"
        ? renderShell(
            t("users.editProfile"),
            myUser ? `${t("common.user")}: ${myUser.id_user}` : t("users.editProfile"),
            <form onSubmit={handleUpdateProfile} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("fields.name")}</label>
                  <input value={profileForm.name_user} onChange={(event) => setProfileForm({ ...profileForm, name_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.email")}</label>
                  <input type="email" value={profileForm.mail_user} onChange={(event) => setProfileForm({ ...profileForm, mail_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.passwordOptional")}</label>
                  <input type="password" value={profileForm.password} onChange={(event) => setProfileForm({ ...profileForm, password: event.target.value })} />
                </div>
              </div>
              <div className="editor-actions compact-end">
                <button className="primary" type="submit" disabled={loading}>{t("common.update")}</button>
              </div>
            </form>,
          )
        : null}

      {view === "create-user"
        ? renderShell(
            t("users.new"),
            t("users.new"),
            <form onSubmit={handleCreateUser} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("login.user")}</label>
                  <input value={userForm.id_user} onChange={(event) => setUserForm({ ...userForm, id_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.name")}</label>
                  <input value={userForm.name_user} onChange={(event) => setUserForm({ ...userForm, name_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.email")}</label>
                  <input type="email" value={userForm.mail_user} onChange={(event) => setUserForm({ ...userForm, mail_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.group")}</label>
                  <select className="inline-input" value={userForm.id_group} onChange={(event) => setUserForm({ ...userForm, id_group: event.target.value })} required>
                    <option value="">{t("common.select")}</option>
                    {groups.map((group) => (
                      <option key={group.id_group} value={group.id_group}>{group.id_group} - {group.name_group}</option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>{t("fields.status")}</label>
                  <select className="inline-input" value={userForm.status_user} onChange={(event) => setUserForm({ ...userForm, status_user: event.target.value })} required>
                    <option value="">{t("common.select")}</option>
                    {userStatuses.map((row) => (
                      <option key={row.status_user} value={row.status_user}>{row.status_user} - {row.description_status}</option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>{t("login.password")}</label>
                  <input type="password" value={userForm.password} onChange={(event) => setUserForm({ ...userForm, password: event.target.value })} required />
                </div>
              </div>
              <div className="editor-actions compact-end">
                <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
              </div>
            </form>,
          )
        : null}

      {view === "edit-user"
        ? renderShell(
            t("users.edit"),
            selectedUser ? `${t("common.user")}: ${selectedUser.id_user}` : t("users.edit"),
            <form onSubmit={handleUpdateUser} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("login.user")}</label>
                  <input value={userForm.id_user} disabled />
                </div>
                <div className="field">
                  <label>{t("fields.name")}</label>
                  <input value={userForm.name_user} onChange={(event) => setUserForm({ ...userForm, name_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.email")}</label>
                  <input type="email" value={userForm.mail_user} onChange={(event) => setUserForm({ ...userForm, mail_user: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.group")}</label>
                  <select className="inline-input" value={userForm.id_group} onChange={(event) => setUserForm({ ...userForm, id_group: event.target.value })} required>
                    <option value="">{t("common.select")}</option>
                    {groups.map((group) => (
                      <option key={group.id_group} value={group.id_group}>{group.id_group} - {group.name_group}</option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>{t("fields.status")}</label>
                  <select className="inline-input" value={userForm.status_user} onChange={(event) => setUserForm({ ...userForm, status_user: event.target.value })} required>
                    <option value="">{t("common.select")}</option>
                    {userStatuses.map((row) => (
                      <option key={row.status_user} value={row.status_user}>{row.status_user} - {row.description_status}</option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>{t("fields.passwordOptional")}</label>
                  <input type="password" value={userForm.password} onChange={(event) => setUserForm({ ...userForm, password: event.target.value })} />
                </div>
              </div>
              <div className="checkbox-panel">
                <div className="muted">{t("users.assignRoles")}</div>
                <div className="checkbox-list">
                  {roles.map((role) => (
                    <label key={role.role_id} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={selectedRoles.includes(role.role_id)}
                        onChange={(event) => {
                          if (event.target.checked) {
                            setSelectedRoles([...selectedRoles, role.role_id]);
                          } else {
                            setSelectedRoles(selectedRoles.filter((entry) => entry !== role.role_id));
                          }
                        }}
                      />
                      {role.role_id} - {role.description_role}
                    </label>
                  ))}
                </div>
              </div>
              <div className="editor-actions">
                <button className="danger" type="button" onClick={handleDeleteUser} disabled={!canWrite || loading || selectedUser?.id_user === auth.id_user}>
                  {t("common.delete")}
                </button>
                <button className="secondary" type="submit" disabled={!canWrite || loading}>
                  {t("common.update")}
                </button>
              </div>
            </form>,
          )
        : null}

      {view === "create-group"
        ? renderShell(
            t("admin.newGroup"),
            t("common.create"),
            <form onSubmit={handleCreateGroup} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("common.id")}</label>
                  <input value={groupForm.id_group} onChange={(event) => setGroupForm({ ...groupForm, id_group: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.name")}</label>
                  <input value={groupForm.name_group} onChange={(event) => setGroupForm({ ...groupForm, name_group: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("common.level")}</label>
                  <input type="number" value={groupForm.level_group} onChange={(event) => setGroupForm({ ...groupForm, level_group: event.target.value })} required />
                </div>
              </div>
              <div className="editor-actions compact-end">
                <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
              </div>
            </form>,
          )
        : null}

      {view === "create-role"
        ? renderShell(
            t("roles.new"),
            t("common.create"),
            <form onSubmit={handleCreateRole} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("fields.roleId")}</label>
                  <input value={roleForm.role_id} onChange={(event) => setRoleForm({ ...roleForm, role_id: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("fields.description")}</label>
                  <input value={roleForm.description_role} onChange={(event) => setRoleForm({ ...roleForm, description_role: event.target.value })} required />
                </div>
              </div>
              <div className="editor-actions compact-end">
                <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
              </div>
            </form>,
          )
        : null}

      {view === "portal-settings"
        ? renderShell(
            t("branding.title"),
            `${t("common.tenant")}: ${currentTenant}`,
            <form onSubmit={handleBrandingSubmit} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("branding.portalTitle")}</label>
                  <input value={brandingForm.portal_title} onChange={(event) => setBrandingForm({ ...brandingForm, portal_title: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("branding.logo")}</label>
                  <input type="file" accept="image/*" onChange={handleLogoChange} />
                </div>
              </div>
              <div className="image-upload-panel">
                <p className="muted">{t("branding.logoHint")}</p>
                {brandingForm.logo_image ? <img className="logo-preview" src={brandingForm.logo_image} alt={brandingForm.portal_title} /> : <div className="logo-empty">{t("branding.noLogo")}</div>}
                <div className="editor-actions compact-end">
                  <button className="ghost" type="button" onClick={() => setBrandingForm((current) => ({ ...current, logo_image: null }))}>{t("branding.removeLogo")}</button>
                  <button className="primary" type="submit" disabled={loading}>{t("common.update")}</button>
                </div>
              </div>
            </form>,
          )
        : null}

      {view === "tenants-home" ? renderTenantsHome() : null}

      {view === "create-tenant"
        ? renderShell(
            t("tenants.new"),
            t("tenants.subtitle"),
            <form onSubmit={handleCreateTenant} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("common.id")}</label>
                  <input value={tenantForm.tenant_id} onChange={(event) => setTenantForm({ ...tenantForm, tenant_id: event.target.value })} required />
                </div>
                <div className="field">
                  <label>{t("common.name")}</label>
                  <input value={tenantForm.name_tenant} onChange={(event) => setTenantForm({ ...tenantForm, name_tenant: event.target.value })} required />
                </div>
                <label className="checkbox-item inline-check">
                  <input type="checkbox" checked={tenantForm.is_active} onChange={(event) => setTenantForm({ ...tenantForm, is_active: event.target.checked })} />
                  {t("tenants.active")}
                </label>
              </div>
              <div className="editor-actions compact-end">
                <button className="primary" type="submit" disabled={loading}>{t("common.create")}</button>
              </div>
            </form>,
          )
        : null}

      {view === "edit-tenant"
        ? renderShell(
            t("tenants.edit"),
            selectedTenant ? `${t("common.id")}: ${selectedTenant.tenant_id}` : t("tenants.edit"),
            <form onSubmit={handleUpdateTenant} className="form">
              <div className="grid two">
                <div className="field">
                  <label>{t("common.id")}</label>
                  <input value={tenantForm.tenant_id} disabled />
                </div>
                <div className="field">
                  <label>{t("common.name")}</label>
                  <input value={tenantForm.name_tenant} onChange={(event) => setTenantForm({ ...tenantForm, name_tenant: event.target.value })} required />
                </div>
                <label className="checkbox-item inline-check">
                  <input type="checkbox" checked={tenantForm.is_active} onChange={(event) => setTenantForm({ ...tenantForm, is_active: event.target.checked })} />
                  {t("tenants.active")}
                </label>
              </div>
              <div className="editor-actions compact-end">
                <button className="primary" type="submit" disabled={loading}>{t("common.update")}</button>
              </div>
            </form>,
          )
        : null}
    </Layout>
  );
}
