import { useEffect, useMemo, useState } from "react";
import Layout from "../ui/Layout.jsx";
import { request } from "../api.js";

const emptyItem = {
  item_id: "",
  model_id: "",
  line_id: "",
  location_id: 1,
  cell_id: "",
  id_user: "",
  status_id: "PASS",
  value1_int: "",
  value2_int: "",
  value3_int: "",
  value4_int: "",
  value5_int: "",
  value1_str: "",
  value2_str: "",
  value3_str: "",
  value4_str: "",
  value5_str: "",
};

const emptyFilters = {
  status_id: "",
  line_id: "",
  model_id: "",
  cell_id: "",
  id_user: "",
  create_date_from: "",
  create_date_to: "",
  last_test_date_from: "",
  last_test_date_to: "",
};

const toPayload = (form) => ({
  ...form,
  location_id: Number(form.location_id),
  value1_int: form.value1_int === "" ? null : Number(form.value1_int),
  value2_int: form.value2_int === "" ? null : Number(form.value2_int),
  value3_int: form.value3_int === "" ? null : Number(form.value3_int),
  value4_int: form.value4_int === "" ? null : Number(form.value4_int),
  value5_int: form.value5_int === "" ? null : Number(form.value5_int),
  value1_str: form.value1_str || null,
  value2_str: form.value2_str || null,
  value3_str: form.value3_str || null,
  value4_str: form.value4_str || null,
  value5_str: form.value5_str || null,
});

