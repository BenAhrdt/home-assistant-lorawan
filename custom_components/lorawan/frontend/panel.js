class LoRaWANPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._activeTab = "devices";
    this._rendered = false;
    this._status = {
      configured: false,
      connected: false,
      topics: [],
      message_count: 0,
      unsupported_message_count: 0,
      lns_counts: { ttn: 0, chirpstack: 0 },
      device_count: 0,
      entity_count: 0,
      has_password: false,
    };
    this._statusTimer = undefined;
    this._deviceUnsubscribe = undefined;
    this._deviceSubscribePending = false;
    this._devices = [];
    this._deviceSettings = null;
    this._deviceDiagnostics = null;
    this._selectedMessage = null;
    this._selectedConnectionId = null;
    this._downlinks = { devices: [], profiles: [], configured_profiles: [], builtin_profile_types: [] };
    this._downlinkDevice = "";
    this._downlinkProfile = "";
    this._profileEditor = null;
    this._openParameterEditorIndex = null;
  }

  set hass(hass) {
    this._hass = hass;
    this._startStatusPolling();
    this._startDeviceSubscription();
    if (!this._rendered) {
      this._loadDownlinks();
    }
    if (!this._rendered) {
      if (this._activeTab !== "downlinks") this._render();
    }
  }

  connectedCallback() {
    this._startStatusPolling();
    this._startDeviceSubscription();
    this._render();
  }

  disconnectedCallback() {
    if (this._statusTimer) {
      clearInterval(this._statusTimer);
      this._statusTimer = undefined;
    }
    if (this._deviceUnsubscribe) {
      this._deviceUnsubscribe();
      this._deviceUnsubscribe = undefined;
    }
    this._deviceSubscribePending = false;
  }

  _setActiveTab(tab) {
    this._activeTab = tab;
    this._render();
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }
    this._rendered = true;

    const tabs = [
      ["devices", "Geraete"],
      ["lns", "LNS / MQTT"],
      ["uplinks", "Uplinks"],
      ["downlinks", "Downlinks"],
    ];

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          min-height: 100vh;
          color: var(--primary-text-color);
          background: var(--primary-background-color);
          font-family: var(--paper-font-body1_-_font-family);
        }

        .page {
          max-width: 1160px;
          margin: 0 auto;
          padding: 24px;
        }

        header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
        }

        .logo {
          width: 56px;
          height: 56px;
          border-radius: 8px;
          object-fit: cover;
        }

        h1 {
          margin: 0;
          font-size: 28px;
          font-weight: 500;
        }

        .tabs {
          display: flex;
          gap: 4px;
          border-bottom: 1px solid var(--divider-color);
          margin-bottom: 24px;
          overflow-x: auto;
        }

        button {
          border: 0;
          border-bottom: 3px solid transparent;
          padding: 14px 18px 11px;
          background: transparent;
          color: var(--secondary-text-color);
          font: inherit;
          cursor: pointer;
          white-space: nowrap;
        }

        button[aria-selected="true"] {
          border-bottom-color: var(--primary-color);
          color: var(--primary-text-color);
          font-weight: 500;
        }

        .section {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 16px;
        }

        .card {
          box-sizing: border-box;
          min-height: 152px;
          padding: 18px;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          background: var(--card-background-color);
        }

        h2 {
          margin: 0 0 16px;
          font-size: 18px;
          font-weight: 500;
        }

        dl {
          display: grid;
          grid-template-columns: max-content 1fr;
          gap: 10px 16px;
          margin: 0;
        }

        dt {
          color: var(--secondary-text-color);
        }

        dd {
          margin: 0;
          min-width: 0;
          overflow-wrap: anywhere;
        }

        code {
          font-family: var(--code-font-family, monospace);
          font-size: 0.95em;
        }

        form {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 16px;
          align-items: end;
        }

        label {
          display: grid;
          gap: 6px;
          color: var(--secondary-text-color);
        }

        input {
          box-sizing: border-box;
          width: 100%;
          min-height: 40px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          padding: 8px 10px;
          color: var(--primary-text-color);
          background: var(--card-background-color);
          font: inherit;
        }

        label.checkbox {
          display: flex;
          align-items: center;
          min-height: 40px;
        }

        input[type="checkbox"] {
          width: auto;
          min-height: auto;
          margin-right: 10px;
        }

        .actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .save {
          min-height: 40px;
          border: 0;
          border-radius: 4px;
          padding: 0 18px;
          color: var(--text-primary-color);
          background: var(--primary-color);
          font-weight: 500;
        }

        button.action {
          min-height: 38px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          padding: 0 14px;
          color: var(--primary-text-color);
          background: var(--secondary-background-color);
          font-weight: 500;
        }

        button.duplicate {
          border-color: #b58900;
          color: #6b5100;
          background: #fff3cd;
        }

        button.danger {
          border-color: #ba1a1a;
          color: #ba1a1a;
          background: #ffdad6;
        }

        .message {
          color: var(--secondary-text-color);
        }

        .status {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
        }

        .dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--disabled-text-color);
        }

        .dot.connected {
          background: var(--success-color, #0b8f47);
        }

        .dot.error {
          background: var(--error-color, #db4437);
        }

        .list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 16px;
        }

        .device-card {
          position: relative;
          box-sizing: border-box;
          min-height: 176px;
          padding: 18px;
          border: 1px solid var(--divider-color);
          border-radius: 10px;
          background: var(--card-background-color);
          cursor: pointer;
        }

        .icon-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          border: 0;
          border-radius: 50%;
          padding: 0;
          color: var(--secondary-text-color);
          background: transparent;
          font-size: 22px;
          cursor: pointer;
        }

        .icon-button:hover {
          background: var(--secondary-background-color);
        }

        .device-name {
          padding-right: 54px;
          font-weight: 500;
        }

        .device-eui {
          margin-top: 12px;
          font-size: 0.9em;
        }

        .device-status {
          position: absolute;
          top: 18px;
          right: 18px;
        }

        .device-settings {
          position: absolute;
          right: 12px;
          bottom: 12px;
        }

        .device-json {
          position: absolute;
          right: 58px;
          bottom: 12px;
          font-family: var(--code-font-family, monospace);
          font-size: 16px;
        }

        .muted {
          color: var(--secondary-text-color);
        }

        .diagnostics {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }

        .tag {
          border-radius: 12px;
          padding: 2px 8px;
          color: var(--secondary-text-color);
          background: var(--secondary-background-color);
          font-size: 12px;
        }

        .dialog-backdrop {
          position: fixed;
          z-index: 10;
          inset: 0;
          display: grid;
          place-items: center;
          padding: 20px;
          background: rgba(0, 0, 0, 0.42);
        }

        .dialog {
          box-sizing: border-box;
          width: min(480px, 100%);
          padding: 24px;
          border-radius: 12px;
          background: var(--card-background-color);
          box-shadow: var(--ha-card-box-shadow, 0 4px 18px rgba(0, 0, 0, 0.3));
        }

        .dialog form, .profile-editor {
          display: grid;
          grid-template-columns: 1fr;
        }

        .profile-editor details, .profile-list > details { padding: 12px; border: 1px solid var(--divider-color); border-radius: 8px; background: var(--card-background-color); }
        .profile-editor details > div, .profile-list details > div { margin-top: 12px; }
        .profile-list { display: grid; gap: 10px; }
        .profile-list summary, .profile-editor summary { cursor: pointer; }
        .profile-list summary strong { font-size: 1.05em; }
        .profile-content { display: grid; gap: 12px; }
        .profile-parameters { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
        .profile-parameter { padding: 10px; border-radius: 6px; background: var(--secondary-background-color); }
        .parameter-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }

        .status-card {
          cursor: pointer;
        }

        .message-list {
          display: grid;
          gap: 8px;
          max-height: 240px;
          overflow-y: auto;
        }

        .message-item {
          width: 100%;
          border: 1px solid var(--divider-color);
          border-radius: 6px;
          padding: 10px;
          color: var(--primary-text-color);
          background: var(--card-background-color);
          text-align: left;
        }

        .message-item.selected {
          border-color: var(--primary-color);
        }

        pre.payload {
          max-height: 240px;
          overflow: auto;
          padding: 12px;
          border-radius: 6px;
          background: var(--secondary-background-color);
          white-space: pre-wrap;
          overflow-wrap: anywhere;
        }

        .downlink-layout { display: grid; grid-template-columns: minmax(280px, 2fr) minmax(260px, 1fr); gap: 16px; }
        .parameter-list { display: grid; gap: 12px; }
        .parameter { display: grid; grid-template-columns: minmax(120px, 1fr) minmax(160px, 1fr); gap: 12px; align-items: end; }
        select, textarea { box-sizing: border-box; width: 100%; min-height: 40px; border: 1px solid var(--divider-color); border-radius: 4px; padding: 8px 10px; color: var(--primary-text-color); background: var(--card-background-color); font: inherit; }
        textarea { min-height: 240px; resize: vertical; font-family: var(--code-font-family, monospace); font-size: 12px; }
        .profile-actions { display: flex; gap: 8px; flex-wrap: wrap; }

        @media (max-width: 720px) {
          .list, .downlink-layout { grid-template-columns: 1fr; }
          .parameter { grid-template-columns: 1fr; }
        }
      </style>
      <div class="page">
        <header>
          <img class="logo" src="/lorawan_static/icon.svg" alt="" />
          <h1>LoRaWAN</h1>
        </header>
        <nav class="tabs" role="tablist">
          ${tabs
            .map(
              ([id, label]) => `
                <button
                  role="tab"
                  aria-selected="${this._activeTab === id}"
                  data-tab="${id}"
                >${label}</button>
              `
            )
            .join("")}
        </nav>
        ${this._renderContent()}
      </div>
      ${this._renderDeviceSettingsDialog()}
      ${this._renderDeviceDiagnosticsDialog()}
      ${this._renderMessagesDialog()}
    `;

    this.shadowRoot.querySelectorAll("button[data-tab]").forEach((button) => {
      button.addEventListener("click", () =>
        this._setActiveTab(button.getAttribute("data-tab"))
      );
    });
    this.shadowRoot
      .querySelectorAll("button[data-device-settings]")
      .forEach((button) => {
        button.addEventListener("click", () =>
          this._handleDeviceSettings(button)
        );
      });
    this.shadowRoot
      .querySelector("form[data-device-settings-form]")
      ?.addEventListener("submit", (event) => this._handleDeviceSettingsSubmit(event));
    this.shadowRoot
      .querySelector("button[data-device-settings-cancel]")
      ?.addEventListener("click", () => {
        this._deviceSettings = null;
        this._render();
      });
    this.shadowRoot.querySelector("select[data-downlink-device]")?.addEventListener("change", (event) => {
      this._downlinkDevice = event.target.value;
      const device = this._downlinks.devices.find((item) => item.dev_eui === this._downlinkDevice);
      this._downlinkProfile = device?.device_type || "";
      if (this._activeTab !== "downlinks") this._render();
    });
    this.shadowRoot.querySelector("select[data-downlink-profile]")?.addEventListener("change", (event) => {
      this._downlinkProfile = event.target.value;
      this._render();
    });
    this.shadowRoot.querySelector("button[data-profile-new]")?.addEventListener("click", () => {
      this._profileEditor = { deviceType: "Neues Profil", downlinkParameter: [] };
      this._openParameterEditorIndex = null;
      this._render();
    });
    this.shadowRoot.querySelectorAll("button[data-profile-edit-type]").forEach((button) => button.addEventListener("click", () => {
      this._downlinkProfile = button.getAttribute("data-profile-edit-type");
      this._profileEditor = this._cloneProfile(this._selectedDownlinkProfile());
      this._openParameterEditorIndex = null;
      this._render();
    }));
    this.shadowRoot.querySelectorAll("button[data-profile-duplicate-type]").forEach((button) => button.addEventListener("click", () => {
      this._duplicateProfile(this._downlinks.profiles.find((profile) => profile.deviceType === button.getAttribute("data-profile-duplicate-type")));
    }));
    this.shadowRoot.querySelectorAll("button[data-profile-delete-type]").forEach((button) => button.addEventListener("click", () => {
      this._deleteProfile(this._downlinks.profiles.find((profile) => profile.deviceType === button.getAttribute("data-profile-delete-type")));
    }));
    this.shadowRoot.querySelector("form[data-profile-editor]")?.addEventListener("submit", (event) => this._saveProfile(event));
    this.shadowRoot.querySelector("button[data-profile-cancel]")?.addEventListener("click", () => { this._profileEditor = null; this._openParameterEditorIndex = null; this._render(); });
    this.shadowRoot.querySelector("button[data-parameter-add]")?.addEventListener("click", () => {
      this._profileEditor.downlinkParameter.push({ name: "Neuer Parameter", type: "number", port: this._profileEditor.port || 1, lengthInByte: 1, multiplyfaktor: 1 }); this._render();
    });
    this.shadowRoot.querySelector("select[data-profile-send-with-uplink]")?.addEventListener("change", (event) => {
      this._profileEditor.sendWithUplink = event.target.value;
      this._render();
    });
    this.shadowRoot.querySelectorAll("select[data-parameter-type]").forEach((select) => select.addEventListener("change", (event) => {
      const index = Number(event.target.getAttribute("data-parameter-type"));
      if (this._profileEditor?.downlinkParameter[index]) {
        this._profileEditor.downlinkParameter[index].type = event.target.value;
        this._openParameterEditorIndex = index;
        this._render();
      }
    }));
    this.shadowRoot.querySelectorAll("input[data-parameter-visibility]").forEach((input) => input.addEventListener("change", (event) => {
      const [index, field] = event.target.getAttribute("data-parameter-visibility").split(":");
      const parameter = this._profileEditor?.downlinkParameter[Number(index)];
      if (parameter) {
        parameter[field] = event.target.checked;
        this._openParameterEditorIndex = Number(index);
        this._render();
      }
    }));
    this.shadowRoot.querySelectorAll("button[data-parameter-duplicate]").forEach((button) => button.addEventListener("click", () => this._duplicateParameter(Number(button.getAttribute("data-parameter-duplicate")))));
    this.shadowRoot.querySelectorAll("button[data-parameter-delete]").forEach((button) => button.addEventListener("click", () => this._deleteParameter(Number(button.getAttribute("data-parameter-delete")))));
    this.shadowRoot.querySelectorAll("button[data-device-json]").forEach((button) => {
      button.addEventListener("click", () => this._showDeviceDiagnostics(button));
    });
    this.shadowRoot
      .querySelector("button[data-device-diagnostics-close]")
      ?.addEventListener("click", () => {
        this._deviceDiagnostics = null;
        this._render();
      });
    this.shadowRoot.querySelectorAll("[data-device-open]").forEach((card) => {
      card.addEventListener("click", (event) => {
        if (event.target.closest("button")) {
          return;
        }
        window.location.href = `/config/devices/device/${card.getAttribute("data-device-open")}`;
      });
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          window.location.href = `/config/devices/device/${card.getAttribute("data-device-open")}`;
        }
      });
    });
    this.shadowRoot.querySelectorAll("[data-show-messages]").forEach((card) => {
      card.addEventListener("click", () => {
        this._selectedConnectionId = card.getAttribute("data-entry-id");
        this._selectedMessage = this._messagesForSelectedConnection()[0] || null;
        this._render();
      });
    });
    this.shadowRoot.querySelectorAll("[data-message-index]").forEach((button) => {
      button.addEventListener("click", () => {
        this._selectedMessage = this._messagesForSelectedConnection()[
          Number(button.getAttribute("data-message-index"))
        ] || null;
        this._render();
      });
    });
    this.shadowRoot
      .querySelector("button[data-messages-close]")
      ?.addEventListener("click", () => {
        this._selectedMessage = null;
        this._selectedConnectionId = null;
        this._render();
      });
  }

  _renderContent() {
    if (this._activeTab === "lns") {
      const connections = this._status.connections || [];
      return `
        <div class="section">
          ${connections.map((connection) => `
          <div class="card status-card" style="border-top: 4px solid ${this._escape(connection.color || "var(--primary-color)")}" role="button" tabindex="0" data-show-messages data-entry-id="${this._escape(connection.entry_id || "")}" title="Letzte Nachrichten anzeigen">
            <h2>${this._escape(connection.name || "LoRaWAN")}</h2>
            <dl>
              <dt>Verbindung</dt>
              <dd>
                <span class="status">
                  <span class="dot ${connection.connected ? "connected" : connection.last_error ? "error" : ""}"></span>
                  ${connection.connected ? "Aktiv" : "Nicht verbunden"}
                </span>
              </dd>
              <dt>Broker</dt>
              <dd><code>${this._escape(connection.host || "-")}:${this._escape(connection.port || "-")}</code></dd>
              <dt>Letzte Nachricht</dt>
              <dd>${this._formatDate(connection.last_message_at)}</dd>
              <dt>Letztes Topic</dt>
              <dd><code>${this._escape(connection.last_topic || "-")}</code></dd>
              <dt>Erkannt</dt>
              <dd>${this._formatDetectedNetworks(connection.lns_counts)}</dd>
              <dt>Fehler</dt>
              <dd>${this._escape(connection.last_error || "-")}</dd>
            </dl>
          </div>
          `).join("")}
          <div class="card">
            <h2>Topics</h2>
            <dl>
              ${(this._status.topics?.length
                ? this._status.topics
                : ["v3/+/devices/+/+", "application/+/device/+/event/+"]
              )
                .map(
                  (topic, index) => `
                    <dt>${index === 0 ? "TTN" : "ChirpStack"}</dt>
                    <dd><code>${this._escape(topic)}</code></dd>
                  `
                )
                .join("")}
            </dl>
          </div>
          <div class="card">
            <h2>Formate</h2>
            <dl>
              <dt>TTN</dt>
              <dd><code>uplink_message.decoded_payload</code></dd>
              <dt>ChirpStack</dt>
              <dd><code>object</code></dd>
            </dl>
          </div>
        </div>
      `;
    }

    if (this._activeTab === "devices") {
      return `
        <div class="list">
          ${this._renderDevices()}
        </div>
      `;
    }

    if (this._activeTab === "downlinks") {
      return this._renderDownlinks();
    }

    return `
      <div class="section">
        <div class="card">
          <h2>Uplinks</h2>
          <dl>
            <dt>Status</dt>
            <dd>${this._status.connected ? "MQTT verbunden" : "Wartet auf MQTT-Verbindung"}</dd>
            <dt>Uplinks</dt>
            <dd>${this._status.message_count || 0}</dd>
            <dt>Geraete</dt>
            <dd>${this._status.device_count || 0}</dd>
            <dt>Entities</dt>
            <dd>${this._status.entity_count || 0}</dd>
            <dt>Diagnose</dt>
            <dd>RSSI, SNR, Gateway, Frame Port und Counter als Attribute</dd>
          </dl>
        </div>
      </div>
    `;
  }

  _selectedDownlinkProfile() {
    return this._downlinks.profiles.find((profile) => profile.deviceType === this._downlinkProfile) || null;
  }

  _cloneProfile(profile) {
    return profile ? JSON.parse(JSON.stringify(profile)) : null;
  }

  _copyName(existingNames, name) {
    const base = `${name || "Neuer Eintrag"} (Kopie)`;
    let candidate = base;
    let number = 2;
    while (existingNames.includes(candidate)) {
      candidate = `${base} ${number}`;
      number += 1;
    }
    return candidate;
  }

  _duplicateProfile(profile) {
    if (!profile) return;
    const copy = this._cloneProfile(profile);
    copy.deviceType = this._copyName((this._downlinks.profiles || []).map((item) => item.deviceType), profile.deviceType);
    this._profileEditor = copy;
    this._render();
  }

  _duplicateParameter(index) {
    const parameters = this._profileEditor?.downlinkParameter;
    if (!Array.isArray(parameters) || !parameters[index]) return;
    const copy = JSON.parse(JSON.stringify(parameters[index]));
    copy.name = this._copyName(parameters.map((item) => item.name), copy.name);
    parameters.splice(index + 1, 0, copy);
    this._render();
  }

  _deleteParameter(index) {
    const parameters = this._profileEditor?.downlinkParameter;
    if (!Array.isArray(parameters) || !parameters[index]) return;
    parameters.splice(index, 1);
    this._render();
  }

  async _deleteProfile(profile) {
    if (!profile) return;
    const configured = this._downlinks.configured_profiles || [];
    const isBuiltIn = (this._downlinks.builtin_profile_types || []).includes(profile.deviceType);
    const message = `Downlink-Profil „${profile.deviceType}“ wirklich löschen?`;
    if (!window.confirm(message)) return;
    try {
      const remaining = configured.filter((item) => item.deviceType !== profile.deviceType);
      if (isBuiltIn) remaining.push({ deviceType: profile.deviceType, _deleted: true });
      await this._hass.callService("lorawan", "configure_downlink_profiles", {
        downlink_profiles: remaining,
      });
      if (this._downlinkProfile === profile.deviceType) this._downlinkProfile = "";
      await this._loadDownlinks();
    } catch (error) { window.alert(`Profil konnte nicht gelöscht werden: ${error.message || error}`); }
  }

  _renderDownlinks() {
    const profiles = this._downlinks.profiles || [];
    if (this._profileEditor) {
      const profile = this._profileEditor;
      return `
        <div class="card"><h2>Downlink-Profil bearbeiten</h2>
          <form class="profile-editor" data-profile-editor>
            <label>Gerätetyp<input name="deviceType" required value="${this._escape(profile.deviceType || "")}" /></label>
            <label>Mit Uplink senden<select name="sendWithUplink" data-profile-send-with-uplink><option ${profile.sendWithUplink === "disabled" ? "selected" : ""}>disabled</option><option ${profile.sendWithUplink === "enabled" ? "selected" : ""}>enabled</option><option ${profile.sendWithUplink === "enabled & collect" ? "selected" : ""}>enabled & collect</option></select></label>
            ${profile.sendWithUplink !== "disabled" ? `<label>Port<input name="port" type="number" value="${profile.port || 1}" /></label>
            <label>Priorität<input name="priority" value="${this._escape(profile.priority || "NORMAL")}" /></label>
            <label class="checkbox"><input name="confirmed" type="checkbox" ${profile.confirmed ? "checked" : ""} /> Bestätigt</label>` : ""}
            <h3>Individuelle Downlink-Konfiguration</h3>
            <button class="action" type="button" data-parameter-add>+ Parameter hinzufügen</button>
            ${(profile.downlinkParameter || []).map((parameter, index) => this._renderParameterEditor(parameter, index, profile)).join("")}
            <div class="actions"><button class="save" type="submit">Profil speichern</button><button class="action" type="button" data-profile-cancel>Abbrechen</button></div>
          </form>
        </div>`;
    }
    return `
      <div class="card">
        <h2>Gerätespezifische Downlink-Profile</h2>
        <p class="muted">Profile und Parameter entsprechen dem ioBroker-Adapter. Änderungen gelten als lokale Überschreibung.</p>
        <div class="profile-actions"><button class="save" type="button" data-profile-new>Eigenes Profil anlegen</button></div>
        <div class="profile-list">${profiles.map((profile) => `<details><summary><strong>${this._escape(profile.deviceType)}</strong> <span class="muted">(${(profile.downlinkParameter || []).length} Parameter)</span></summary><div class="profile-content"><ul class="profile-parameters">${(profile.downlinkParameter || []).map((parameter) => `<li class="profile-parameter"><strong>${this._escape(parameter.name)}</strong> <span class="muted">${this._escape(parameter.type || "number")}${parameter.unit ? ` · ${this._escape(parameter.unit)}` : ""}</span></li>`).join("")}</ul><div class="actions"><button class="action" type="button" data-profile-edit-type="${this._escape(profile.deviceType)}">Profil bearbeiten</button><button class="action duplicate" type="button" data-profile-duplicate-type="${this._escape(profile.deviceType)}">Duplizieren</button><button class="action danger" type="button" data-profile-delete-type="${this._escape(profile.deviceType)}">Löschen</button></div></div></details>`).join("")}</div>
      </div>`;
  }

  _renderParameterEditor(parameter, index, profile) {
    const value = (key, fallback = "") => this._escape(parameter[key] ?? fallback);
    const checked = (key) => parameter[key] ? "checked" : "";
    const type = parameter.type || "number";
    const isValueType = ["number", "ascii", "string"].includes(type);
    const isNumber = type === "number";
    return `<details ${this._openParameterEditorIndex === index ? "open" : ""}><summary><strong>${value("name", "Parameter")}</strong> <span class="muted">${value("type", "number")}</span></summary><div class="parameter-fields">
      <label>Name<input name="p${index}name" value="${value("name")}" /></label>
      <label>Typ<select name="p${index}type" data-parameter-type="${index}">${["number", "boolean", "button", "ascii", "string"].map((option) => `<option ${type === option ? "selected" : ""}>${option}</option>`).join("")}</select></label>
      <label>Port<input name="p${index}port" type="number" value="${value("port", profile.port || 1)}" /></label>
      <label>Priorität<input name="p${index}priority" value="${value("priority", "NORMAL")}" /></label>
      <label class="checkbox"><input name="p${index}confirmed" type="checkbox" ${checked("confirmed")} /> Bestätigt</label>
      ${isValueType ? `<label>Führend<input name="p${index}front" value="${value("front")}" /></label>
      <label>Folgend<input name="p${index}end" value="${value("end")}" /></label>` : ""}
      ${type !== "boolean" && type !== "button" && type !== "string" ? `<label>Länge (Byte)<input name="p${index}lengthInByte" type="number" min="1" max="20" value="${value("lengthInByte", 3)}" /></label>` : ""}
      ${type === "boolean" ? `<label>Ein-Folge (Hex)<input name="p${index}on" value="${value("on")}" /></label><label>Aus-Folge (Hex)<input name="p${index}off" value="${value("off")}" /></label>` : ""}
      ${type === "button" ? `<label>Klick-Folge (Hex)<input name="p${index}onClick" value="${value("onClick")}" /></label>` : ""}
      ${isNumber ? `<label>Multiplikator<input name="p${index}multiplyfaktor" type="number" step="any" value="${value("multiplyfaktor", 1)}" /></label>
      <label>Dezimalstellen<input name="p${index}decimalPlaces" type="number" min="0" max="5" value="${value("decimalPlaces", 0)}" /></label>
      <label>Einheit<input name="p${index}unit" value="${value("unit")}" /></label>` : ""}
      ${type === "ascii" ? `<label>Einheit<input name="p${index}unit" value="${value("unit")}" /></label>` : ""}
      <label>CRC<select name="p${index}crc">${[["noCrc", "keine CRC"], ["CRC-8", "CRC-8"], ["KERMIT", "KERMIT"], ["KERMIT.LittleEndian", "KERMIT (Little Endian)"]].map(([option, label]) => `<option value="${option}" ${value("crc", "noCrc") === option ? "selected" : ""}>${label}</option>`).join("")}</select></label>
      ${isNumber ? `<label class="checkbox"><input name="p${index}swap" type="checkbox" ${checked("swap")} /> Byte-Reihenfolge tauschen</label>
      <label class="checkbox"><input name="p${index}limitMin" data-parameter-visibility="${index}:limitMin" type="checkbox" ${checked("limitMin")} /> Minimum begrenzen</label>
      ${parameter.limitMin ? `<label>Min.-Wert<input name="p${index}limitMinValue" type="number" step="any" value="${value("limitMinValue", 0)}" /></label>` : ""}
      <label class="checkbox"><input name="p${index}limitMax" data-parameter-visibility="${index}:limitMax" type="checkbox" ${checked("limitMax")} /> Maximum begrenzen</label>
      ${parameter.limitMax ? `<label>Max.-Wert<input name="p${index}limitMaxValue" type="number" step="any" value="${value("limitMaxValue", 0)}" /></label>` : ""}
      <label class="checkbox"><input name="p${index}withStates" data-parameter-visibility="${index}:withStates" type="checkbox" ${checked("withStates")} /> Statuswerte verwenden</label>
      ${parameter.withStates ? `<label>Statuswerte<input name="p${index}statesValue" value="${value("statesValue")}" /></label>` : ""}` : ""}
    </div><div class="actions"><button class="action duplicate" type="button" data-parameter-duplicate="${index}">Parameter duplizieren</button><button class="action danger" type="button" data-parameter-delete="${index}">Parameter löschen</button></div></details>`;
  }

  _renderDownlinkParameter(parameter) {
    const name = this._escape(parameter.name);
    if (parameter.type === "button") {
      return `<div class="parameter"><div><strong>${name}</strong></div><button type="submit" name="parameter_name" value="${name}">Ausführen</button></div>`;
    }
    if (parameter.type === "boolean") {
      return `<div class="parameter"><div><strong>${name}</strong></div><label class="checkbox"><input type="checkbox" name="${name}" /> Aktiv</label></div>`;
    }
    const states = this._stateOptions(parameter);
    if (states.length) {
      return `<div class="parameter"><label><strong>${name}</strong>${parameter.unit ? ` (${this._escape(parameter.unit)})` : ""}</label><div class="actions"><select name="${name}">${states.map(([rawValue, label]) => `<option value="${this._escape(rawValue)}">${this._escape(label)} (${this._escape(rawValue)})</option>`).join("")}</select><button type="submit" name="parameter_name" value="${name}">Senden</button></div></div>`;
    }
    const decimalPlaces = Math.max(0, Number(parameter.decimalPlaces || 0));
    const step = decimalPlaces === 0 ? "1" : String(10 ** -decimalPlaces);
    return `<div class="parameter"><label><strong>${name}</strong>${parameter.unit ? ` (${this._escape(parameter.unit)})` : ""}</label><div class="actions"><input name="${name}" type="number" step="${step}" ${parameter.limitMin ? `min="${parameter.limitMinValue}"` : ""} ${parameter.limitMax ? `max="${parameter.limitMaxValue}"` : ""} /><button type="submit" name="parameter_name" value="${name}">Senden</button></div></div>`;
  }

  _stateOptions(parameter) {
    if (!parameter.withStates) return [];
    try {
      const states = typeof parameter.statesValue === "string"
        ? JSON.parse(parameter.statesValue)
        : parameter.statesValue;
      return states && typeof states === "object" && !Array.isArray(states)
        ? Object.entries(states)
        : [];
    } catch (error) {
      return [];
    }
  }

  async _sendDownlink(event) {
    event.preventDefault();
    const profile = this._selectedDownlinkProfile();
    const device = this._downlinks.devices.find((item) => item.dev_eui === this._downlinkDevice);
    const form = new FormData(event.currentTarget);
    const buttonParameter = event.submitter?.value;
    const parameterName = buttonParameter || (profile?.downlinkParameter || []).find((item) => item.type !== "button")?.name;
    const parameter = profile?.downlinkParameter?.find((item) => item.name === parameterName);
    if (!profile || !device || !parameter) return;
    const value = parameter.type === "button" ? true : parameter.type === "boolean" ? form.get(parameter.name) === "on" : form.get(parameter.name);
    try {
      const result = await this._hass.callWS({ type: "lorawan/send_downlink", dev_eui: device.dev_eui, device_type: profile.deviceType, parameter_name: parameter.name, value });
      window.alert(`Downlink gesendet: ${result.payload_hex}`);
    } catch (error) { window.alert(`Downlink konnte nicht gesendet werden: ${error.message || error}`); }
  }

  async _saveProfile(event) {
    event.preventDefault();
    try {
      const data = new FormData(event.currentTarget);
      const old = this._cloneProfile(this._profileEditor);
      if (!old || !Array.isArray(old.downlinkParameter)) {
        throw new Error("Kein zu speicherndes Downlink-Profil vorhanden");
      }
      const number = (name, fallback) => {
        const value = Number(data.get(name));
        return Number.isFinite(value) ? value : fallback;
      };
      const parameter = (item, index) => {
        const name = (field) => `p${index}${field}`;
        const text = (field, fallback = "") => data.has(name(field)) ? String(data.get(name(field)) || "") : fallback;
        const type = text("type", item.type || "number");
        const result = {
          ...item,
          name: text("name"),
          type,
          port: number(name("port"), item.port || old.port || 1),
          priority: text("priority", item.priority || "NORMAL"),
          confirmed: data.get(name("confirmed")) === "on",
          crc: text("crc", item.crc || "noCrc"),
        };
        if (["number", "ascii", "string"].includes(type)) {
          result.front = text("front", item.front || "");
          result.end = text("end", item.end || "");
        }
        if (["number", "ascii"].includes(type)) result.lengthInByte = number(name("lengthInByte"), item.lengthInByte || 3);
        if (type === "boolean") {
          result.on = text("on", item.on || "");
          result.off = text("off", item.off || "");
        }
        if (type === "button") result.onClick = text("onClick", item.onClick || "");
        if (type === "number") {
          result.multiplyfaktor = number(name("multiplyfaktor"), item.multiplyfaktor ?? 1);
          result.decimalPlaces = number(name("decimalPlaces"), item.decimalPlaces ?? 0);
          result.unit = text("unit", item.unit || "");
          result.swap = data.get(name("swap")) === "on";
          result.limitMin = data.get(name("limitMin")) === "on";
          result.limitMax = data.get(name("limitMax")) === "on";
          result.withStates = data.get(name("withStates")) === "on";
          if (result.limitMin) result.limitMinValue = number(name("limitMinValue"), item.limitMinValue ?? 0);
          if (result.limitMax) result.limitMaxValue = number(name("limitMaxValue"), item.limitMaxValue ?? 0);
          if (result.withStates) {
            result.statesValue = text("statesValue", item.statesValue || "");
            let states;
            try {
              states = JSON.parse(result.statesValue);
            } catch (error) {
              throw new Error(`${result.name}: Statuswerte müssen gültiges JSON sein`);
            }
            if (!states || typeof states !== "object" || Array.isArray(states) || !Object.keys(states).length) {
              throw new Error(`${result.name}: Statuswerte müssen ein JSON-Objekt mit mindestens einem Wert sein`);
            }
            result.statesValue = JSON.stringify(states);
          }
        }
        if (type === "ascii") result.unit = text("unit", item.unit || "");
        return result;
      };
      const sendWithUplink = String(data.get("sendWithUplink") || "disabled");
      const profile = {
        ...old,
        deviceType: String(data.get("deviceType") || ""),
        sendWithUplink,
        downlinkParameter: old.downlinkParameter.map(parameter),
      };
      if (sendWithUplink !== "disabled") {
        profile.port = number("port", old.port || 1);
        profile.priority = String(data.get("priority") || "NORMAL");
        profile.confirmed = data.get("confirmed") === "on";
      }
      if (!profile.deviceType || !Array.isArray(profile.downlinkParameter)) throw new Error("deviceType und downlinkParameter sind erforderlich");
      const current = (this._downlinks.configured_profiles || []).filter((item) => item.deviceType !== old.deviceType && item.deviceType !== profile.deviceType);
      current.push(profile);
      await this._hass.callService("lorawan", "configure_downlink_profiles", { downlink_profiles: current });
      this._profileEditor = null;
      this._downlinkProfile = profile.deviceType;
      await this._loadDownlinks();
    } catch (error) { window.alert(`Profil konnte nicht gespeichert werden: ${error.message || error}`); }
  }

  async _handleDeviceSettings(button) {
    this._deviceSettings = {
      devEui: button.getAttribute("data-device-settings"),
      entryId: button.getAttribute("data-entry-id") || "",
      name: button.getAttribute("data-device-name") || "Gerät",
      hours: button.getAttribute("data-device-hours") || "25",
      raw: button.getAttribute("data-device-raw") === "true",
      remaining: button.getAttribute("data-device-remaining") === "true",
    };
    this._render();
  }

  async _handleDeviceSettingsSubmit(event) {
    event.preventDefault();
    if (this._deviceSettings?.saving) return;
    const formData = new FormData(event.currentTarget);
    const hours = Number(formData.get("offline_after_hours"));
    if (!Number.isInteger(hours) || hours < 1 || hours > 8760) {
      window.alert("Bitte eine ganze Zahl zwischen 1 und 8760 eingeben.");
      return;
    }
    this._deviceSettings.saving = true;
    const controls = event.currentTarget.querySelectorAll("input, button");
    controls.forEach((control) => { control.disabled = true; });
    const saveButton = event.currentTarget.querySelector('button[type="submit"]');
    if (saveButton) saveButton.textContent = "Speichert…";
    try {
      await this._hass.callService("lorawan", "configure_device", {
        dev_eui: this._deviceSettings.devEui,
        entry_id: this._deviceSettings.entryId,
        offline_after_hours: hours,
        create_raw_sensors: formData.get("create_raw_sensors") === "on",
        create_remaining_sensors: formData.get("create_remaining_sensors") === "on",
      });
      this._deviceSettings = null;
      await this._loadDevices();
      await this._loadStatus();
    } catch (error) {
      this._deviceSettings.saving = false;
      controls.forEach((control) => { control.disabled = false; });
      if (saveButton) saveButton.textContent = "Speichern";
      window.alert("Speichern fehlgeschlagen.");
    }
  }

  async _showDeviceDiagnostics(button) {
    const devEui = button.getAttribute("data-device-json");
    this._deviceDiagnostics = {
      name: button.getAttribute("data-device-name") || "Gerät",
      loading: true,
      raw: null,
      remaining: null,
    };
    this._render();
    try {
      const diagnostics = await this._hass.callWS({
        type: "lorawan/device_diagnostics",
        dev_eui: devEui,
      });
      this._deviceDiagnostics = {
        ...this._deviceDiagnostics,
        loading: false,
        raw: diagnostics.raw,
        remaining: diagnostics.remaining,
      };
    } catch (error) {
      this._deviceDiagnostics = {
        ...this._deviceDiagnostics,
        loading: false,
        error: true,
      };
    }
    this._render();
  }

  _renderDeviceSettingsDialog() {
    const settings = this._deviceSettings;
    if (!settings) {
      return "";
    }
    return `
      <div class="dialog-backdrop" role="presentation">
        <div class="dialog" role="dialog" aria-modal="true" aria-label="Geräteeinstellungen">
          <h2>${this._escape(settings.name)}</h2>
          <form data-device-settings-form>
            <label>
              Offline nach Stunden
              <input name="offline_after_hours" type="number" min="1" max="8760" required value="${this._escape(settings.hours)}" />
            </label>
            <label class="checkbox">
              <input name="create_raw_sensors" type="checkbox" ${settings.raw ? "checked" : ""} />
              Raw-Diagnose aktivieren
            </label>
            <label class="checkbox">
              <input name="create_remaining_sensors" type="checkbox" ${settings.remaining ? "checked" : ""} />
              Verbleibende Payload-Diagnose aktivieren
            </label>
            <div class="actions">
              <button class="save" type="submit" ${settings.saving ? "disabled" : ""}>${settings.saving ? "Speichert…" : "Speichern"}</button>
              <button type="button" data-device-settings-cancel ${settings.saving ? "disabled" : ""}>Abbrechen</button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  _renderMessagesDialog() {
    if (!this._selectedMessage) {
      return "";
    }
    const messages = this._messagesForSelectedConnection();
    const selectedIndex = messages.indexOf(this._selectedMessage);
    return `
      <div class="dialog-backdrop" role="presentation">
        <div class="dialog" role="dialog" aria-modal="true" aria-label="Letzte Nachrichten">
          <h2>Letzte Nachrichten</h2>
          <div class="message-list">
            ${messages.map((message, index) => `
              <button class="message-item ${index === selectedIndex ? "selected" : ""}" type="button" data-message-index="${index}">
                <strong>${this._formatDate(message.received_at)}</strong><br />
                <code>${this._escape(message.topic)}</code>
              </button>
            `).join("")}
          </div>
          <h3>Topic</h3>
          <code>${this._escape(this._selectedMessage.topic)}</code>
          <h3>Payload</h3>
          <pre class="payload">${this._escape(this._selectedMessage.payload)}</pre>
          <div class="actions">
            <button type="button" data-messages-close>Schließen</button>
          </div>
        </div>
      </div>
    `;
  }

  _messagesForSelectedConnection() {
    const messages = this._status.recent_messages || [];
    if (!this._selectedConnectionId) return messages;
    return messages.filter((message) => message.entry_id === this._selectedConnectionId);
  }

  _renderDeviceDiagnosticsDialog() {
    const diagnostics = this._deviceDiagnostics;
    if (!diagnostics) {
      return "";
    }
    const renderPayload = (title, value) => `
      <h3>${title}</h3>
      <pre class="payload">${value === null ? "Nicht aktiviert oder noch kein Uplink empfangen." : this._escape(JSON.stringify(value, null, 2))}</pre>
    `;
    return `
      <div class="dialog-backdrop" role="presentation">
        <div class="dialog" role="dialog" aria-modal="true" aria-label="MQTT-Daten">
          <h2>${this._escape(diagnostics.name)}</h2>
          ${diagnostics.loading ? "Daten werden geladen..." : diagnostics.error ? "Daten konnten nicht geladen werden." : `
            ${renderPayload("Raw JSON", diagnostics.raw)}
            ${renderPayload("Weitere MQTT-Daten", diagnostics.remaining)}
          `}
          <div class="actions">
            <button type="button" data-device-diagnostics-close>Schließen</button>
          </div>
        </div>
      </div>
    `;
  }

  _renderDevices() {
    if (!this._devices.length) {
      return `
        <div class="device-card">
          <div>
            <div class="device-name">Keine Geraete gefunden</div>
            <div class="muted">Geraete erscheinen hier nach dem ersten passenden Uplink.</div>
          </div>
        </div>
      `;
    }

    return this._devices
      .map((device) => {
        const identifier = device.identifiers?.[0] || "-";
        const subtitle = device.model || device.manufacturer || "LoRaWAN";
        return `
          <div class="device-card" role="button" tabindex="0" data-device-open="${this._escape(device.id)}">
            <div>
              <div class="device-name">${this._escape(device.name)}</div>
              <div class="muted">${this._escape(subtitle)}</div>
              ${device.application_name ? `<div class="muted">Applikation: ${this._escape(device.application_name)}</div>` : ""}
              <div class="device-eui muted">DevEUI<br /><code>${this._escape(identifier)}</code></div>
              <div class="diagnostics">
                ${device.connection_name ? `<span class="tag connection-tag" style="${this._connectionTagStyle(device.connection_color)}">${this._escape(device.connection_name)}</span>` : ""}
                ${device.create_raw_sensors ? '<span class="tag">Raw</span>' : ""}
                ${device.create_remaining_sensors ? '<span class="tag">Rest</span>' : ""}
              </div>
            </div>
            <span class="device-status status" title="${device.online ? "Online" : "Offline"}">
              <span class="dot ${device.online ? "connected" : "error"}"></span>
            </span>
            <button
              class="icon-button device-settings"
              type="button"
              title="Geräteeinstellungen"
              data-device-settings="${this._escape(identifier)}"
              data-entry-id="${this._escape(device.entry_id || "")}"
              data-device-name="${this._escape(device.name)}"
              data-device-hours="${device.offline_after_hours || device.offline_after_default_hours || 25}"
              data-device-raw="${Boolean(device.create_raw_sensors)}"
              data-device-remaining="${Boolean(device.create_remaining_sensors)}"
            >⚙</button>
            ${device.create_raw_sensors || device.create_remaining_sensors ? `<button
              class="icon-button device-json"
              type="button"
              title="MQTT-Daten anzeigen"
              data-device-json="${this._escape(identifier)}"
              data-device-name="${this._escape(device.name)}"
            >{ }</button>` : ""}
          </div>
        `;
      })
      .join("");
  }

  _connectionTagStyle(color) {
    const channels = String(color || "").match(/\d+/g)?.slice(0, 3).map(Number);
    if (!channels || channels.length !== 3) return "";
    const [red, green, blue] = channels;
    const luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255;
    return `background:${color};color:${luminance > 0.62 ? "#111" : "#fff"}`;
  }

  _formatDetectedNetworks(counts) {
    const detected = [];
    if (counts?.ttn > 0) detected.push(`TTN ${counts.ttn}`);
    if (counts?.chirpstack > 0) detected.push(`ChirpStack ${counts.chirpstack}`);
    return detected.length ? detected.join(", ") : "Noch keine Nachrichten";
  }

  _startStatusPolling() {
    if (!this._hass || this._statusTimer) {
      return;
    }
    this._loadStatus();
    this._statusTimer = setInterval(() => this._loadStatus(), 5000);
  }

  async _startDeviceSubscription() {
    if (!this._hass || this._deviceUnsubscribe || this._deviceSubscribePending) {
      return;
    }
    this._deviceSubscribePending = true;
    this._loadDevices();
    try {
      this._deviceUnsubscribe = await this._hass.connection.subscribeMessage(
        () => {
          this._loadDevices();
          setTimeout(() => this._loadDevices(), 1000);
        },
        { type: "lorawan/subscribe_devices" }
      );
    } catch (error) {
      this._deviceUnsubscribe = undefined;
    } finally {
      this._deviceSubscribePending = false;
    }
  }

  async _loadStatus() {
    if (!this._hass) {
      return;
    }
    try {
      const status = await this._hass.callWS({ type: "lorawan/status" });
      this._status = status;
      if (this._activeTab !== "downlinks" && !this._deviceSettings) {
        this._render();
      }
      if (this._activeTab === "devices" && !this._deviceSettings) {
        await this._loadDevices();
      }
    } catch (error) {
      this._status = {
        ...this._status,
        connected: false,
        last_error: "Status nicht verfuegbar",
      };
      if (!this._deviceSettings) this._render();
    }
  }

  async _loadDevices() {
    if (!this._hass) {
      return;
    }
    try {
      const devices = await this._hass.callWS({ type: "lorawan/devices" });
      this._devices = devices.devices || [];
      if (this._activeTab !== "downlinks" && !this._deviceSettings) this._render();
    } catch (error) {
      this._devices = [];
      if (this._activeTab !== "downlinks" && !this._deviceSettings) this._render();
    }
  }

  async _loadDownlinks() {
    if (!this._hass) return;
    try {
      this._downlinks = await this._hass.callWS({ type: "lorawan/downlinks" });
      if (!this._downlinkDevice && this._downlinks.devices.length) {
        this._downlinkDevice = this._downlinks.devices[0].dev_eui;
        this._downlinkProfile = this._downlinks.devices[0].device_type || "";
      }
    } catch (error) { this._downlinks = { devices: [], profiles: [], configured_profiles: [], builtin_profile_types: [] }; }
  }

  _formatDate(value) {
    if (!value) {
      return "-";
    }
    return new Date(value).toLocaleString();
  }

  _escape(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll('"', "&quot;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }
}

if (!customElements.get("lorawan-panel")) {
  customElements.define("lorawan-panel", LoRaWANPanel);
}
