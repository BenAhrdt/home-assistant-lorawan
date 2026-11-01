/* Network observations, deliberately distinct from permanent routing links. */
const LABELS = {
  de: {
    network: "Netzwerk", all: "Alle LNS", search: "Gerät, DevEUI, Applikation oder Gateway suchen",
    fit: "Alles einpassen", reset: "Layout zurücksetzen", unknown: "Unbekannte Applikation",
    devices: "Geräte", gateways: "Gateways", empty: "Keine passenden Geräte vorhanden.",
    hint: "Knoten ziehen zum Anordnen · Hintergrund ziehen zum Verschieben · Mausrad / zwei Finger zum Zoomen",
    links: "Linien zeigen Gateway-Empfänge der jeweils letzten Uplinks, keine dauerhaften Verbindungen.",
    noGateway: "Keine Gateway-Metadaten", last: "Letzter Uplink", never: "Noch kein Uplink gespeichert",
    lns: "LNS", affiliation: "Applikationszuordnung", reception: "Funkempfang", application: "Applikation", close: "Schließen", page: "HA-Geräteseite öffnen", history: "Letzte Uplinks",
    historyHint: "Maximal 20 Uplinks je Gerät, gespeichert ab dieser Version. Empfangswerte gelten je Gateway.",
    loading: "Uplinks werden geladen …", error: "Uplinks konnten nicht geladen werden.", retry: "Erneut laden",
    online: "Online", offline: "Offline", observed: "Zuletzt beobachtet", gateway: "Gateway",
    received: "Empfangen", frequency: "Frequenz", count: "Frame Counter", port: "Port",
    details: "Empfang und Nutzdaten", data: "Dekodierte Werte", mqtt: "MQTT verbunden", disconnected: "MQTT getrennt",
  },
  en: {
    network: "Network", all: "All LNS", search: "Search device, DevEUI, application or gateway",
    fit: "Fit all", reset: "Reset layout", unknown: "Unknown application", devices: "Devices", gateways: "Gateways",
    empty: "No matching devices.", hint: "Drag nodes to arrange · Drag background to pan · Wheel / pinch to zoom",
    links: "Lines show gateway receptions of the latest uplinks, not permanent connections.", noGateway: "No gateway metadata",
    last: "Last uplink", never: "No uplink saved yet", lns: "LNS", affiliation: "Application membership", reception: "Radio reception", application: "Application", close: "Close", page: "Open HA device page",
    history: "Recent uplinks", historyHint: "Up to 20 uplinks per device, recorded from this version. Reception values belong to each gateway.",
    loading: "Loading uplinks …", error: "Could not load uplinks.", retry: "Retry", online: "Online", offline: "Offline",
    observed: "Last observed", gateway: "Gateway", received: "Received", frequency: "Frequency", count: "Frame counter",
    port: "Port", details: "Reception and payload", data: "Decoded values", mqtt: "MQTT connected", disconnected: "MQTT disconnected",
  },
};
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const keyFor = (...parts) => JSON.stringify(parts);
const safeColor = (color) => /^#[\da-f]{3,8}$/i.test(color || "") || /^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$/.test(color || "") ? color : "var(--primary-color, #03a9f4)";

