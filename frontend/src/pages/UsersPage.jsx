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

export default function UsersPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedRoles, setSelectedRoles] = useState([]);
  const [form, setForm] = useState(emptyUser);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const isAdmin = useMemo(() => auth.roles?.includes("ADM"), [auth]);
  const canWrite = useMemo(() => auth.permissions?.includes("users.write"), [auth]);

  if (!isAdmin) {
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
        <div className="card">
          <h2>{t("users.title")}</h2>
          <p className="muted">{t("users.adminOnly")}</p>
        </div>
      </Layout>
    );
  }

  const loadUsers = async () => {
    const data = await request("/users", { tenantId });
    setUsers(data);
  };

  const loadRoles = async () => {
    const data = await request("/roles", { tenantId });
    setRoles(data);
  };

  useEffect(() => {
    loadUsers().catch(() => {});
    loadRoles().catch(() => {});
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/users", {
        method: "POST",
        data: form,
        tenantId,
        csrfToken,
      });
      setForm(emptyUser);
      await loadUsers();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectUser = async (user) => {
    setSelectedUser(user);
    setForm({
      ...emptyUser,
      id_user: user.id_user,
      name_user: user.name_user,
      mail_user: user.mail_user,
      id_group: user.id_group,
      status_user: user.status_user,
      password: "",
    });
    setStatus("");
    try {
      const roleIds = await request(`/users/${user.id_user}/roles`, { tenantId });
      setSelectedRoles(roleIds);
    } catch (error) {
      setSelectedRoles([]);
    }
  };

  const handleSaveRoles = async () => {
    if (!selectedUser) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/users/${selectedUser.id_user}/roles`, {
        method: "PUT",
        data: { role_ids: selectedRoles },
        tenantId,
        csrfToken,
      });
      setStatus(t("users.rolesUpdated"));
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;
    setStatus("");
    setLoading(true);
    try {
      const payload = {
        name_user: form.name_user,
        mail_user: form.mail_user,
        id_group: form.id_group,
        status_user: form.status_user,
        password: form.password || undefined,
      };
      await request(`/users/${selectedUser.id_user}`, {
        method: "PATCH",
        data: payload,
        tenantId,
        csrfToken,
      });
      await loadUsers();
      setStatus(t("users.userUpdated"));
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
        tenantId,
        csrfToken,
      });
      setSelectedUser(null);
      setForm(emptyUser);
      await loadUsers();
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
      active="users"
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
          <h2>{t("users.title")}</h2>
          <p className="muted">{t("users.subtitle")}</p>
        </div>
        <div className="badge">{t("common.tenant")}: {auth.tenant_id}</div>
      </div>

      <div className="grid two">
        <div className="card">
          <h3>{t("common.list")}</h3>
          <table className="table">
            <thead>
              <tr>
                <th>{t("common.user")}</th>
                <th>{t("common.name")}</th>
                <th>{t("common.email")}</th>
                <th>{t("common.group")}</th>
                <th>{t("common.status")}</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr
                  key={user.id_user}
                  onClick={() => handleSelectUser(user)}
                  className={selectedUser?.id_user === user.id_user ? "active" : ""}
                >
                  <td>{user.id_user}</td>
                  <td>{user.name_user}</td>
                  <td>{user.mail_user}</td>
                  <td>{user.id_group}</td>
                  <td>{user.status_user}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>{t("users.new")}</h3>
          {!canWrite && <p className="muted">{t("users.noWrite")}</p>}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("login.user")}</label>
              <input
                value={form.id_user}
                onChange={(event) => setForm({ ...form, id_user: event.target.value })}
                required
              />
            </div>
            <div className="field">
              <label>{t("fields.name")}</label>
              <input
                value={form.name_user}
                onChange={(event) => setForm({ ...form, name_user: event.target.value })}
                required
              />
            </div>
            <div className="field">
              <label>{t("fields.email")}</label>
              <input
                type="email"
                value={form.mail_user}
                onChange={(event) => setForm({ ...form, mail_user: event.target.value })}
                required
              />
            </div>
            <div className="field">
              <label>{t("fields.group")}</label>
              <input
                value={form.id_group}
                onChange={(event) => setForm({ ...form, id_group: event.target.value })}
                placeholder="USR"
                required
              />
            </div>
            <div className="field">
              <label>{t("fields.status")}</label>
              <input
                value={form.status_user}
                onChange={(event) => setForm({ ...form, status_user: event.target.value })}
                placeholder="ENB"
                required
              />
            </div>
            <div className="field">
              <label>{t("login.password")}</label>
              <input
                type="password"
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
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
        <h3>{t("users.edit")}</h3>
        {!selectedUser ? (
          <p className="muted">{t("users.selectToEdit")}</p>
        ) : (
          <>
            <p className="muted">{t("common.user")}: {selectedUser.id_user}</p>
            <div className="grid two">
              <div className="field">
                <label>{t("fields.name")}</label>
                <input
                  value={form.name_user}
                  onChange={(event) => setForm({ ...form, name_user: event.target.value })}
                />
              </div>
              <div className="field">
                <label>{t("fields.email")}</label>
                <input
                  type="email"
                  value={form.mail_user}
                  onChange={(event) => setForm({ ...form, mail_user: event.target.value })}
                />
              </div>
              <div className="field">
                <label>{t("fields.group")}</label>
                <input
                  value={form.id_group}
                  onChange={(event) => setForm({ ...form, id_group: event.target.value })}
                />
              </div>
              <div className="field">
                <label>{t("fields.status")}</label>
                <input
                  value={form.status_user}
                  onChange={(event) => setForm({ ...form, status_user: event.target.value })}
                />
              </div>
              <div className="field">
                <label>{t("fields.passwordOptional")}</label>
                <input
                  type="password"
                  value={form.password}
                  onChange={(event) => setForm({ ...form, password: event.target.value })}
                />
              </div>
            </div>
            <div className="row-space" style={{ marginTop: 10 }}>
              <button className="secondary" onClick={handleUpdateUser} disabled={!canWrite || loading}>
                {t("common.update")}
              </button>
              <button
                className="danger"
                onClick={handleDeleteUser}
                disabled={!canWrite || loading || selectedUser.id_user === auth.id_user}
              >
                {t("common.delete")}
              </button>
            </div>
          </>
        )}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>{t("users.assignRoles")}</h3>
        {!selectedUser ? (
          <p className="muted">{t("users.selectToRoles")}</p>
        ) : (
          <>
            <p className="muted">{t("common.user")}: {selectedUser.id_user}</p>
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
                        setSelectedRoles(selectedRoles.filter((r) => r !== role.role_id));
                      }
                    }}
                  />
                  {role.role_id} - {role.description_role}
                </label>
              ))}
            </div>
            <button className="secondary" onClick={handleSaveRoles} disabled={!canWrite || loading}>
              {t("users.saveRoles")}
            </button>
          </>
        )}
        {status ? <div className="notice">{status}</div> : null}
      </div>
    </Layout>
  );
}
