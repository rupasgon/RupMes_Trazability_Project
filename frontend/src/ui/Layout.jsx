import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Layout({ auth, onLogout, active, tenantId, setTenantId, lang, setLang, theme, setTheme, t, children }) {
  const permissions = auth.permissions || [];
  const isAdmin = auth.roles?.includes("ADM");
  const canUsers = permissions.includes("users.read") && isAdmin;
  const canRoles = permissions.includes("roles.read") && isAdmin;
  const canAdmin = canUsers || canRoles;
  const canItems = permissions.includes("items.read");
  const canMasters = permissions.includes("masters.read");
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("rupmes_sidebar") === "collapsed");

  useEffect(() => {
    localStorage.setItem("rupmes_sidebar", collapsed ? "collapsed" : "expanded");
  }, [collapsed]);

  return (
    <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="brand">
          <div className="brand-badge" />
          <h1>RupMes</h1>
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
        <div className="nav">
          <Link className={`nav-link ${active === "dashboard" ? "active" : ""}`} to="/" title={t("nav.dashboard")}>
            <span className="nav-icon">D</span>
            <span className="nav-text">{t("nav.dashboard")}</span>
          </Link>
          {canAdmin ? (
            <Link className={`nav-link ${active === "users" || active === "roles" ? "active" : ""}`} to="/users" title={t("nav.admin")}>
              <span className="nav-icon">A</span>
              <span className="nav-text">{t("nav.admin")}</span>
            </Link>
          ) : null}
          {canItems ? (
            <Link className={`nav-link ${active === "items" ? "active" : ""}`} to="/items" title={t("nav.items")}>
              <span className="nav-icon">P</span>
              <span className="nav-text">{t("nav.items")}</span>
            </Link>
          ) : null}
          {canMasters ? (
            <>
              <div className="nav-label">{t("nav.masters")}</div>
              <Link className={`nav-link ${active === "lines" ? "active" : ""}`} to="/lines" title={t("nav.lines")}>
                <span className="nav-icon">L</span>
                <span className="nav-text">{t("nav.lines")}</span>
              </Link>
              <Link className={`nav-link ${active === "cells" ? "active" : ""}`} to="/cells" title={t("nav.cells")}>
                <span className="nav-icon">C</span>
                <span className="nav-text">{t("nav.cells")}</span>
              </Link>
              <Link className={`nav-link ${active === "models" ? "active" : ""}`} to="/models" title={t("nav.models")}>
                <span className="nav-icon">M</span>
                <span className="nav-text">{t("nav.models")}</span>
              </Link>
              <Link className={`nav-link ${active === "statuses" ? "active" : ""}`} to="/statuses" title={t("nav.statuses")}>
                <span className="nav-icon">S</span>
                <span className="nav-text">{t("nav.statuses")}</span>
              </Link>
            </>
          ) : null}
          <button className="ghost" onClick={onLogout}>
            <span className="nav-icon">X</span>
            <span className="nav-text">{t("nav.logout")}</span>
          </button>
        </div>
        <div className="sidebar-footer">
          <div className="sidebar-footer-content">
            <div className="muted">{t("nav.user")}</div>
            <div>{auth.id_user}</div>
            <div className="muted" style={{ marginTop: 6 }}>{t("dashboard.roles")}</div>
            <div>{auth.roles.join(", ") || t("common.noRoles")}</div>
            <div className="muted" style={{ marginTop: 12 }}>{t("nav.activeTenant")}</div>
            <input
              className="inline-input"
              value={tenantId}
              onChange={(event) => setTenantId(event.target.value)}
              placeholder="DEFAULT"
            />
            <div className="muted" style={{ marginTop: 12 }}>{t("language.label")}</div>
            <select className="inline-input" value={lang} onChange={(event) => setLang(event.target.value)}>
              <option value="es">ES</option>
              <option value="en">EN</option>
              <option value="ca">CA</option>
            </select>
            <div className="muted" style={{ marginTop: 12 }}>{t("theme.label")}</div>
            <select className="inline-input" value={theme} onChange={(event) => setTheme(event.target.value)}>
              <option value="dark">{t("theme.dark")}</option>
              <option value="light">{t("theme.light")}</option>
            </select>
          </div>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
