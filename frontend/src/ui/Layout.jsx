import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { request } from "../api.js";

const MASTER_ROUTES = ["lines", "cells", "models", "statuses"];
const ADMIN_ROUTES = ["users", "roles"];

function NavGroup({ collapsed, label, isOpen, onToggle, children }) {
  if (collapsed) {
    return <div className="nav-group-panel open">{children}</div>;
  }

  return (
    <>
      <button className={`nav-group-toggle ${isOpen ? "open" : ""}`} type="button" onClick={onToggle} aria-expanded={isOpen}>
        <span className="nav-group-label">{label}</span>
        <span className="nav-group-caret">{isOpen ? "-" : "+"}</span>
      </button>
      <div className={`nav-group-panel ${isOpen ? "open" : ""}`}>{children}</div>
    </>
  );
}

export default function Layout({ auth, onLogout, active, tenantId, setTenantId, lang, setLang, theme, setTheme, t, children }) {
  const permissions = auth.permissions || [];
  const isAdmin = auth.roles?.includes("ADM");
  const canAdmin = permissions.includes("users.read");
  const canItems = permissions.includes("items.read");
  const canReports = permissions.includes("production.read");
  const canMasters = permissions.includes("masters.read");
  const currentTenant = tenantId || auth.tenant_id || "DEFAULT";
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("rupmes_sidebar") === "collapsed");
  const [branding, setBranding] = useState({ portal_title: "RupMes", logo_image: null });
  const [tenants, setTenants] = useState([]);
  const [openGroups, setOpenGroups] = useState({
    masters: MASTER_ROUTES.includes(active),
    admin: ADMIN_ROUTES.includes(active),
  });

  useEffect(() => {
    localStorage.setItem("rupmes_sidebar", collapsed ? "collapsed" : "expanded");
  }, [collapsed]);

  useEffect(() => {
    if (MASTER_ROUTES.includes(active)) {
      setOpenGroups((current) => ({ ...current, masters: true }));
    }
    if (ADMIN_ROUTES.includes(active)) {
      setOpenGroups((current) => ({ ...current, admin: true }));
    }
  }, [active]);

  useEffect(() => {
    const loadBranding = async () => {
      try {
        const data = await request("/portal-settings", { tenantId: currentTenant });
        setBranding(data);
      } catch {
        setBranding({ portal_title: "RupMes", logo_image: null });
      }
    };

    loadBranding();

    const handleBrandingChanged = () => {
      loadBranding().catch(() => {});
    };

    window.addEventListener("rupmes-branding-changed", handleBrandingChanged);
    return () => window.removeEventListener("rupmes-branding-changed", handleBrandingChanged);
  }, [currentTenant, auth.tenant_id]);

  useEffect(() => {
    if (!isAdmin) {
      setTenants([]);
      return;
    }

    const loadTenants = async () => {
      try {
        const data = await request("/tenants", { tenantId: currentTenant });
        setTenants(Array.isArray(data) ? data : []);
      } catch {
        setTenants([]);
      }
    };

    loadTenants().catch(() => {});
  }, [isAdmin, currentTenant]);

  return (
    <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="brand">
          {branding.logo_image ? (
            <img className="brand-logo" src={branding.logo_image} alt={branding.portal_title || "RupMes"} />
          ) : (
            <div className="brand-badge" />
          )}
          <div className="brand-copy">
            <h1>{branding.portal_title || "RupMes"}</h1>
          </div>
          <button
            className="collapse-toggle"
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? t("sidebar.expand") : t("sidebar.collapse")}
            title={collapsed ? t("sidebar.expand") : t("sidebar.collapse")}
          >
            {collapsed ? ">" : "<"}
          </button>
        </div>

        <nav className="nav">
          <div className="nav-section">
            <Link className={`nav-link ${active === "dashboard" ? "active" : ""}`} to="/" title={t("nav.dashboard")}>
              <span className="nav-icon">DB</span>
              <span className="nav-text">{t("nav.dashboard")}</span>
            </Link>
          </div>

          {canReports ? (
            <div className="nav-section">
              <Link className={`nav-link ${active === "reports" ? "active" : ""}`} to="/reports" title={t("nav.reports")}>
                <span className="nav-icon">RP</span>
                <span className="nav-text">{t("nav.reports")}</span>
              </Link>
            </div>
          ) : null}

          {canItems ? (
            <div className="nav-section">
              <Link className={`nav-link ${active === "items" ? "active" : ""}`} to="/items" title={t("nav.items")}>
                <span className="nav-icon">PR</span>
                <span className="nav-text">{t("nav.items")}</span>
              </Link>
            </div>
          ) : null}

          {canMasters ? (
            <div className="nav-section">
              <NavGroup
                collapsed={collapsed}
                label={t("nav.masters")}
                isOpen={openGroups.masters}
                onToggle={() => setOpenGroups((current) => ({ ...current, masters: !current.masters }))}
              >
                <Link className={`nav-link sub-link ${active === "lines" ? "active" : ""}`} to="/lines" title={t("nav.lines")}>
                  <span className="nav-icon">LN</span>
                  <span className="nav-text">{t("nav.lines")}</span>
                </Link>
                <Link className={`nav-link sub-link ${active === "cells" ? "active" : ""}`} to="/cells" title={t("nav.cells")}>
                  <span className="nav-icon">CL</span>
                  <span className="nav-text">{t("nav.cells")}</span>
                </Link>
                <Link className={`nav-link sub-link ${active === "models" ? "active" : ""}`} to="/models" title={t("nav.models")}>
                  <span className="nav-icon">MD</span>
                  <span className="nav-text">{t("nav.models")}</span>
                </Link>
                <Link className={`nav-link sub-link ${active === "statuses" ? "active" : ""}`} to="/statuses" title={t("nav.statuses")}>
                  <span className="nav-icon">ST</span>
                  <span className="nav-text">{t("nav.statuses")}</span>
                </Link>
              </NavGroup>
            </div>
          ) : null}

          {canAdmin ? (
            <div className="nav-section">
              <NavGroup
                collapsed={collapsed}
                label={t("nav.admin")}
                isOpen={openGroups.admin}
                onToggle={() => setOpenGroups((current) => ({ ...current, admin: !current.admin }))}
              >
                <Link className={`nav-link sub-link ${active === "users" ? "active" : ""}`} to="/users" title={t("users.title")}>
                  <span className="nav-icon">US</span>
                  <span className="nav-text">{t("users.title")}</span>
                </Link>
                <Link className={`nav-link sub-link ${active === "roles" ? "active" : ""}`} to="/roles" title={t("roles.title")}>
                  <span className="nav-icon">RL</span>
                  <span className="nav-text">{t("roles.title")}</span>
                </Link>
              </NavGroup>
            </div>
          ) : null}

          <div className="nav-section nav-footer-section">
            <button className="nav-link logout-btn" onClick={onLogout} title={t("nav.logout")}>
              <span className="nav-icon">EX</span>
              <span className="nav-text">{t("nav.logout")}</span>
            </button>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-footer-content">
            <div className="sidebar-meta-card">
              <div className="sidebar-meta-head sidebar-meta-head-compact">
                <div className="sidebar-meta-identity">
                  <div className="sidebar-meta-subtitle">{t("nav.user")}</div>
                  <strong className="sidebar-meta-value">{auth.id_user}</strong>
                </div>
                <div className="sidebar-meta-role">
                  <div className="sidebar-meta-subtitle">{t("dashboard.roles")}</div>
                  <strong className="sidebar-meta-value sidebar-meta-role-badge">{auth.roles.join(", ") || t("common.noRoles")}</strong>
                </div>
              </div>
              <div className="sidebar-meta-grid">
                {isAdmin ? (
                  <div className="sidebar-meta-item">
                    <span className="muted">{t("nav.activeTenant")}</span>
                    <select
                      className="inline-input"
                      value={currentTenant}
                      onChange={(event) => setTenantId(event.target.value)}
                    >
                      {!tenants.some((tenant) => tenant.tenant_id === currentTenant) ? (
                        <option value={currentTenant}>{currentTenant}</option>
                      ) : null}
                      {tenants.filter((tenant) => tenant.is_active).map((tenant) => (
                        <option key={tenant.tenant_id} value={tenant.tenant_id}>
                          {tenant.tenant_id}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : null}
                <div className="sidebar-meta-item">
                  <span className="muted">{t("language.label")}</span>
                  <select className="inline-input" value={lang} onChange={(event) => setLang(event.target.value)}>
                    <option value="es">ES</option>
                    <option value="en">EN</option>
                    <option value="ca">CA</option>
                  </select>
                </div>
                <div className="sidebar-meta-item">
                  <span className="muted">{t("theme.label")}</span>
                  <select className="inline-input" value={theme} onChange={(event) => setTheme(event.target.value)}>
                    <option value="dark">{t("theme.dark")}</option>
                    <option value="light">{t("theme.light")}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
      <main className="content">
        <div className="content-scroll">{children}</div>
      </main>
    </div>
  );
}
