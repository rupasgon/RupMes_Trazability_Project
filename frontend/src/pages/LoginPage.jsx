import { useEffect, useState } from "react";
import { request } from "../api.js";

export default function LoginPage({ onLogin, tenantId, setTenantId, t, lang, setLang, theme, setTheme }) {
  const [form, setForm] = useState({ id_user: "", password: "" });
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [branding, setBranding] = useState({ portal_title: "RupMes", logo_image: null });
  const [loginContext, setLoginContext] = useState({ multi_tenant_enabled: false, default_tenant_id: "DEFAULT", tenants: [] });

  useEffect(() => {
    const loadLoginContext = async () => {
      try {
        const data = await request("/public/login-context");
        setLoginContext(data);
        if (!tenantId && data.default_tenant_id) {
          setTenantId(data.default_tenant_id);
        }
      } catch {
        setLoginContext({ multi_tenant_enabled: false, default_tenant_id: "DEFAULT", tenants: [] });
        if (!tenantId) {
          setTenantId("DEFAULT");
        }
      }
    };

    loadLoginContext().catch(() => {});
  }, []);

  useEffect(() => {
    const targetTenant = tenantId || loginContext.default_tenant_id || "DEFAULT";
    const loadBranding = async () => {
      try {
        const data = await request("/portal-settings", { tenantId: targetTenant });
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
  }, [tenantId, loginContext.default_tenant_id]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setStatus("");
    try {
      await onLogin(form);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-brand">
          {branding.logo_image ? <img className="login-logo" src={branding.logo_image} alt={branding.portal_title || "RupMes"} /> : <div className="brand-badge" />}
          <div>
            <h2>{branding.portal_title || t("app.title")}</h2>
            <p>{t("login.subtitle")}</p>
          </div>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>{t("login.user")}</label>
            <input
              value={form.id_user}
              onChange={(event) => setForm({ ...form, id_user: event.target.value })}
              placeholder="admin"
              required
            />
          </div>
          <div className="field">
            <label>{t("login.password")}</label>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              placeholder="********"
              required
            />
          </div>
          <div className="field">
            <label>{t("login.tenant")}</label>
            {loginContext.multi_tenant_enabled ? (
              <select value={tenantId || loginContext.default_tenant_id || "DEFAULT"} onChange={(event) => setTenantId(event.target.value)}>
                {loginContext.tenants.map((tenant) => (
                  <option key={tenant.tenant_id} value={tenant.tenant_id}>
                    {tenant.name_tenant} ({tenant.tenant_id}){tenant.is_default ? ` - ${t("tenants.default")}` : ""}
                  </option>
                ))}
              </select>
            ) : (
              <input value={tenantId || loginContext.default_tenant_id || "DEFAULT"} disabled />
            )}
          </div>
          <div className="field">
            <label>{t("language.label")}</label>
            <select value={lang} onChange={(event) => setLang(event.target.value)}>
              <option value="es">ES</option>
              <option value="en">EN</option>
              <option value="ca">CA</option>
            </select>
          </div>
          <div className="field">
            <label>{t("theme.label")}</label>
            <select value={theme} onChange={(event) => setTheme(event.target.value)}>
              <option value="dark">{t("theme.dark")}</option>
              <option value="light">{t("theme.light")}</option>
            </select>
          </div>
          <button className="primary" type="submit" disabled={loading}>
            {loading ? t("login.loading") : t("login.submit")}
          </button>
        </form>
        {status ? <div className="notice">{status}</div> : null}
      </div>
    </div>
  );
}
