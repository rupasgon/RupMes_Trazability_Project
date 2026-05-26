import { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { getCookie, request } from "./api.js";
import { useI18n } from "./i18n.js";
import LoginPage from "./pages/LoginPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import UsersPage from "./pages/UsersPage.jsx";
import RolesPage from "./pages/RolesPage.jsx";
import ItemsPage from "./pages/ItemsPage.jsx";
import LinesPage from "./pages/LinesPage.jsx";
import CellsPage from "./pages/CellsPage.jsx";
import ModelsPage from "./pages/ModelsPage.jsx";
import StatusesPage from "./pages/StatusesPage.jsx";
import ReportsPage from "./pages/ReportsPage.jsx";
import "./styles.css";

const CSRF_COOKIE = import.meta.env.VITE_CSRF_COOKIE_NAME || "rupmes_csrf";

export default function App() {
  const { lang, setLang, t } = useI18n();
  const [auth, setAuth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem("rupmes_theme");
    if (stored === "light" || stored === "dark") {
      return stored;
    }
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  });
  const [tenantId, setTenantId] = useState(
    localStorage.getItem("rupmes_tenant") || import.meta.env.VITE_TENANT_ID || ""
  );

  const csrfToken = useMemo(() => getCookie(CSRF_COOKIE), [auth]);

  const checkSession = async () => {
    try {
      const me = await request("/auth/me", { tenantId });
      setAuth(me);
    } catch (error) {
      setAuth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkSession();
  }, []);

  useEffect(() => {
    localStorage.setItem("rupmes_tenant", tenantId);
  }, [tenantId]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("rupmes_theme", theme);
  }, [theme]);

  const handleLogin = async (payload) => {
    const me = await request("/auth/login", {
      method: "POST",
      data: payload,
      tenantId,
    });
    setAuth(me);
    return me;
  };

  const handleLogout = async () => {
    await request("/auth/logout", {
      method: "POST",
      tenantId,
      csrfToken,
    });
    setAuth(null);
  };

  if (loading) {
    return (
      <div className="login-wrap">
        <div className="login-card">{t("common.loading")}</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            auth ? (
              <Navigate to="/" replace />
            ) : (
              <LoginPage
                onLogin={handleLogin}
                tenantId={tenantId}
                setTenantId={setTenantId}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            )
          }
        />
        <Route
          path="/"
          element={
            auth ? (
              <DashboardPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/users"
          element={
            auth ? (
              <UsersPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/roles"
          element={
            auth ? (
              <RolesPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/items"
          element={
            auth ? (
              <ItemsPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/lines"
          element={
            auth ? (
              <LinesPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/cells"
          element={
            auth ? (
              <CellsPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/models"
          element={
            auth ? (
              <ModelsPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/reports"
          element={
            auth ? (
              <ReportsPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/statuses"
          element={
            auth ? (
              <StatusesPage
                auth={auth}
                onLogout={handleLogout}
                tenantId={tenantId}
                setTenantId={setTenantId}
                csrfToken={csrfToken}
                t={t}
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to={auth ? "/" : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  );
}
