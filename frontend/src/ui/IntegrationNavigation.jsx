import { Link } from "react-router-dom";

const sections = [
  {
    id: "clients",
    to: "/integrations",
    eyebrow: "ENTRADA",
    title: "Clientes",
    description: "PLC, SCADA y conectores autorizados",
    icon: "IN",
  },
  {
    id: "servers",
    to: "/integrations/servers",
    eyebrow: "SALIDA",
    title: "Servidores ERP y reglas",
    description: "Destinos, secretos y reglas de envío",
    icon: "OUT",
  },
];

export default function IntegrationNavigation({ active }) {
  return (
    <nav className="integration-navigation" aria-label="Secciones de integraciones">
      <div className="integration-navigation-title">
        <span className="eyebrow">Configuración de integración</span>
        <span>Define el origen y el destino sin acoplar cada conector a una sede.</span>
      </div>
      <div className="integration-navigation-tabs">
        {sections.map((section) => {
          const isActive = active === section.id;
          return (
            <Link
              key={section.id}
              className={`integration-navigation-tab ${isActive ? "active" : ""}`}
              to={section.to}
              aria-current={isActive ? "page" : undefined}
            >
              <span className="integration-navigation-icon">{section.icon}</span>
              <span className="integration-navigation-copy">
                <span className="integration-navigation-eyebrow">{section.eyebrow}</span>
                <strong>{section.title}</strong>
                <small>{section.description}</small>
              </span>
              <span className="integration-navigation-arrow" aria-hidden="true">›</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
