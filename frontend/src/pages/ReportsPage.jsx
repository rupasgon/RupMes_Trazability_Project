import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyFilters = {
  date_from: "",
  date_to: "",
  plant_code: "",
  line_code: "",
  trace_serial: "",
};

const buildAnalyticsFilters = (filters) => ({
  date_from: filters.date_from,
  date_to: filters.date_to,
  plant_code: filters.plant_code,
  line_code: filters.line_code,
});

const toQuery = (filters, extra = {}) => {
  const params = new URLSearchParams();
  Object.entries({ ...filters, ...extra }).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, String(value));
    }
  });
  return params.toString();
};

const formatPercent = (value) => `${Number(value || 0).toFixed(2)}%`;
const formatNumber = (value, digits = 0) => Number(value || 0).toFixed(digits);

export default function ReportsPage({
  auth,
  onLogout,
  tenantId,
  setTenantId,
  t,
  lang,
  setLang,
  theme,
  setTheme,
}) {
  const [filters, setFilters] = useState(() => {
    const today = new Date().toISOString().slice(0, 10);
    return { ...emptyFilters, date_from: today, date_to: today };
  });
  const [dailyTotal, setDailyTotal] = useState([]);
  const [byLine, setByLine] = useState([]);
  const [okNokByShift, setOkNokByShift] = useState([]);
  const [ftqFpy, setFtqFpy] = useState([]);
  const [topDefects, setTopDefects] = useState([]);
  const [cycleTimeByLine, setCycleTimeByLine] = useState([]);
  const [traceability, setTraceability] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const canReports = useMemo(() => auth.permissions?.includes("production.read"), [auth]);

  const summary = useMemo(() => {
    const totalProduction = dailyTotal.reduce((acc, row) => acc + Number(row.total_production || 0), 0);
    const totalOk = okNokByShift.reduce((acc, row) => acc + Number(row.ok_count || 0), 0);
    const totalNok = okNokByShift.reduce((acc, row) => acc + Number(row.nok_count || 0), 0);
    const totalScrap = okNokByShift.reduce((acc, row) => acc + Number(row.scrap_count || 0), 0);
    const weightedFtq = ftqFpy.reduce(
      (acc, row) => {
        acc.ok += Number(row.first_pass_ok || 0);
        acc.total += Number(row.first_pass_total || 0);
        return acc;
      },
      { ok: 0, total: 0 }
    );
    const weightedFpy = ftqFpy.reduce(
      (acc, row) => {
        acc.ok += Number(row.serial_ok || 0);
        acc.total += Number(row.serial_total || 0);
        return acc;
      },
      { ok: 0, total: 0 }
    );

    return {
      totalProduction,
      totalOk,
      totalNok,
      totalScrap,
      globalFtq: weightedFtq.total ? (weightedFtq.ok / weightedFtq.total) * 100 : 0,
      globalFpy: weightedFpy.total ? (weightedFpy.ok / weightedFpy.total) * 100 : 0,
    };
  }, [dailyTotal, okNokByShift, ftqFpy]);

  const loadAnalytics = async () => {
    if (!canReports) return;
    setLoading(true);
    setStatus("");
    try {
      const analyticsFilters = buildAnalyticsFilters(filters);
      const query = toQuery(analyticsFilters);
      const [daily, lines, shifts, quality, defects, cycle] = await Promise.all([
        request(`/production-reports/analytics/daily-total?${query}`, { tenantId }),
        request(`/production-reports/analytics/by-line?${query}`, { tenantId }),
        request(`/production-reports/analytics/ok-nok-by-shift?${query}`, { tenantId }),
        request(`/production-reports/analytics/ftq-fpy?${query}`, { tenantId }),
        request(`/production-reports/analytics/top-defects?${toQuery(analyticsFilters, { limit: 8 })}`, { tenantId }),
        request(`/production-reports/analytics/average-cycle-time?${query}`, { tenantId }),
      ]);
      setDailyTotal(daily);
      setByLine(lines);
      setOkNokByShift(shifts);
      setFtqFpy(quality);
      setTopDefects(defects);
      setCycleTimeByLine(cycle);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics().catch(() => {});
  }, [canReports]);

  const handleTraceabilitySearch = async () => {
    if (!filters.trace_serial) {
      setTraceability([]);
      return;
    }
    setStatus("");
    try {
      const rows = await request(`/production-reports/traceability/${encodeURIComponent(filters.trace_serial)}`, { tenantId });
      setTraceability(rows);
    } catch (error) {
      setStatus(error.message);
    }
  };

  const exportExcel = async () => {
    const XLSX = await import("xlsx");
    const workbook = XLSX.utils.book_new();
    const sheets = [
      ["Summary", [
        { metric: "Total Production", value: summary.totalProduction },
        { metric: "OK", value: summary.totalOk },
        { metric: "NOK", value: summary.totalNok },
        { metric: "SCRAP", value: summary.totalScrap },
        { metric: "FTQ %", value: formatPercent(summary.globalFtq) },
        { metric: "FPY %", value: formatPercent(summary.globalFpy) },
      ]],
      ["Daily Total", dailyTotal],
      ["By Line", byLine],
      ["OK-NOK Shift", okNokByShift],
      ["FTQ-FPY", ftqFpy],
      ["Top Defects", topDefects],
      ["Cycle Time", cycleTimeByLine],
      ["Traceability", traceability],
    ];
    sheets.forEach(([name, data]) => {
      const worksheet = XLSX.utils.json_to_sheet(data);
      XLSX.utils.book_append_sheet(workbook, worksheet, name);
    });
    XLSX.writeFile(workbook, "production_reports.xlsx");
  };

  const exportCsv = () => {
    const headers = ["metric", "value"];
    const rows = [
      ["total_production", summary.totalProduction],
      ["ok", summary.totalOk],
      ["nok", summary.totalNok],
      ["scrap", summary.totalScrap],
      ["ftq_percent", formatPercent(summary.globalFtq)],
      ["fpy_percent", formatPercent(summary.globalFpy)],
    ];
    const csv = [headers.join(","), ...rows.map((row) => row.map((value) => JSON.stringify(value)).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "production_reports_summary.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  if (!canReports) {
    return (
      <Layout
        auth={auth}
        onLogout={onLogout}
        active="reports"
        tenantId={tenantId}
        setTenantId={setTenantId}
        lang={lang}
        setLang={setLang}
        t={t}
        theme={theme}
        setTheme={setTheme}
      >
        <div className="card">
          <h2>{t("reports.title")}</h2>
          <p className="notice">{t("reports.noAccess")}</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout
      auth={auth}
      onLogout={onLogout}
      active="reports"
      tenantId={tenantId}
      setTenantId={setTenantId}
      lang={lang}
      setLang={setLang}
      t={t}
      theme={theme}
      setTheme={setTheme}
    >
      <div className="sticky-stack">
        <div className="reports-hero card page-header">
          <div className="page-header-copy">
            <span className="eyebrow">{t("reports.eyebrow")}</span>
            <h2>{t("reports.title")}</h2>
            <p>{t("reports.subtitle")}</p>
          </div>
          <div className="page-header-meta reports-hero-actions">
            <button className="secondary" onClick={exportCsv}>{t("common.exportCsv")}</button>
            <button className="primary reports-export" onClick={exportExcel}>{t("common.exportExcel")}</button>
          </div>
        </div>

        <div className="card reports-filters compact-toolbar">
          <div className="section-head">
            <div>
              <h3>{t("reports.filters")}</h3>
              <p className="muted">{t("reports.filtersHint")}</p>
            </div>
            <div className="row-space">
              <button className="secondary" onClick={() => loadAnalytics()} disabled={loading}>
                {loading ? t("common.loading") : t("common.apply")}
              </button>
              <button
                className="ghost"
                onClick={() => {
                  const today = new Date().toISOString().slice(0, 10);
                  setFilters({ ...emptyFilters, date_from: today, date_to: today });
                  setTraceability([]);
                }}
              >
                {t("common.clear")}
              </button>
            </div>
          </div>
          <div className="grid reports-filter-grid">
            <div className="field">
              <label>{t("reports.dateFrom")}</label>
              <input type="date" value={filters.date_from} onChange={(event) => setFilters({ ...filters, date_from: event.target.value })} />
            </div>
            <div className="field">
              <label>{t("reports.dateTo")}</label>
              <input type="date" value={filters.date_to} onChange={(event) => setFilters({ ...filters, date_to: event.target.value })} />
            </div>
            <div className="field">
              <label>{t("reports.plantCode")}</label>
              <input value={filters.plant_code} onChange={(event) => setFilters({ ...filters, plant_code: event.target.value })} placeholder="PLANT-ES" />
            </div>
            <div className="field">
              <label>{t("reports.lineCode")}</label>
              <input value={filters.line_code} onChange={(event) => setFilters({ ...filters, line_code: event.target.value })} placeholder="LINE-A" />
            </div>
          </div>
        </div>
      </div>

      <div className="reports-kpis">
        <div className="report-kpi report-kpi-production">
          <span>{t("reports.kpiTotalProduction")}</span>
          <strong>{summary.totalProduction}</strong>
          <small>{t("reports.kpiTotalProductionHint")}</small>
        </div>
        <div className="report-kpi report-kpi-quality">
          <span>{t("reports.kpiOkNok")}</span>
          <strong>{summary.totalOk} / {summary.totalNok}</strong>
          <small>{t("reports.kpiOkNokHint")}</small>
        </div>
        <div className="report-kpi report-kpi-ftq">
          <span>{t("reports.kpiFtq")}</span>
          <strong>{formatPercent(summary.globalFtq)}</strong>
          <small>{t("reports.kpiFtqHint")}</small>
        </div>
        <div className="report-kpi report-kpi-fpy">
          <span>{t("reports.kpiFpy")}</span>
          <strong>{formatPercent(summary.globalFpy)}</strong>
          <small>{t("reports.kpiFpyHint")}</small>
        </div>
      </div>

      <div className="grid two reports-grid">
        <div className="card reports-panel">
          <div className="section-head">
            <div>
              <h3>{t("reports.dailyTotalTitle")}</h3>
              <p className="muted">{t("reports.dailyTotalSubtitle")}</p>
            </div>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>{t("reports.day")}</th>
                <th>{t("reports.total")}</th>
              </tr>
            </thead>
            <tbody>
              {dailyTotal.map((row) => (
                <tr key={row.production_day}>
                  <td>{row.production_day}</td>
                  <td>{row.total_production}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card reports-panel">
          <div className="section-head">
            <div>
              <h3>{t("reports.byLineTitle")}</h3>
              <p className="muted">{t("reports.byLineSubtitle")}</p>
            </div>
          </div>
          <div className="bar-list">
            {byLine.map((row) => {
              const max = byLine[0]?.total_production || 1;
              const width = `${(Number(row.total_production || 0) / max) * 100}%`;
              return (
                <div key={row.line_code} className="bar-row">
                  <div className="bar-row-meta">
                    <strong>{row.line_code}</strong>
                    <span>{row.total_production}</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card reports-panel">
          <div className="section-head">
            <div>
              <h3>{t("reports.shiftQualityTitle")}</h3>
              <p className="muted">{t("reports.shiftQualitySubtitle")}</p>
            </div>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>{t("reports.shift")}</th>
                <th>OK</th>
                <th>NOK</th>
                <th>SCRAP</th>
                <th>REWORK</th>
              </tr>
            </thead>
            <tbody>
              {okNokByShift.map((row, index) => (
                <tr key={`${row.shift_code || "na"}-${index}`}>
                  <td>{row.shift_code || "-"}</td>
                  <td>{row.ok_count}</td>
                  <td>{row.nok_count}</td>
                  <td>{row.scrap_count}</td>
                  <td>{row.rework_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card reports-panel">
          <div className="section-head">
            <div>
              <h3>{t("reports.defectsTitle")}</h3>
              <p className="muted">{t("reports.defectsSubtitle")}</p>
            </div>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>{t("reports.errorCode")}</th>
                <th>{t("reports.description")}</th>
                <th>{t("reports.count")}</th>
              </tr>
            </thead>
            <tbody>
              {topDefects.map((row) => (
                <tr key={`${row.error_code}-${row.error_description || ""}`}>
                  <td>{row.error_code}</td>
                  <td>{row.error_description || "-"}</td>
                  <td>{row.defect_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card reports-panel" style={{ marginTop: 20 }}>
        <div className="section-head">
          <div>
            <h3>{t("reports.ftqFpyTitle")}</h3>
            <p className="muted">{t("reports.ftqFpySubtitle")}</p>
          </div>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>{t("reports.day")}</th>
              <th>{t("reports.lineCode")}</th>
              <th>{t("reports.firstPassTotal")}</th>
              <th>{t("reports.firstPassOk")}</th>
              <th>FTQ</th>
              <th>{t("reports.serialTotal")}</th>
              <th>{t("reports.serialOk")}</th>
              <th>FPY</th>
            </tr>
          </thead>
          <tbody>
            {ftqFpy.map((row) => (
              <tr key={`${row.production_day}-${row.line_code}`}>
                <td>{row.production_day}</td>
                <td>{row.line_code}</td>
                <td>{row.first_pass_total}</td>
                <td>{row.first_pass_ok}</td>
                <td>{formatPercent(row.ftq_percent)}</td>
                <td>{row.serial_total}</td>
                <td>{row.serial_ok}</td>
                <td>{formatPercent(row.fpy_percent)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid two reports-grid" style={{ marginTop: 20 }}>
        <div className="card reports-panel">
          <div className="section-head">
            <div>
              <h3>{t("reports.cycleTitle")}</h3>
              <p className="muted">{t("reports.cycleSubtitle")}</p>
            </div>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>{t("reports.lineCode")}</th>
                <th>{t("reports.avgCycle")}</th>
                <th>{t("reports.samples")}</th>
              </tr>
            </thead>
            <tbody>
              {cycleTimeByLine.map((row) => (
                <tr key={row.line_code}>
                  <td>{row.line_code}</td>
                  <td>{formatNumber(row.average_cycle_time_seconds, 3)} s</td>
                  <td>{row.sample_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card reports-panel">
          <div className="section-head">
            <div>
              <h3>{t("reports.traceabilityTitle")}</h3>
              <p className="muted">{t("reports.traceabilitySubtitle")}</p>
            </div>
            <div className="row-space">
              <input
                className="inline-input"
                value={filters.trace_serial}
                onChange={(event) => setFilters({ ...filters, trace_serial: event.target.value })}
                placeholder={t("reports.traceabilityPlaceholder")}
              />
              <button className="secondary" onClick={handleTraceabilitySearch}>{t("reports.searchSerial")}</button>
            </div>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>{t("reports.timestamp")}</th>
                <th>{t("reports.lineCode")}</th>
                <th>{t("reports.stationCode")}</th>
                <th>{t("reports.machineCode")}</th>
                <th>{t("reports.result")}</th>
              </tr>
            </thead>
            <tbody>
              {traceability.map((row) => (
                <tr key={row.id}>
                  <td>{row.production_datetime}</td>
                  <td>{row.line_code}</td>
                  <td>{row.station_code || "-"}</td>
                  <td>{row.machine_code || "-"}</td>
                  <td>
                    <span className={`result-pill result-${String(row.result).toLowerCase()}`}>{row.result}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {status ? <div className="notice">{status}</div> : null}
    </Layout>
  );
}
