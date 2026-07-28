// ---------------------------------------------------------------------------
// Data Explorer front-end. Talks to the Flask API in app.py.
// ---------------------------------------------------------------------------
const state = {
  table: null,
  columns: [],          // [{name, type}]
  selected: new Set(),  // selected column names
  filters: [],          // [{type, column, value} | {type:'range', column, start, end}]
  tableRows: 0,
};

const $ = (id) => document.getElementById(id);
const api = async (url, opts) => (await fetch(url, opts)).json();

function fmtNum(n) {
  if (n === null || n === undefined) return "—";
  if (typeof n === "number" && !Number.isInteger(n)) n = Math.round(n * 100) / 100;
  return typeof n === "number" ? n.toLocaleString() : n;
}

function toast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove("show"), 2200);
}

const colType = (name) => (state.columns.find((c) => c.name === name) || {}).type;
const numericCols = () => state.columns.filter((c) => c.type === "numerical").map((c) => c.name);
const categoricalCols = () => state.columns.filter((c) => c.type === "categorical").map((c) => c.name);

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
async function boot() {
  const data = await api("/api/tables");
  $("dbName").textContent = data.db;
  const sel = $("tableSelect");
  sel.innerHTML = "";
  data.tables.forEach((t) => {
    const o = document.createElement("option");
    o.value = t.name;
    o.textContent = `${t.name}  (${t.rows.toLocaleString()} rows)`;
    o.dataset.rows = t.rows;
    sel.appendChild(o);
  });
  sel.addEventListener("change", () => loadTable(sel.value));
  await loadTable(data.tables[0].name);
}

async function loadTable(table) {
  state.table = table;
  state.filters = [];
  const data = await api(`/api/columns?table=${encodeURIComponent(table)}`);
  state.columns = data.columns;
  state.tableRows = data.rows;
  state.selected = new Set(state.columns.map((c) => c.name)); // default: all selected

  renderColumnList();
  renderFilterColumnOptions();
  renderCalcOptions();
  renderChartOptions();
  renderFilterChips();
  updateKpis({ matched: data.rows });
  await runQuery();
  await refreshChart();
}

// ---------------------------------------------------------------------------
// Column picker
// ---------------------------------------------------------------------------
function renderColumnList() {
  const wrap = $("colList");
  wrap.innerHTML = "";
  state.columns.forEach((c) => {
    const row = document.createElement("label");
    row.className = "col-item";
    const isNum = c.type === "numerical";
    row.innerHTML = `
      <input type="checkbox" ${state.selected.has(c.name) ? "checked" : ""} data-col="${c.name}"/>
      <span>${c.name}</span>
      <span class="type-tag ${isNum ? "num" : "cat"}">${isNum ? "num" : "cat"}</span>`;
    row.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) state.selected.add(c.name);
      else state.selected.delete(c.name);
      updateKpis({});
    });
    wrap.appendChild(row);
  });
}

$("selectAll").addEventListener("click", () => {
  state.selected = new Set(state.columns.map((c) => c.name));
  renderColumnList();
  updateKpis({});
});
$("clearCols").addEventListener("click", () => {
  state.selected.clear();
  renderColumnList();
  updateKpis({});
});

// ---------------------------------------------------------------------------
// Filters
// ---------------------------------------------------------------------------
function renderFilterColumnOptions() {
  const sel = $("filterColumn");
  sel.innerHTML = "";
  state.columns.forEach((c) => {
    const o = document.createElement("option");
    o.value = c.name;
    o.textContent = `${c.name} (${c.type === "numerical" ? "num" : "cat"})`;
    sel.appendChild(o);
  });
  sel.addEventListener("change", renderFilterInput);
  renderFilterInput();
}

async function renderFilterInput() {
  const col = $("filterColumn").value;
  const area = $("filterInputArea");
  if (!col) { area.innerHTML = ""; return; }
  if (colType(col) === "categorical") {
    area.innerHTML = `<label class="field" style="flex:1;margin-bottom:0"><span>Equals</span><select id="fCatValue"></select></label>`;
    const data = await api(`/api/values?table=${encodeURIComponent(state.table)}&column=${encodeURIComponent(col)}`);
    const sel = $("fCatValue");
    data.values.forEach((v) => {
      const o = document.createElement("option");
      o.value = v; o.textContent = v; sel.appendChild(o);
    });
  } else {
    const b = await api(`/api/bounds?table=${encodeURIComponent(state.table)}&column=${encodeURIComponent(col)}`);
    area.innerHTML = `
      <label class="field" style="flex:1;margin-bottom:0"><span>Greater than</span><input type="number" id="fStart" placeholder="${b.min}"/></label>
      <label class="field" style="flex:1;margin-bottom:0"><span>Less than</span><input type="number" id="fEnd" placeholder="${b.max}"/></label>`;
  }
}