export default function ItemsPage({ auth, onLogout, tenantId, setTenantId, csrfToken, t, lang, setLang, theme, setTheme }) {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [form, setForm] = useState(emptyItem);
  const [filters, setFilters] = useState(emptyFilters);
  const [editorMode, setEditorMode] = useState("idle");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);

  const canWrite = useMemo(() => auth.permissions?.includes("items.write"), [auth]);
  const canUsers = useMemo(() => auth.permissions?.includes("users.read"), [auth]);
  const canMasters = useMemo(() => auth.permissions?.includes("masters.read"), [auth]);

  const [lines, setLines] = useState([]);
  const [cells, setCells] = useState([]);
  const [models, setModels] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [users, setUsers] = useState([]);

  const buildQuery = () => {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    return params.toString();
  };

  const loadItems = async () => {
    const query = buildQuery();
    const data = await request(`/items?${query}`, { tenantId });
    setItems(data);
  };

  useEffect(() => {
    loadItems().catch(() => {});
  }, [limit, offset]);

  useEffect(() => {
    if (!canMasters) return;
    request("/lines", { tenantId }).then(setLines).catch(() => {});
    request("/cells", { tenantId }).then(setCells).catch(() => {});
    request("/models", { tenantId }).then(setModels).catch(() => {});
    request("/statuses", { tenantId }).then(setStatuses).catch(() => {});
  }, [canMasters, tenantId]);

  useEffect(() => {
    if (!canUsers) return;
    request("/users", { tenantId }).then(setUsers).catch(() => {});
  }, [canUsers, tenantId]);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus("");
    setLoading(true);
    try {
      await request("/items", {
        method: "POST",
        data: toPayload(form),
        tenantId,
        csrfToken,
      });
      setForm(emptyItem);
      setEditorMode("idle");
      await loadItems();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (item) => {
    setSelectedItem(item);
    setEditorMode("edit");
    setForm({
      ...emptyItem,
      ...item,
      location_id: item.location_id ?? 1,
      value1_int: item.value1_int ?? "",
      value2_int: item.value2_int ?? "",
      value3_int: item.value3_int ?? "",
      value4_int: item.value4_int ?? "",
      value5_int: item.value5_int ?? "",
      value1_str: item.value1_str ?? "",
      value2_str: item.value2_str ?? "",
      value3_str: item.value3_str ?? "",
      value4_str: item.value4_str ?? "",
      value5_str: item.value5_str ?? "",
    });
  };

  const handleUpdate = async () => {
    if (!selectedItem) return;
    setStatus("");
    setLoading(true);
    try {
      const payload = { ...toPayload(form) };
      delete payload.item_id;
      await request(`/items/${selectedItem.item_id}`, {
        method: "PATCH",
        data: payload,
        tenantId,
        csrfToken,
      });
      await loadItems();
      setStatus(t("items.updated"));
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedItem) return;
    setStatus("");
    setLoading(true);
    try {
      await request(`/items/${selectedItem.item_id}`, {
        method: "DELETE",
        tenantId,
        csrfToken,
      });
      setSelectedItem(null);
      setForm(emptyItem);
      setEditorMode("idle");
      await loadItems();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = () => {
    if (!items.length) return;
    const headers = [
      "item_id",
      "model_id",
      "line_id",
      "location_id",
      "cell_id",
      "id_user",
      "status_id",
      "create_date",
      "last_test_date",
      "value1_int",
      "value2_int",
      "value3_int",
      "value4_int",
      "value5_int",
      "value1_str",
      "value2_str",
      "value3_str",
      "value4_str",
      "value5_str",
    ];
    const rows = items.map((item) => headers.map((key) => JSON.stringify(item[key] ?? "")).join(","));
    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "items_export.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportExcel = async () => {
    if (!items.length) return;
    const XLSX = await import("xlsx");
    const worksheet = XLSX.utils.json_to_sheet(items);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Items");
    XLSX.writeFile(workbook, "items_export.xlsx");
  };

  return (
    <Layout
      auth={auth}
      onLogout={onLogout}
      active="items"
      tenantId={tenantId}
      setTenantId={setTenantId}
      lang={lang}
      setLang={setLang}
      t={t}
      theme={theme}
      setTheme={setTheme}
    >
      <div className="sticky-stack">
        <div className="card page-header">
          <div className="page-header-copy">
            <h2>{t("items.title")}</h2>
            <p>{t("items.subtitle")}</p>
          </div>
          <div className="page-header-meta">
            <div className="badge">{t("common.tenant")}: {auth.tenant_id}</div>
          </div>
        </div>

        <div className="card compact-toolbar" style={{ marginBottom: 0 }}>
          <div className="row-space">
            <div className="muted">{t("items.filters")}</div>
            <div className="row-space">
              <button className="secondary" onClick={() => loadItems()}>
                {t("common.apply")}
              </button>
              <button
                className="ghost"
                onClick={() => {
                  setFilters(emptyFilters);
                  setOffset(0);
                }}
              >
                {t("common.clear")}
              </button>
            </div>
          </div>
          <div className="grid three" style={{ marginTop: 10 }}>
            {canMasters && statuses.length ? (
              <select className="inline-input" value={filters.status_id} onChange={(e) => setFilters({ ...filters, status_id: e.target.value })}>
                <option value="">{t("common.select")}</option>
                {statuses.map((row) => (
                  <option key={row.status_id} value={row.status_id}>{row.status_id}</option>
                ))}
              </select>
            ) : (
              <input className="inline-input" placeholder={t("fields.statusId")} value={filters.status_id} onChange={(e) => setFilters({ ...filters, status_id: e.target.value })} />
            )}
            {canMasters && lines.length ? (
              <select className="inline-input" value={filters.line_id} onChange={(e) => setFilters({ ...filters, line_id: e.target.value })}>
                <option value="">{t("common.select")}</option>
                {lines.map((row) => (
                  <option key={row.line_id} value={row.line_id}>{row.line_id}</option>
                ))}
              </select>
            ) : (
              <input className="inline-input" placeholder={t("fields.lineId")} value={filters.line_id} onChange={(e) => setFilters({ ...filters, line_id: e.target.value })} />
            )}
            {canMasters && models.length ? (
              <select className="inline-input" value={filters.model_id} onChange={(e) => setFilters({ ...filters, model_id: e.target.value })}>
                <option value="">{t("common.select")}</option>
                {models.map((row) => (
                  <option key={row.model_id} value={row.model_id}>{row.model_id}</option>
                ))}
              </select>
            ) : (
              <input className="inline-input" placeholder={t("fields.modelId")} value={filters.model_id} onChange={(e) => setFilters({ ...filters, model_id: e.target.value })} />
            )}
            {canMasters && cells.length ? (
              <select className="inline-input" value={filters.cell_id} onChange={(e) => setFilters({ ...filters, cell_id: e.target.value })}>
                <option value="">{t("common.select")}</option>
                {cells.map((row) => (
                  <option key={row.cell_id} value={row.cell_id}>{row.cell_id}</option>
                ))}
              </select>
            ) : (
              <input className="inline-input" placeholder={t("fields.cellId")} value={filters.cell_id} onChange={(e) => setFilters({ ...filters, cell_id: e.target.value })} />
            )}
            {canUsers && users.length ? (
              <select className="inline-input" value={filters.id_user} onChange={(e) => setFilters({ ...filters, id_user: e.target.value })}>
                <option value="">{t("common.select")}</option>
                {users.map((row) => (
                  <option key={row.id_user} value={row.id_user}>{row.id_user}</option>
                ))}
              </select>
            ) : (
              <input className="inline-input" placeholder={t("fields.userId")} value={filters.id_user} onChange={(e) => setFilters({ ...filters, id_user: e.target.value })} />
            )}
          </div>
          <div className="grid three" style={{ marginTop: 8 }}>
            <input className="inline-input" type="datetime-local" value={filters.create_date_from} onChange={(e) => setFilters({ ...filters, create_date_from: e.target.value })} />
            <input className="inline-input" type="datetime-local" value={filters.create_date_to} onChange={(e) => setFilters({ ...filters, create_date_to: e.target.value })} />
            <input className="inline-input" type="datetime-local" value={filters.last_test_date_from} onChange={(e) => setFilters({ ...filters, last_test_date_from: e.target.value })} />
            <input className="inline-input" type="datetime-local" value={filters.last_test_date_to} onChange={(e) => setFilters({ ...filters, last_test_date_to: e.target.value })} />
          </div>
        </div>

        <div className="card compact-toolbar" style={{ marginBottom: 0 }}>
          <div className="row-space">
            <div className="muted">{t("items.pagination")}</div>
            <div className="row-space">
              <input className="inline-input" type="number" min="1" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
              <input className="inline-input" type="number" min="0" value={offset} onChange={(e) => setOffset(Number(e.target.value))} />
              <button className="secondary" onClick={() => loadItems()}>{t("common.reload")}</button>
              <button className="secondary" onClick={exportCsv}>{t("common.exportCsv")}</button>
              <button className="secondary" onClick={exportExcel}>{t("common.exportExcel")}</button>
            </div>
          </div>
        </div>
      </div>

      <div className="crud-grid">
        <div className="card crud-card crud-list-card">
          <div className="crud-card-header">
            <div>
              <h3>{t("items.list")}</h3>
              <p>{t("items.subtitle")}</p>
            </div>
            <div className="row-space">
              {canWrite ? (
                <button
                  className="secondary"
                  type="button"
                  onClick={() => {
                    setSelectedItem(null);
                    setForm(emptyItem);
                    setStatus("");
                    setEditorMode("create");
                  }}
                >
                  {t("items.new")}
                </button>
              ) : null}
              <div className="crud-card-metric">{items.length}</div>
            </div>
          </div>
          <div className="table-shell">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("fields.itemId")}</th>
                  <th>{t("fields.modelId")}</th>
                  <th>{t("fields.lineId")}</th>
                  <th>{t("fields.cellId")}</th>
                  <th>{t("fields.status")}</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.item_id} onClick={() => handleSelect(item)} className={selectedItem?.item_id === item.item_id ? "active" : ""}>
                    <td>{item.item_id}</td>
                    <td>{item.model_id}</td>
                    <td>{item.line_id}</td>
                    <td>{item.cell_id}</td>
                    <td>{item.status_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card crud-card crud-editor-card">
          <div className="crud-card-header">
            <div>
              <h3>{editorMode === "edit" ? t("items.edit") : t("items.new")}</h3>
              <p>{editorMode === "edit" ? t("items.edit") : t("items.new")}</p>
            </div>
          </div>
          {!canWrite && <p className="muted">{t("items.noWrite")}</p>}
          {editorMode === "idle" ? (
            <div className="empty-state">{t("items.new")} / {t("items.edit")}</div>
          ) : (
            <>
          {selectedItem ? <div className="editor-banner">{t("fields.itemId")}: {selectedItem.item_id}</div> : null}
          <form onSubmit={handleCreate} className="form" style={{ marginTop: 12 }}>
            <div className="field">
              <label>{t("fields.itemId")}</label>
              <input value={form.item_id} onChange={(e) => setForm({ ...form, item_id: e.target.value })} required disabled={!!selectedItem} />
            </div>
            <div className="field">
              <label>{t("fields.modelId")}</label>
              {canMasters && models.length ? (
                <select className="inline-input" value={form.model_id} onChange={(e) => setForm({ ...form, model_id: e.target.value })}>
                  <option value="">{t("common.select")}</option>
                  {models.map((row) => (
                    <option key={row.model_id} value={row.model_id}>{row.model_id} - {row.description_model}</option>
                  ))}
                </select>
              ) : (
                <input value={form.model_id} onChange={(e) => setForm({ ...form, model_id: e.target.value })} required />
              )}
            </div>
            <div className="field">
              <label>{t("fields.lineId")}</label>
              {canMasters && lines.length ? (
                <select className="inline-input" value={form.line_id} onChange={(e) => setForm({ ...form, line_id: e.target.value })}>
                  <option value="">{t("common.select")}</option>
                  {lines.map((row) => (
                    <option key={row.line_id} value={row.line_id}>{row.line_id} - {row.description_line}</option>
                  ))}
                </select>
              ) : (
                <input value={form.line_id} onChange={(e) => setForm({ ...form, line_id: e.target.value })} required />
              )}
            </div>
            <div className="field">
              <label>{t("fields.locationId")}</label>
              <input type="number" value={form.location_id} onChange={(e) => setForm({ ...form, location_id: e.target.value })} required />
            </div>
            <div className="field">
              <label>{t("fields.cellId")}</label>
              {canMasters && cells.length ? (
                <select className="inline-input" value={form.cell_id} onChange={(e) => setForm({ ...form, cell_id: e.target.value })}>
                  <option value="">{t("common.select")}</option>
                  {cells.map((row) => (
                    <option key={row.cell_id} value={row.cell_id}>{row.cell_id} - {row.description_cell}</option>
                  ))}
                </select>
              ) : (
                <input value={form.cell_id} onChange={(e) => setForm({ ...form, cell_id: e.target.value })} required />
              )}
            </div>
            <div className="field">
              <label>{t("login.user")}</label>
              {canUsers && users.length ? (
                <select className="inline-input" value={form.id_user} onChange={(e) => setForm({ ...form, id_user: e.target.value })}>
                  <option value="">{t("common.select")}</option>
                  {users.map((row) => (
                    <option key={row.id_user} value={row.id_user}>{row.id_user} - {row.name_user}</option>
                  ))}
                </select>
              ) : (
                <input value={form.id_user} onChange={(e) => setForm({ ...form, id_user: e.target.value })} required />
              )}
            </div>
            <div className="field">
              <label>{t("fields.statusId")}</label>
              {canMasters && statuses.length ? (
                <select className="inline-input" value={form.status_id} onChange={(e) => setForm({ ...form, status_id: e.target.value })}>
                  <option value="">{t("common.select")}</option>
                  {statuses.map((row) => (
                    <option key={row.status_id} value={row.status_id}>{row.status_id} - {row.description_status}</option>
                  ))}
                </select>
              ) : (
                <input value={form.status_id} onChange={(e) => setForm({ ...form, status_id: e.target.value })} required />
              )}
            </div>

            <details className="details">
              <summary>{t("items.optional")}</summary>
              <div className="grid three">
                <input className="inline-input" placeholder="value1_int" value={form.value1_int} onChange={(e) => setForm({ ...form, value1_int: e.target.value })} />
                <input className="inline-input" placeholder="value2_int" value={form.value2_int} onChange={(e) => setForm({ ...form, value2_int: e.target.value })} />
                <input className="inline-input" placeholder="value3_int" value={form.value3_int} onChange={(e) => setForm({ ...form, value3_int: e.target.value })} />
                <input className="inline-input" placeholder="value4_int" value={form.value4_int} onChange={(e) => setForm({ ...form, value4_int: e.target.value })} />
                <input className="inline-input" placeholder="value5_int" value={form.value5_int} onChange={(e) => setForm({ ...form, value5_int: e.target.value })} />
              </div>
              <div className="grid three" style={{ marginTop: 10 }}>
                <input className="inline-input" placeholder="value1_str" value={form.value1_str} onChange={(e) => setForm({ ...form, value1_str: e.target.value })} />
                <input className="inline-input" placeholder="value2_str" value={form.value2_str} onChange={(e) => setForm({ ...form, value2_str: e.target.value })} />
                <input className="inline-input" placeholder="value3_str" value={form.value3_str} onChange={(e) => setForm({ ...form, value3_str: e.target.value })} />
                <input className="inline-input" placeholder="value4_str" value={form.value4_str} onChange={(e) => setForm({ ...form, value4_str: e.target.value })} />
                <input className="inline-input" placeholder="value5_str" value={form.value5_str} onChange={(e) => setForm({ ...form, value5_str: e.target.value })} />
              </div>
            </details>

            {!selectedItem ? (
              <div className="editor-actions compact-end">
                <button
                  className="ghost"
                  type="button"
                  onClick={() => {
                    setEditorMode("idle");
                    setForm(emptyItem);
                    setStatus("");
                  }}
                >
                  {t("common.cancel")}
                </button>
                <button className="primary" type="submit" disabled={!canWrite || loading}>{t("common.create")}</button>
              </div>
            ) : (
              <div className="editor-actions">
                <button className="danger" type="button" onClick={handleDelete} disabled={!canWrite || loading}>{t("common.delete")}</button>
                <button className="secondary" type="button" onClick={handleUpdate} disabled={!canWrite || loading}>{t("common.update")}</button>
              </div>
            )}
          </form>
            </>
          )}
        </div>
      </div>

      {status ? <div className="notice">{status}</div> : null}
    </Layout>
  );
}