class LoRaWANNetwork extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = { devices: [], connections: [] };
    this._state = { positions: {}, view: null, filter: "", search: "" };
    this._pointers = new Map();
    this._selected = null;
  }

  set data(data) {
    this._data = data;
    const storageKey = `lorawan.network.v2.${data.hass?.user?.id || "local"}`;
    if (storageKey !== this._storageKey) {
      this._storageKey = storageKey;
      try {
        const saved = JSON.parse(localStorage.getItem(storageKey));
        if (saved && typeof saved.positions === "object" && saved.positions !== null) {
          this._state.positions = Object.fromEntries(Object.entries(saved.positions).filter(([, p]) => Number.isFinite(p?.x) && Number.isFinite(p?.y)));
          if ([saved.view?.x, saved.view?.y, saved.view?.scale].every(Number.isFinite) && saved.view.scale >= 0.02 && saved.view.scale <= 4) this._state.view = saved.view;
          this._state.filter = typeof saved.filter === "string" ? saved.filter : "";
          this._state.search = typeof saved.search === "string" ? saved.search : "";
        }
      } catch (_) { /* Storage is optional. */ }
    }
    if (!this._pointers.size && !this._selected) this._render();
  }

  get _lang() { return String(this._data.hass?.locale?.language || this._data.hass?.language || navigator.language).startsWith("de") ? "de" : "en"; }
  _t(key) { return LABELS[this._lang][key] || key; }
  _save() { try { localStorage.setItem(this._storageKey, JSON.stringify(this._state)); } catch (_) { /* Session state remains usable. */ } }
  _date(value) { const date = new Date(value); return value && !Number.isNaN(date.valueOf()) ? date.toLocaleString(this._lang) : "—"; }
  connectedCallback() {
    this._resizeObserver = new ResizeObserver(() => {
      if (!this._state.view && this._nodes?.length) this._fit();
    });
    this._resizeObserver.observe(this);
  }
  disconnectedCallback() { this._resizeObserver?.disconnect(); }

  _canvasSize() {
    return {
      width: this._svg?.clientWidth || this.clientWidth || 1200,
      height: this._svg?.clientHeight || Math.max(440, Math.min(850, (typeof window === "undefined" ? 1000 : window.innerHeight) * .7)),
    };
  }

  _buildGraph() {
    const { devices, connections } = this._data;
    const search = this._state.search.toLocaleLowerCase();
    this._nodes = [];
    this._edges = [];
    this._groups = [];
    for (const connection of connections) {
      if (this._state.filter && connection.entry_id !== this._state.filter) continue;
      const selected = devices.filter((device) => device.entry_id === connection.entry_id && [device.name, device.dev_eui, device.application_name, ...(device.last_uplink?.gateways || []).map((g) => g.gateway_id)].some((v) => String(v || "").toLocaleLowerCase().includes(search)));
      if (!selected.length) continue;
      selected.sort((a, b) => `${a.application_name} ${a.name} ${a.dev_eui}`.localeCompare(`${b.application_name} ${b.name} ${b.dev_eui}`));
      const color = safeColor(connection.color);
      const lns = { key: keyFor("lns", connection.entry_id), type: "lns", label: connection.name, connection, entryId: connection.entry_id, color, radius: 25, x: 0, y: 0 };
      const nodes = [lns], apps = new Map(), gateways = new Map();
      for (const device of selected) {
        const appKey = keyFor("application", connection.entry_id, device.application_id || device.application_name || "unknown");
        if (!apps.has(appKey)) {
          const app = { key: appKey, type: "application", label: device.application_name || this._t("unknown"), entryId: connection.entry_id, color, radius: 21, devices: [] };
          apps.set(appKey, app); nodes.push(app);
          this._edges.push({ source: lns.key, target: appKey, kind: "affiliation", color });
        }
        const node = { key: keyFor("device", connection.entry_id, device.dev_eui), type: "device", label: device.name, color, radius: 17, device, appKey };
        apps.get(appKey).devices.push(node); nodes.push(node);
        this._edges.push({ source: appKey, target: node.key, kind: "affiliation", color });
        for (const reception of device.last_uplink?.gateways || []) {
          if (!reception.gateway_id) continue;
          const gatewayKey = keyFor("gateway", connection.entry_id, reception.gateway_id);
          if (!gateways.has(gatewayKey)) {
            const gateway = { key: gatewayKey, type: "gateway", label: reception.gateway_id, color, radius: 23, observed: device.last_uplink.received_at };
            gateways.set(gatewayKey, gateway); nodes.push(gateway);
            this._edges.push({ source: lns.key, target: gatewayKey, kind: "infrastructure", color });
          }
          const gateway = gateways.get(gatewayKey);
          if (Date.parse(device.last_uplink.received_at) > Date.parse(gateway.observed)) gateway.observed = device.last_uplink.received_at;
          this._edges.push({ source: gatewayKey, target: node.key, kind: "radio", color, reception });
        }
      }
      // Seed application sectors on an ellipse, then resolve label collisions.
      // The aspect ratio follows the canvas, not a fixed vertical hierarchy.
      const viewport = this._canvasSize();
      const aspect = Math.max(.8, Math.min(2.1, viewport.width / viewport.height));
      const area = Math.max(6, nodes.length) * 10500;
      const rx = Math.max(180, Math.sqrt(area * aspect) / 2);
      const ry = Math.max(150, Math.sqrt(area / aspect) / 2);
      let ordinal = 0;
      for (const app of apps.values()) {
        const middle = (ordinal + (app.devices.length - 1) / 2 + .5) / selected.length * Math.PI * 2 - Math.PI / 2;
        app.x = Math.cos(middle) * rx * .49;
        app.y = Math.sin(middle) * ry * .49;
        for (const node of app.devices) {
          const angle = (ordinal + .5) / selected.length * Math.PI * 2 - Math.PI / 2;
          const ring = selected.length > 22 ? (ordinal % 2 ? 1.12 : .84) : 1;
          node.x = Math.cos(angle) * rx * ring;
          node.y = Math.sin(angle) * ry * ring;
          ordinal++;
        }
      }
      [...gateways.values()].forEach((gateway, i) => {
        const angle = i / gateways.size * Math.PI * 2 + Math.PI * .75;
        gateway.x = Math.cos(angle) * Math.max(100, rx * .23);
        gateway.y = Math.sin(angle) * Math.max(85, ry * .23);
      });
      this._relax(nodes, lns);
      const minX = Math.min(...nodes.map((n) => n.x - 84));
      const maxX = Math.max(...nodes.map((n) => n.x + 84));
      const minY = Math.min(...nodes.map((n) => n.y - n.radius - 8));
      const maxY = Math.max(...nodes.map((n) => n.y + n.radius + 49));
      this._groups.push({ connection, nodes, width: maxX - minX, height: maxY - minY, minX, minY, count: selected.length, gatewayCount: gateways.size });
    }
    // Pack LNS islands horizontally on desktop, vertically on narrow screens.
    const viewport = this._canvasSize();
    const horizontal = viewport.width >= viewport.height * 1.15;
    let offset = 0;
    const cross = Math.max(0, ...this._groups.map((g) => horizontal ? g.height : g.width));
    for (const group of this._groups) {
      group.x = horizontal ? offset : (cross - group.width) / 2;
      group.y = horizontal ? (cross - group.height) / 2 : offset;
      for (const node of group.nodes) {
        node.x += group.x - group.minX;
        node.y += group.y - group.minY;
        Object.assign(node, this._state.positions[node.key] || {});
        this._nodes.push(node);
      }
      offset += (horizontal ? group.width : group.height) + 70;
    }
    this._nodeMap = new Map(this._nodes.map((node) => [node.key, node]));
  }

  _relax(nodes, root) {
    // Deterministic label-aware separation, no running physics or jumping nodes.
    const anchors = nodes.map((node) => ({ x: node.x, y: node.y }));
    for (let step = 0; step < 180; step++) {
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        if (a !== root) { a.x += (anchors[i].x - a.x) * .012; a.y += (anchors[i].y - a.y) * .012; }
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dx = b.x - a.x, dy = (b.y + b.radius / 2) - (a.y + a.radius / 2);
          const overlapX = 153 - Math.abs(dx), overlapY = 91 - Math.abs(dy);
          if (overlapX <= 0 || overlapY <= 0) continue;
          if (overlapX < overlapY * 1.6) {
            const shift = Math.sign(dx || (j % 2 ? 1 : -1)) * overlapX * .28;
            a.x -= shift; b.x += shift;
          } else {
            const shift = Math.sign(dy || 1) * overlapY * .28;
            a.y -= shift; b.y += shift;
          }
        }
      }
    }
  }

  _icon(node) {
    if (node.type === "lns") return '<rect x="-11" y="-13" width="22" height="10" rx="3"/><rect x="-11" y="3" width="22" height="10" rx="3"/><path d="M-6-8h1M-6 8h1M0-8h6M0 8h6"/>';
    if (node.type === "application") return '<rect x="-10" y="-10" width="8" height="8" rx="2"/><rect x="2" y="-10" width="8" height="8" rx="2"/><rect x="-10" y="2" width="8" height="8" rx="2"/><rect x="2" y="2" width="8" height="8" rx="2"/>';
    if (node.type === "gateway") return '<path d="M0-4v17M-7 13h14M-10-11a14 14 0 0 1 20 0M-7-7a9 9 0 0 1 14 0M-3-3a4 4 0 0 1 6 0"/>';
    const name = `${node.label} ${node.device?.model || ""}`.toLowerCase();
    if (/temper|therm|heiz|vicki/.test(name)) return '<path d="M-3 3v-12a3 3 0 0 1 6 0V3a6 6 0 1 1-6 0Z"/><path d="M0-6V7"/>';
    if (/fenster|door|tür|kontakt/.test(name)) return '<rect x="-8" y="-12" width="13" height="24" rx="2"/><path d="M1 0h1M9-8v16"/>';
    if (/strom|energie|power|steck/.test(name)) return '<path d="m2-13-10 15h7l-1 11L9-3H2Z"/>';
    if (/wasser|feucht|regen|pool/.test(name)) return '<path d="M0-13C-4-6-9-1-9 4a9 9 0 0 0 18 0C9-1 4-6 0-13Z"/><path d="M-5 4a5 5 0 0 0 5 5"/>';
    return '<rect x="-9" y="-12" width="18" height="24" rx="5"/><path d="M-4-5h8M-4 0h8"/><circle cx="0" cy="7" r="1"/>';
  }

  _nodeMarkup(node, index) {
    const e = escapeHtml;
    const words = node.label.match(/.{1,23}(?:\s|$)|.{1,23}/g) || [node.label];
    const lines = words.slice(0, 2).map((line) => line.trim());
    if (words.length > 2) lines[1] = `${lines[1].slice(0, 21)}…`;
    const labelY = node.radius + 19;
    const type = node.type === "device" ? "" : this._t(node.type);
    const fill = node.type === "lns" ? node.color : "var(--card-background-color,#fff)";
    const shape = node.type === "gateway"
      ? `<rect class="body" x="-18" y="-18" width="36" height="36" rx="9" transform="rotate(45)" fill="${fill}" stroke="${node.color}"/>`
      : node.type === "lns"
        ? `<rect class="body" x="-25" y="-25" width="50" height="50" rx="16" fill="${fill}" stroke="${node.color}"/>`
        : `<circle class="body" r="${node.radius}" fill="${fill}" stroke="${node.color}"/>`;
    return `<g class="node node-${node.type}" data-node="${index}" tabindex="0" role="button" aria-label="${e(node.label)}" transform="translate(${node.x} ${node.y})">
      <title>${e(node.label)}${type ? ` · ${type}` : ""}</title>
      <circle r="${node.radius + 7}" fill="${node.color}" fill-opacity=".07"/>
      ${shape}<g fill="none" stroke="${node.type === "lns" ? "#fff" : node.color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" transform="scale(${node.type === "device" ? .75 : .85})">${this._icon(node)}</g>
      ${node.type === "device" ? `<circle cx="${node.radius - 1}" cy="${-node.radius + 2}" r="4" fill="${node.device.online ? "var(--success-color,#43a047)" : "var(--disabled-text-color,#999)"}" stroke="var(--card-background-color,#fff)" stroke-width="2"/>` : ""}
      <rect class="label-bg" x="-78" y="${labelY - 12}" width="156" height="${lines.length * 15 + (type ? 14 : 0) + 3}" rx="5"/>
      ${lines.map((line, i) => `<text class="node-label" text-anchor="middle" y="${labelY + i * 15}">${e(line)}</text>`).join("")}
      ${type ? `<text class="node-caption" text-anchor="middle" y="${labelY + lines.length * 15 - 1}">${e(type)}${node.type === "application" ? ` · ${node.devices.length}` : ""}</text>` : ""}
    </g>`;
  }

  _graphMarkup() {
    return `${this._edges.map((edge, i) => `<path class="edge edge-${edge.kind}" data-edge="${i}" stroke="${edge.color}"><title>${edge.kind === "radio" ? `${escapeHtml(edge.reception.gateway_id)} · RSSI ${escapeHtml(edge.reception.rssi ?? "—")} dBm · SNR ${escapeHtml(edge.reception.snr ?? "—")} dB` : edge.kind === "infrastructure" ? "LNS / Gateway" : this._t("affiliation")}</title></path>`).join("")}${this._nodes.map((node, i) => this._nodeMarkup(node, i)).join("")}`;
  }

  _render() {
    if (!this.isConnected) return;
    const focused = this.shadowRoot.activeElement;
    const focusState = focused?.matches?.("input[type=search]")
      ? { search: true, start: focused.selectionStart, end: focused.selectionEnd }
      : focused?.dataset?.node !== undefined
        ? { key: this._nodes?.[Number(focused.dataset.node)]?.key }
        : null;
    this._buildGraph();
    const e = escapeHtml;
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;color:var(--primary-text-color);font:inherit}*{box-sizing:border-box}
        .toolbar{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}.toolbar input{flex:1;min-width:200px}
        button,input,select{font:inherit;color:inherit;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd);border-radius:10px;padding:10px 12px;min-height:42px}
        button{cursor:pointer}button:hover{background:var(--secondary-background-color,#eee)}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--primary-color)}
        .canvas{position:relative;border:1px solid var(--divider-color,#ddd);border-radius:18px;overflow:hidden;background:var(--card-background-color,#fff)}
        svg{display:block;width:100%;height:clamp(440px,70vh,850px);touch-action:none;user-select:none;cursor:grab}
        svg:active{cursor:grabbing}.node{cursor:grab;outline:none}.node:focus .body{stroke:var(--primary-color);stroke-width:3}.node text{pointer-events:none}
        .body{stroke-width:1.8;filter:drop-shadow(0 2px 3px #0000000d)}.node:hover .body,.node:focus .body{stroke-width:3}
        .label-bg{fill:var(--card-background-color,#fff);fill-opacity:.94}.node-label{fill:var(--primary-text-color,#222);font-size:12px;font-weight:500;font-family:inherit}.node-lns .node-label,.node-application .node-label{font-weight:650}.node-caption{fill:var(--secondary-text-color,#777);font-size:10px;font-family:inherit}
        .edge{fill:none;vector-effect:non-scaling-stroke;stroke-width:1.5;opacity:.4}.edge-affiliation{stroke-dasharray:3 5;stroke-width:1;opacity:.18}.edge-infrastructure{stroke-dasharray:5 5;opacity:.25}.node:hover{cursor:pointer}
        .legend{display:flex;flex-wrap:wrap;align-items:center;gap:14px;padding:12px 16px;border-top:1px solid var(--divider-color,#eee);font-size:12px;color:var(--secondary-text-color)}.legend span{display:inline-flex;align-items:center;gap:7px}.legend i{display:inline-block;width:10px;height:10px;border:2px solid var(--primary-color);border-radius:50%}.legend .gateway{border-radius:3px;transform:rotate(45deg)}.legend .lns{border-radius:3px;background:var(--primary-color)}.legend .radio{width:24px;height:0;border:0;border-top:2px solid var(--primary-color);border-radius:0}.legend .affiliation{width:24px;height:0;border:0;border-top:1px dashed var(--secondary-text-color);border-radius:0}
        .lns-keys{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}.lns-key{display:inline-flex;align-items:center;gap:8px;font-size:12px;padding:6px 10px;min-height:32px;border-radius:20px}.lns-key b{width:9px;height:9px;border-radius:50%;display:inline-block}.lns-key small{color:var(--secondary-text-color)}
        .hint{font-size:12px;color:var(--secondary-text-color);line-height:1.7;margin:10px 2px}.empty{position:absolute;inset:45% 12px auto;text-align:center}
        dialog{color:inherit;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd);border-radius:20px;width:min(760px,calc(100vw - 28px));max-height:85vh;padding:24px;overflow:auto;box-shadow:0 20px 90px #0005}
        dialog::backdrop{background:#0006}h2{margin:0 0 8px}h3{margin:22px 0 10px;font-size:16px}.muted{color:var(--secondary-text-color);font-size:13px;overflow-wrap:anywhere}.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}.metric{padding:12px;border-radius:12px;background:var(--secondary-background-color,#f5f5f5)}.metric strong{display:block;margin-top:6px;overflow-wrap:anywhere}
        .table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--divider-color,#ddd);overflow-wrap:anywhere}summary{cursor:pointer;padding:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}footer{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;margin-top:20px}.primary{background:var(--primary-color);color:var(--text-primary-color,#fff)}.status{font-size:13px}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}.history-item{border-bottom:1px solid var(--divider-color,#ddd)}
        @media(max-width:600px){.toolbar select{flex:1}.toolbar button{flex:1}dialog{padding:18px}}
      </style>
      <div class="toolbar">
        <select aria-label="LNS"><option value="">${this._t("all")}</option>${this._data.connections.map((c) => `<option value="${e(c.entry_id)}" ${c.entry_id === this._state.filter ? "selected" : ""}>${e(c.name)}</option>`).join("")}</select>
        <input type="search" aria-label="${this._t("search")}" placeholder="${this._t("search")}" value="${e(this._state.search)}">
        <button data-fit>${this._t("fit")}</button><button data-reset>${this._t("reset")}</button>
      </div>
      <div class="lns-keys">${this._groups.map((group) => `<button class="lns-key" data-lns="${escapeHtml(group.connection.entry_id)}"><b style="background:${safeColor(group.connection.color)}"></b>${escapeHtml(group.connection.name)}<small>${group.count} ${this._t("devices")} · ${group.gatewayCount} ${this._t("gateways")}</small></button>`).join("")}</div>
      <div class="canvas"><svg role="group" aria-label="${this._t("network")}"><g class="world">${this._graphMarkup()}</g></svg>${!this._nodes.length ? `<div class="empty">${e(this._data.error || this._t("empty"))}</div>` : ""}
      <div class="legend"><span><i class="lns"></i>LNS</span><span><i></i>${this._t("application")}</span><span><i class="gateway"></i>${this._t("gateway")}</span><span><i></i>${this._t("devices")}</span><span><i class="radio"></i>${this._t("reception")}</span><span><i class="affiliation"></i>${this._t("affiliation")}</span></div></div>
      <p class="hint">${this._t("hint")}<br>${this._t("links")}</p><dialog aria-label="${this._t("details")}"></dialog>`;
    this._svg = this.shadowRoot.querySelector("svg");
    this._world = this.shadowRoot.querySelector(".world");
    this._paint();
    if (!this._state.view && this._nodes.length) this._fit();
    this._bind();
    if (focusState?.search) {
      const input = this.shadowRoot.querySelector("input");
      input.focus({ preventScroll: true }); input.setSelectionRange(focusState.start, focusState.end);
    } else if (focusState?.key) {
      const index = this._nodes.findIndex((node) => node.key === focusState.key);
      this.shadowRoot.querySelector(`[data-node="${index}"]`)?.focus({ preventScroll: true });
    }
  }

  _paint() {
    const view = this._state.view || { x: 0, y: 0, scale: 1 };
    this._world?.setAttribute("transform", `translate(${view.x} ${view.y}) scale(${view.scale})`);
    this.shadowRoot.querySelectorAll("[data-node]").forEach((element) => {
      const node = this._nodes[Number(element.dataset.node)];
      element.setAttribute("transform", `translate(${node.x} ${node.y})`);
    });
    this.shadowRoot.querySelectorAll("[data-edge]").forEach((element) => {
      const edge = this._edges[Number(element.dataset.edge)];
      const a = this._nodeMap.get(edge.source), b = this._nodeMap.get(edge.target);
      element.setAttribute("d", this._edgePath(a, b));
    });
  }

  _edgePath(a, b) {
    const dx = b.x - a.x, dy = b.y - a.y, distance = Math.hypot(dx, dy) || 1;
    const start = a.radius + 3, end = b.radius + 3;
    return `M${a.x + dx / distance * start},${a.y + dy / distance * start} L${b.x - dx / distance * end},${b.y - dy / distance * end}`;
  }

  _fit() {
    if (!this._svg || !this._nodes.length) return;
    const minX = Math.min(...this._nodes.map((n) => n.x - 85));
    const minY = Math.min(...this._nodes.map((n) => n.y - n.radius - 10));
    const maxX = Math.max(...this._nodes.map((n) => n.x + 85));
    const maxY = Math.max(...this._nodes.map((n) => n.y + n.radius + 55));
    const { width, height } = this._canvasSize();
    const scale = Math.max(.02, Math.min(1.25, (width - 44) / (maxX - minX), (height - 40) / (maxY - minY)));
    this._state.view = { x: (width - (maxX - minX) * scale) / 2 - minX * scale, y: (height - (maxY - minY) * scale) / 2 - minY * scale, scale };
    this._paint(); this._save();
  }

  _zoom(factor, x, y, origin = this._state.view || { x: 0, y: 0, scale: 1 }) {
    const scale = Math.min(4, Math.max(.02, origin.scale * factor));
    const ratio = scale / origin.scale;
    this._state.view = { x: x - (x - origin.x) * ratio, y: y - (y - origin.y) * ratio, scale };
    this._paint();
  }

  _bind() {
    this.shadowRoot.querySelectorAll("[data-lns]").forEach((button) => {
      button.onclick = () => {
        this._state.filter = this._state.filter === button.dataset.lns ? "" : button.dataset.lns;
        this._state.view = null; this._save(); this._render();
      };
    });
    this.shadowRoot.querySelector("[data-fit]").onclick = () => this._fit();
    this.shadowRoot.querySelector("[data-reset]").onclick = () => { this._state.positions = {}; this._state.view = null; this._save(); this._render(); };
    this.shadowRoot.querySelector("select").onchange = (event) => { this._state.filter = event.target.value; this._state.view = null; this._save(); this._render(); };
    this.shadowRoot.querySelector("input").oninput = (event) => {
      const start = event.target.selectionStart;
      this._state.search = event.target.value; this._state.view = null; this._save(); this._render();
      const input = this.shadowRoot.querySelector("input"); input.focus(); input.setSelectionRange(start, start);
    };
    this.shadowRoot.querySelectorAll("[data-node]").forEach((element) => {
      const highlight = (active) => {
        const node = this._nodes[Number(element.dataset.node)];
        this.shadowRoot.querySelectorAll("[data-edge]").forEach((path) => {
          const edge = this._edges[Number(path.dataset.edge)];
          const selected = edge.source === node.key || edge.target === node.key;
          path.style.opacity = active ? (selected ? ".95" : ".045") : "";
          path.style.strokeWidth = active && selected ? "2.5" : "";
        });
      };
      element.onpointerenter = () => highlight(true);
      element.onpointerleave = () => highlight(false);
      element.onfocus = () => highlight(true);
      element.onblur = () => highlight(false);
      element.onkeydown = (event) => { if (["Enter", " "].includes(event.key)) { event.preventDefault(); this._open(this._nodes[Number(element.dataset.node)]); } };
    });
    this._svg.addEventListener("wheel", (event) => {
      event.preventDefault(); const rect = this._svg.getBoundingClientRect();
      this._zoom(Math.exp(-event.deltaY * .0015), event.clientX - rect.left, event.clientY - rect.top); this._save();
    }, { passive: false });
    this._svg.onpointerdown = (event) => {
      if (event.button !== 0 || this._pointers.size >= 2) return;
      event.preventDefault(); this._svg.setPointerCapture(event.pointerId);
      const rect = this._svg.getBoundingClientRect();
      const point = { x: event.clientX - rect.left, y: event.clientY - rect.top };
      this._pointers.set(event.pointerId, point);
      const index = event.target.closest("[data-node]")?.dataset.node;
      const node = index === undefined ? null : this._nodes[Number(index)];
      this._gesture = { point, view: { ...(this._state.view || { x: 0, y: 0, scale: 1 }) }, node, position: node ? { x: node.x, y: node.y } : null, moved: false };
      if (this._pointers.size === 2) {
        const [a, b] = [...this._pointers.values()];
        this._gesture.node = null;
        this._gesture.moved = true;
        this._gesture.distance = Math.hypot(a.x - b.x, a.y - b.y) || 1;
        this._gesture.point = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      }
    };
    this._svg.onpointermove = (event) => {
      if (!this._pointers.has(event.pointerId) || !this._gesture) return;
      const rect = this._svg.getBoundingClientRect(), g = this._gesture;
      const point = { x: event.clientX - rect.left, y: event.clientY - rect.top };
      this._pointers.set(event.pointerId, point);
      if (this._pointers.size === 2) {
        const [a, b] = [...this._pointers.values()];
        const center = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
        this._zoom(Math.hypot(a.x - b.x, a.y - b.y) / g.distance, g.point.x, g.point.y, g.view);
        this._state.view.x += center.x - g.point.x; this._state.view.y += center.y - g.point.y;
      } else if (this._pointers.size === 1 && !g.distance) {
        const dx = point.x - g.point.x, dy = point.y - g.point.y;
        if (Math.hypot(dx, dy) > 4) g.moved = true;
        if (!g.moved) return;
        if (g.node) {
          g.node.x = g.position.x + dx / g.view.scale; g.node.y = g.position.y + dy / g.view.scale;
          this._state.positions[g.node.key] = { x: g.node.x, y: g.node.y };
        } else this._state.view = { ...g.view, x: g.view.x + dx, y: g.view.y + dy };
      }
      this._paint();
    };
    const finish = (event) => {
      if (!this._pointers.has(event.pointerId)) return;
      this._pointers.delete(event.pointerId);
      const gesture = this._gesture;
      if (!this._pointers.size) {
        this._gesture = null; this._save();
        if (event.type === "pointerup" && gesture?.node && !gesture.moved) this._open(gesture.node);
      }
    };
    this._svg.onpointerup = finish; this._svg.onpointercancel = finish; this._svg.onlostpointercapture = finish;
  }

  _receptionTable(gateways) {
    const e = escapeHtml;
    return gateways?.length ? `<div class="table-wrap"><table><thead><tr><th>${this._t("gateway")}</th><th>RSSI</th><th>SNR</th></tr></thead><tbody>${gateways.map((g) => `<tr><td>${e(g.gateway_id || "—")}</td><td>${e(g.rssi ?? "—")} dBm</td><td>${e(g.snr ?? "—")} dB</td></tr>`).join("")}</tbody></table></div>` : `<p class="muted">${this._t("noGateway")}</p>`;
  }

  async _open(node) {
    if (node.type === "application" || node.type === "lns") {
      this._state.filter = node.entryId;
      this._state.search = node.type === "application" ? node.label : "";
      this._state.view = null;
      this._save(); this._render();
      return;
    }
    this._selected = node;
    this._returnFocusKey = node.key;
    const dialog = this.shadowRoot.querySelector("dialog"), e = escapeHtml;
    const device = node.device, uplink = device?.last_uplink;
    const metric = (label, value) => `<div class="metric"><span class="muted">${e(label)}</span><strong>${e(value ?? "—")}</strong></div>`;
    dialog.innerHTML = `<h2>${e(node.label)}</h2>${device ? `
      <div class="muted">${e(device.connection_name)} · ${e(device.application_name)} · ${e(device.dev_eui)}</div>
      <p class="status"><span class="dot" style="background:${device.online ? "var(--success-color,#43a047)" : "var(--disabled-text-color,#999)"}"></span>${this._t(device.online ? "online" : "offline")}</p>
      <div class="summary">${metric(this._t("last"), uplink ? this._date(uplink.received_at) : this._t("never"))}${metric("Spreading Factor", uplink?.spreading_factor == null ? "—" : `SF${uplink.spreading_factor}`)}${metric(this._t("frequency"), uplink?.frequency == null ? "—" : `${Number(uplink.frequency) / 1000000} MHz`)}${metric(this._t("count"), uplink?.f_cnt)}${metric(this._t("port"), uplink?.f_port)}</div>
      ${this._receptionTable(uplink?.gateways)}
      ${device.tile_values?.length ? `<h3>${this._t("data")}</h3><div class="summary">${device.tile_values.map((v) => metric(v.name, `${v.state ?? v.value ?? "—"} ${v.unit || ""}`)).join("")}</div>` : ""}
      <h3>${this._t("history")}</h3><p class="muted">${this._t("historyHint")}</p><div data-history>${this._t("loading")}</div>
      ` : `<p class="muted">${this._t("gateway")} · ${this._t("observed")}: ${this._date(node.observed)}</p><p>${this._t("links")}</p>`}
      <footer>${device?.id ? `<button class="primary" data-page>${this._t("page")}</button>` : ""}<button data-close>${this._t("close")}</button></footer>`;
    const close = () => dialog.close();
    dialog.querySelector("[data-close]").onclick = close;
    dialog.addEventListener("close", () => {
      this._selected = null; this._render();
      const index = this._nodes.findIndex((n) => n.key === this._returnFocusKey);
      this.shadowRoot.querySelector(`[data-node="${index}"]`)?.focus();
    }, { once: true });
    dialog.onclick = (event) => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) close(); } };
    dialog.querySelector("[data-page]")?.addEventListener("click", () => {
      this._save();
      dialog.close();
      this.dispatchEvent(new CustomEvent("network-open-device", { detail: { id: device.id }, bubbles: true, composed: true }));
    });
    dialog.showModal();
    if (device) await this._loadHistory(device, dialog);
  }

  async _loadHistory(device, dialog) {
    const target = dialog.querySelector("[data-history]");
    try {
      const result = await this._data.hass.callWS({ type: "lorawan/device_uplinks", entry_id: device.entry_id, dev_eui: device.dev_eui });
      if (!dialog.isConnected) return;
      target.innerHTML = result.uplinks.length ? result.uplinks.map((up) => `<details class="history-item"><summary>${escapeHtml(this._date(up.received_at))} · FCnt ${escapeHtml(up.f_cnt ?? "—")} · SF${escapeHtml(up.spreading_factor ?? "—")}</summary>${this._receptionTable(up.gateways)}<p class="muted">${this._t("port")}: ${escapeHtml(up.f_port ?? "—")} · ${this._t("frequency")}: ${up.frequency == null ? "—" : `${escapeHtml(Number(up.frequency) / 1000000)} MHz`}</p><pre>${escapeHtml(JSON.stringify(up.decoded, null, 2))}</pre></details>`).join("") : `<p class="muted">${this._t("never")}</p>`;
    } catch (_) {
      if (!dialog.isConnected) return;
      target.innerHTML = `<p>${this._t("error")}</p><button>${this._t("retry")}</button>`;
      target.querySelector("button").onclick = () => this._loadHistory(device, dialog);
    }
  }
}
if (!customElements.get("lorawan-network")) customElements.define("lorawan-network", LoRaWANNetwork);
