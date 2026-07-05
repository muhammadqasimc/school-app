// Management Reports — shared JS utilities
// Extracted from inline script tags in management templates

/**
 * Build URLSearchParams from filter select elements.
 * @param {string[]} keys - Filter key names (e.g. ["year","term","grade","phase","subject"])
 * @returns {URLSearchParams}
 */
function mgtParams(keys) {
  const p = new URLSearchParams();
  keys.forEach(k => {
    const v = document.getElementById(`f-${k}`).value.trim();
    if (v) p.set(k, v);
  });
  return p;
}

/**
 * Refill a <select> with option values, preserving current selection if possible.
 * @param {string} id - Element ID
 * @param {string[]} values - Option values to populate
 */
function mgtFillSelect(id, values) {
  const el = document.getElementById(id);
  const keep = el.value;
  while (el.options.length > 1) el.remove(1);
  (values || []).forEach(v => {
    const o = document.createElement("option");
    o.value = String(v);
    o.textContent = String(v);
    el.appendChild(o);
  });
  el.value = keep;
}

/**
 * Load management report filters from API and populate filter selects.
 * @param {string[]} keys - Filter key names
 * @param {object} [opts] - Optional overrides
 * @param {string[]} [opts.skip] - Keys to skip
 */
async function mgtLoadFilters(keys, opts) {
  const p = mgtParams(keys);
  const r = await fetch(`/api/management-report-filters?${p.toString()}`);
  const d = await r.json();
  if (!d.filters) return;
  const skip = (opts && opts.skip) || [];
  if (!skip.includes("year") && d.filters.years) mgtFillSelect("f-year", d.filters.years);
  if (!skip.includes("term") && d.filters.terms) mgtFillSelect("f-term", d.filters.terms);
  if (!skip.includes("phase") && d.filters.phases) mgtFillSelect("f-phase", d.filters.phases);
  if (!skip.includes("grade") && d.filters.grades) mgtFillSelect("f-grade", d.filters.grades);
  if (!skip.includes("subject") && d.filters.subjects) mgtFillSelect("f-subject", d.filters.subjects);
}

/**
 * Render a Chart.js chart on a canvas element.
 * @param {string} canvasId - Canvas element ID
 * @param {string} type - Chart type (bar, line, doughnut, pie)
 * @param {string} label - Dataset label
 * @param {object[]} rows - Data rows with label and value properties
 * @param {string} color - Background/border color
 * @param {string[]} [palette] - Color palette for doughnut/pie charts
 * @returns {Chart}
 */
function mgtChart(canvasId, type, label, rows, color, palette) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  const labels = (rows || []).map(r => r.label);
  const values = (rows || []).map(r => Number(r.value || 0));
  const isDonutOrPie = type === "doughnut" || type === "pie";
  const bgColor = isDonutOrPie
    ? (palette || ["#0d6efd","#6610f2","#d63384","#fd7e14","#ffc107","#198754","#20c997","#0dcaf0"]).slice(0, (rows || []).length)
    : color;
  const bdColor = bgColor;
  return new Chart(ctx, {
    type,
    data: { labels, datasets: [{ label, data: values, backgroundColor: bgColor, borderColor: bdColor, borderWidth: 1 }] },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

/**
 * Update KPI element inner text.
 * @param {string} id - Element ID
 * @param {*} value - Value to display
 * @param {string} [suffix] - Optional suffix (e.g. "%")
 */
function mgtKpi(id, value, suffix) {
  document.getElementById(id).textContent = value != null ? `${value}${suffix || ""}` : "-";
}

/**
 * Render table body rows.
 * @param {string} tbodyId - Table body element ID
 * @param {object[]} rows - Data rows
 * @param {function} mapFn - Maps row to <tr> string
 * @param {string} [emptyMsg] - Message when no rows
 */
function mgtTable(tbodyId, rows, mapFn, emptyMsg) {
  const body = document.getElementById(tbodyId);
  if (!rows || !rows.length) {
    body.innerHTML = `<tr><td colspan="3" class="text-muted">${emptyMsg || "No data."}</td></tr>`;
    return;
  }
  body.innerHTML = rows.slice(0, 30).map(mapFn).join("");
}

/**
 * Bind filter change events to trigger filter reload.
 * @param {string[]} ids - Element IDs
 * @param {Function} handler - Event handler
 */
function mgtBindFilters(ids, handler) {
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", handler);
  });
}

const MGT_DEFAULT_PALETTE = ["#0d6efd","#6610f2","#d63384","#fd7e14","#ffc107","#198754","#20c997","#0dcaf0"];