$("addFilter").addEventListener("click", () => {
  const col = $("filterColumn").value;
  if (!col) return;
  if (colType(col) === "categorical") {
    const v = $("fCatValue").value;
    state.filters.push({ type: "category", column: col, value: v });
  } else {
    const s = $("fStart").value, e = $("fEnd").value;
    if (s === "" && e === "") { toast("Enter a start and/or end value."); return; }
    state.filters.push({
      type: "range", column: col,
      start: s === "" ? null : parseFloat(s),
      end: e === "" ? null : parseFloat(e),
    });
  }
  renderFilterChips();
  runQuery();
  refreshChart();
});

function renderFilterChips() {
  const wrap = $("filterChips");
  if (!state.filters.length) {
    wrap.innerHTML = `<span class="empty-note">No filters applied — showing all rows.</span>`;
    return;
  }
  wrap.innerHTML = "";
  state.filters.forEach((f, i) => {
    let text;
    if (f.type === "category") text = `${f.column} = <b>${f.value}</b>`;
    else {
      const parts = [];
      if (f.start !== null) parts.push(`&gt; ${f.start}`);
      if (f.end !== null) parts.push(`&lt; ${f.end}`);
      text = `${f.column} <b>${parts.join(" &amp; ")}</b>`;
    }
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.innerHTML = `${text} <span class="x" data-i="${i}">✕</span>`;
    chip.querySelector(".x").addEventListener("click", () => {
      state.filters.splice(i, 1);
      renderFilterChips();
      runQuery();
      refreshChart();
    });
    wrap.appendChild(chip);
  });
}

