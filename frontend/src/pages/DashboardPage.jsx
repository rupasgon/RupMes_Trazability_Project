import Layout from "../ui/Layout.jsx";

export default function DashboardPage({ auth, onLogout, tenantId, setTenantId, t, lang, setLang, theme, setTheme }) {
  return (
    <Layout
      auth={auth}
      onLogout={onLogout}
      active="dashboard"
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
            <h2>{t("dashboard.title")}, {auth.name_user}</h2>
            <p>{t("dashboard.subtitle")}</p>
          </div>
          <div className="page-header-meta">
            <div className="badge">{t("common.tenant")}: {auth.tenant_id}</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="row-space">
          <div>
            <strong>{t("dashboard.activeUser")}:</strong> {auth.id_user} ({auth.mail_user})
            <div className="muted" style={{ marginTop: 4 }}>
              {t("dashboard.roles")}: {auth.roles.join(", ") || t("common.noRoles")}
            </div>
          </div>
          <button className="secondary" onClick={onLogout}>{t("nav.logout")}</button>
        </div>
      </div>

      <div className="grid">
        <div className="stat">
          <h3>{t("dashboard.items")}</h3>
          <p>—</p>
        </div>
        <div className="stat">
          <h3>{t("dashboard.users")}</h3>
          <p>—</p>
        </div>
        <div className="stat">
          <h3>{t("dashboard.routings")}</h3>
          <p>—</p>
        </div>
        <div className="stat">
          <h3>{t("dashboard.system")}</h3>
          <p>OK</p>
        </div>
      </div>
    </Layout>
  );
}
