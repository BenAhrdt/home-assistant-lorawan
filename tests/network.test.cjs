/* Run with node tests/network.test.cjs; also runnable in a plain JS isolate. */
function runNetworkTests(Network, Panel) {
  let checks = 0;
  const assert = (condition, message) => { checks++; if (!condition) throw new Error(message); };
  const connection = (entry_id) => ({ entry_id, name: entry_id, color: "rgb(20, 100, 200)", connected: true });
  const device = (entry_id, name, app = "app") => ({ entry_id, name, dev_eui: name, application_id: app, application_name: app, last_uplink: { received_at: "2026-11-01T10:00:00Z", spreading_factor: 7, gateways: [{ gateway_id: "one", rssi: 0, snr: 0 }, { gateway_id: "two", rssi: -100, snr: -5 }] } });
  const graph = Object.create(Network.prototype);
  graph._data = { devices: [device("a", "same"), device("a", "other", "other-app"), device("b", "same")], connections: [connection("a"), connection("b")], hass: { language: "de" } };
  graph._state = { positions: {}, expanded: {}, view: null, filter: "", search: "" };
  graph._buildGraph();
  assert(graph._nodes.filter((n) => n.type === "gateway").length === 4, "Gateways scoped by LNS and shared by applications");
  assert(graph._edges.filter((edge) => edge.kind === "radio").length === 6, "All gateway receptions shown");
  assert(new Set(graph._nodes.map((n) => n.key)).size === graph._nodes.length, "Identical EUIs separated across LNS");
  const key = graph._nodes.find((n) => n.type === "device").key;
  graph._state.positions[key] = { x: 123, y: 456 }; graph._buildGraph();
  assert(graph._nodeMap.get(key).x === 123 && graph._nodeMap.get(key).y === 456, "Custom positions survive updates");
  graph._state.filter = "b"; graph._buildGraph();
  assert(graph._groups.length === 1 && graph._nodes.length === 5, "LNS filtering");
  graph._state.filter = ""; graph._state.search = "other-app"; graph._buildGraph();
  assert(graph._nodes.filter((n) => n.type === "device").length === 1, "Application search");
  graph._state.search = "two"; graph._buildGraph();
  assert(graph._edges.filter((edge) => edge.kind === "radio").length === 6, "Gateway search");
  graph._state.search = "missing"; graph._buildGraph();
  assert(graph._nodes.length === 0, "Empty search results");
  graph._state.search = "";
  graph._data.devices = Array.from({ length: 12 }, (_, i) => device("a", `sensor-${i}`));
  graph._buildGraph();
  assert(graph._nodes.filter((n) => n.type === "device").length === 12, "All devices visible by default, including large applications");
  assert(graph._edges.filter((edge) => edge.kind === "radio").length === 24, "All device reception edges retained");
  assert(graph._nodes.filter((n) => n.type === "lns").length === 1 && graph._nodes.filter((n) => n.type === "application").length === 1, "LNS and application are real map nodes");
  graph._data.devices = [{ ...device("a", "no-gateway"), last_uplink: null }]; graph._buildGraph();
  assert(graph._nodes.filter((n) => n.type === "device").length === 1 && graph._edges.every((edge) => edge.kind !== "radio"), "Missing metadata keeps device visible without invented radio link");
  const metrics = Object.create(Network.prototype);
  Object.assign(metrics, {
    clientWidth: 1600, _svg: { clientWidth: 1600, clientHeight: 700 },
    _state: { positions: {}, view: null, filter: "", search: "" },
    _data: { hass: { language: "de" }, connections: [connection("a"), connection("b")], devices: [
      ...Array.from({ length: 32 }, (_, i) => device("a", `Raum Temperatur ${i}`, `app-${Math.floor(i / 5)}`)),
      device("b", "Außentemperatur", "weather"),
    ] },
    _paint() {}, _save() {},
  });
  metrics._buildGraph(); metrics._fit();
  assert(metrics._state.view.scale >= .72, "Realistic 33-device landscape layout keeps 12px labels readable instead of shrinking a vertical list");
  assert(metrics._groups[0].width / metrics._groups[0].height > 1.25, "Main LNS occupies landscape space");
  assert(new Set(metrics._nodes.filter((n) => n.type === "device").map((n) => Math.round(n.x))).size > 20, "Devices spread spatially rather than in one column");
  let labelCollisions = 0;
  for (let i = 0; i < metrics._nodes.length; i++) for (let j = i + 1; j < metrics._nodes.length; j++) {
    const a = metrics._nodes[i], b = metrics._nodes[j];
    if (Math.abs(a.x - b.x) < 130 && Math.abs((a.y + a.radius / 2) - (b.y + b.radius / 2)) < 73) labelCollisions++;
  }
  assert(labelCollisions === 0, "Realistic landscape layout separates label areas");
  const positions = JSON.stringify(metrics._nodes.map((n) => [n.key, n.x, n.y]));
  metrics._buildGraph();
  assert(JSON.stringify(metrics._nodes.map((n) => [n.key, n.x, n.y])) === positions, "Layout deterministic across data refreshes");
  assert(metrics._nodes.every((n) => Number.isFinite(n.x) && Number.isFinite(n.y)), "All map coordinates finite");
  const markup = metrics._graphMarkup();
  assert(markup.includes('node-lns') && markup.includes('node-gateway') && !markup.includes('width="970"'), "Map uses compact node symbols and no tall grouping boxes");
  metrics._svg = { clientWidth: 400, clientHeight: 600 }; metrics.clientWidth = 400; metrics._buildGraph(); metrics._fit();
  assert(metrics._groups[1].y > metrics._groups[0].y && metrics._state.view.scale > 0, "Portrait layout stacks spatial LNS islands");
  assert(graph._receptionTable([{ gateway_id: '<script>"', rssi: 0, snr: 0 }]).includes("&lt;script&gt;&quot;"), "Reception HTML escaped");
  assert(graph._receptionTable([{ gateway_id: "g", rssi: 0, snr: 0 }]).includes("0 dBm"), "Zero reception values displayed");
  const paint = Network.prototype._paint;
  graph._paint = () => {};
  graph._state.view = { x: 10, y: 20, scale: 1 };
  graph._zoom(2, 100, 100);
  assert(graph._state.view.x === -80 && graph._state.view.y === -60 && graph._state.view.scale === 2, "Zoom preserves pointer anchor");
  graph._zoom(999, 0, 0);
  assert(graph._state.view.scale === 4, "Zoom bounded");

  const controls = new Map(["[data-fit]", "[data-reset]", "select", "input"].map((key) => [key, {}]));
  graph.shadowRoot = { querySelector: (key) => controls.get(key), querySelectorAll: () => [] };
  graph._svg = { addEventListener() {}, setPointerCapture() {}, getBoundingClientRect: () => ({ left: 0, top: 0 }) };
  graph._pointers = new Map(); graph._state.view = { x: 0, y: 0, scale: 1 }; graph._save = () => {}; graph._render = () => {};
  graph._bind();
  const pointer = (id, x, y, type = "pointerdown") => ({ pointerId: id, clientX: x, clientY: y, button: 0, type, preventDefault() {}, target: { closest: () => null } });
  graph._svg.onpointerdown(pointer(1, 100, 100)); graph._svg.onpointermove(pointer(1, 120, 130));
  assert(graph._state.view.x === 20 && graph._state.view.y === 30, "Background drag pans");
  graph._svg.onpointerup(pointer(1, 120, 130, "pointerup"));
  assert(graph._pointers.size === 0, "Pointer released");
  graph._state.view = { x: 0, y: 0, scale: 1 };
  graph._svg.onpointerdown(pointer(1, 100, 100)); graph._svg.onpointerdown(pointer(2, 200, 100));
  graph._svg.onpointermove(pointer(2, 300, 100));
  assert(graph._state.view.scale === 2 && graph._state.view.x === -100, "Pinch zoom and center movement");
  graph._svg.onpointercancel(pointer(1, 100, 100, "pointercancel")); graph._svg.onpointerup(pointer(2, 300, 100, "pointerup"));
  assert(graph._pointers.size === 0, "Pinch cancellation clears pointers");
  const node = graph._nodes[0];
  const down = pointer(3, 100, 100); down.target.closest = () => ({ dataset: { node: "0" } });
  graph._state.view = { x: 0, y: 0, scale: 2 };
  const originalX = node.x;
  graph._svg.onpointerdown(down); graph._svg.onpointermove(pointer(3, 120, 100));
  assert(node.x === originalX + 10 && graph._state.positions[node.key].x === node.x, "Node dragging accounts for zoom and persists");
  graph._svg.onpointerup(pointer(3, 120, 100, "pointerup"));
  graph._paint = paint;
  assert(typeof Panel.prototype._updateNetwork === "function" && typeof Panel.prototype._openDevice === "function", "Panel integration methods exist");
  const previousWindow = globalThis.window, previousEvent = globalThis.CustomEvent;
  try {
    let navigation, changed;
    globalThis.window = {
      location: { pathname: "/lorawan", search: "?view=network", hash: "" },
      history: { pushState: (state, _, url) => { navigation = { state, url }; } },
      dispatchEvent: (event) => { changed = event; },
    };
    globalThis.CustomEvent = class { constructor(type, options) { this.type = type; this.detail = options.detail; } };
    Panel.prototype._openDevice.call({}, "device/id");
    assert(navigation.state.from === "/lorawan?view=network", "Device navigation preserves network return URL");
    assert(navigation.url === "/config/devices/device/device%2Fid?back=1" && changed.type === "location-changed", "HA navigation uses back support and location event");
  } finally { globalThis.window = previousWindow; globalThis.CustomEvent = previousEvent; }
  const previousStorage = globalThis.localStorage;
  try {
    let requestedKey;
    globalThis.localStorage = { getItem(key) { requestedKey = key; return null; } };
    const preferences = Object.create(Network.prototype);
    Object.assign(preferences, { _state: { positions: {}, view: null, filter: "", search: "" }, _pointers: new Map(), _selected: null, _render() {} });
    preferences.data = { hass: { user: { id: "test-user" } }, devices: [], connections: [] };
    assert(requestedKey === "lorawan.network.v2.test-user", "Old column-layout viewport is not restored");
    assert(preferences._state.view === null, "New layout starts with automatic fit");
  } finally { globalThis.localStorage = previousStorage; }
  return `${checks} JavaScript checks passed`;
}

if (typeof require === "function") {
  const fs = require("node:fs");
  const root = require("node:path").join(__dirname, "../custom_components/lorawan/frontend/");
  const stub = { define() {}, get() { return false; } };
  const load = (name, className) => new Function("HTMLElement", "customElements", fs.readFileSync(root + name, "utf8").replace(/^import .*;\n/gm, "") + `;return ${className};`)(class {}, stub);
  console.log(runNetworkTests(load("network.js", "LoRaWANNetwork"), load("panel.js", "LoRaWANPanel")));
}