// ---------------------------------------------------------------------------
// Run query -> data table
// ---------------------------------------------------------------------------
async function runQuery() {
  const cols = state.columns.map((c) => c.name).filter((c) => state.selected.has(c));
  const body = {
    table: state.table,
    columns: cols,
    limit: parseInt($("limitInput").value || "0", 10),
    filters: state.filters,
  };
  const data = await api("/api/query", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  renderTable(data);
  updateKpis({ matched: data.matched });
  const cap = data.limited ? ` (limited to ${data.returned.toLocaleString()})` : "";
  $("resultMeta").textContent = `Showing ${data.returned.toLocaleString()} of ${data.matched.toLocaleString()} matching rows${cap}.`;
}

function renderTable(data) {
  const thead = $("dataTable").querySelector("thead");
  const tbody = $("dataTable").querySelector("tbody");
  if (!data.columns.length) {
    thead.innerHTML = ""; tbody.innerHTML = `<tr><td class="loading">Select at least one column.</td></tr>`;
    return;
  }
  thead.innerHTML = `<tr>${data.columns.map((c) => `<th>${c}</th>`).join("")}</tr>`;
  if (!data.rows.length) {
    tbody.innerHTML = `<tr><td class="loading" colspan="${data.columns.length}">No rows match these filters.</td></tr>`;
    return;
  }
  tbody.innerHTML = data.rows
    .map((r) => `<tr>${r.map((v) => `<td>${v === null ? "<span style='color:var(--muted)'>null</span>" : v}</td>`).join("")}</tr>`)
    .join("");
}

// ---------------------------------------------------------------------------
// KPIs
// ---------------------------------------------------------------------------
function updateKpis({ matched }) {
  $("kpiTotal").textContent = state.tableRows.toLocaleString();
  if (matched !== undefined) $("kpiMatch").textContent = matched.toLocaleString();
  $("kpiCols").textContent = state.selected.size;
  $("kpiFilters").textContent = state.filters.length;
}

// ---------------------------------------------------------------------------
// Calculations
// ---------------------------------------------------------------------------
const CALC_OPS = [
  { op: "T", label: "Total" },
  { op: "A", label: "Average" },
  { op: "M", label: "Median" },
  { op: "H", label: "Highest" },
  { op: "L", label: "Lowest" },
];

function renderCalcOptions() {
  const sel = $("calcColumn");
  sel.innerHTML = "";
  state.columns.forEach((c) => {
    const o = document.createElement("option");
    o.value = c.name;
    o.textContent = `${c.name} (${c.type === "numerical" ? "num" : "cat"})`;
    sel.appendChild(o);
  });
  sel.addEventListener("change", onCalcColumnChange);

  const ops = $("calcOps");
  ops.innerHTML = "";
  CALC_OPS.forEach((c) => {
    const b = document.createElement("button");
    b.textContent = c.label;
    b.dataset.op = c.op;
    b.addEventListener("click", () => runCalc(c.op));
    ops.appendChild(b);
  });
  onCalcColumnChange();
}

async function onCalcColumnChange() {
  const col = $("calcColumn").value;
  const isCat = colType(col) === "categorical";
  const wrap = $("calcValueWrap");
  wrap.hidden = !isCat;
  // categorical columns: only Count-of-value makes sense
  document.querySelectorAll("#calcOps button").forEach((b) => {
    b.style.display = isCat && b.dataset.op !== "T" ? "none" : "";
    if (isCat && b.dataset.op === "T") b.textContent = "Count";
    else if (!isCat && b.dataset.op === "T") b.textContent = "Total";
  });
  if (isCat) {
    const data = await api(`/api/values?table=${encodeURIComponent(state.table)}&column=${encodeURIComponent(col)}`);
    const sel = $("calcValue");
    sel.innerHTML = "";
    data.values.forEach((v) => {
      const o = document.createElement("option");
      o.value = v; o.textContent = v; sel.appendChild(o);
    });
  }
  $("calcResult").classList.remove("show");
}

async function runCalc(op) {
  const col = $("calcColumn").value;
  const isCat = colType(col) === "categorical";
  const body = { table: state.table, column: col, op, filters: state.filters };
  if (isCat) body.value = $("calcValue").value;
  const data = await api("/api/calculate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (data.error) { toast(data.error); return; }
  const res = $("calcResult");
  if (data.op === "COUNT") {
    $("crLabel").textContent = `Count of "${data.value}" in ${data.column}`;
  } else {
    $("crLabel").textContent = `${data.op} of ${data.column}`;
  }
  $("crValue").textContent = fmtNum(data.result);
  res.classList.add("show");
}

// ---------------------------------------------------------------------------
// Distribution chart (simple horizontal bars, no external libs)
// ---------------------------------------------------------------------------
function renderChartOptions() {
  const sel = $("chartColumn");
  sel.innerHTML = "";
  state.columns.forEach((c) => {
    const o = document.createElement("option");
    o.value = c.name;
    o.textContent = c.name;
    sel.appendChild(o);
  });
  sel.addEventListener("change", refreshChart);
}

async function refreshChart() {
  const col = $("chartColumn").value;
  if (!col) return;
  const bars = $("chartBars");
  bars.innerHTML = `<div class="loading">Loading…</div>`;
  const data = await api(`/api/distribution?table=${encodeURIComponent(state.table)}&column=${encodeURIComponent(col)}`);
  if (!data.labels || !data.labels.length) { bars.innerHTML = `<div class="loading">No data.</div>`; return; }
  const max = Math.max(...data.counts);
  bars.innerHTML = data.labels
    .map((lab, i) => {
      const pct = max ? (data.counts[i] / max) * 100 : 0;
      return `<div class="bar-row">
        <div class="b-label" title="${lab}">${lab}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
        <div class="b-count">${data.counts[i].toLocaleString()}</div>
      </div>`;
    })
    .join("");
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------
$("exportBtn").addEventListener("click", async () => {
  const cols = state.columns.map((c) => c.name).filter((c) => state.selected.has(c));
  const body = {
    table: state.table, columns: cols,
    limit: parseInt($("limitInput").value || "0", 10),
    filters: state.filters, filename: `${state.table}_export`,
  };
  const res = await fetch("/api/export", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `${state.table}_export.csv`;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  toast("CSV exported ✓");
});

$("runQuery").addEventListener("click", runQuery);
$("limitInput").addEventListener("keydown", (e) => { if (e.key === "Enter") runQuery(); });

boot();
