class LoRaWANPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._activeTab = "uplinks";
    this._rendered = false;
    this._saveMessage = "";
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
    this._mqttDirty = false;
    this._mqttConfig = {
      host: "",
      port: 1883,
      ssl: false,
      username: "",
      password: "",
    };
  }

  set hass(hass) {
    this._hass = hass;
    this._startStatusPolling();
    this._startDeviceSubscription();
    if (!this._rendered) {
      this._render();
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
      ["uplinks", "Uplinks"],
      ["lns", "LNS / MQTT"],
      ["devices", "Geraete"],
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
          gap: 0;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          overflow: hidden;
          background: var(--card-background-color);
        }

        .device-row {
          display: grid;
          grid-template-columns: minmax(220px, 1.4fr) minmax(180px, 1fr) 96px 120px 48px;
          gap: 16px;
          align-items: center;
          min-height: 64px;
          padding: 12px 16px;
          border-bottom: 1px solid var(--divider-color);
          color: inherit;
          text-decoration: none;
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

        .device-row:last-child {
          border-bottom: 0;
        }

        .device-name {
          font-weight: 500;
        }

        .muted {
          color: var(--secondary-text-color);
        }

        .arrow {
          justify-self: end;
          color: var(--secondary-text-color);
          font-size: 24px;
          text-decoration: none;
        }

        @media (max-width: 720px) {
          .device-row {
            grid-template-columns: 1fr;
            gap: 6px;
          }

          .arrow {
            display: none;
          }
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
    `;

    this.shadowRoot.querySelectorAll("button[data-tab]").forEach((button) => {
      button.addEventListener("click", () =>
        this._setActiveTab(button.getAttribute("data-tab"))
      );
    });
    this.shadowRoot
      .querySelector("form[data-mqtt-form]")
      ?.addEventListener("submit", (event) => this._handleMqttSubmit(event));
    this.shadowRoot
      .querySelector("form[data-mqtt-form]")
      ?.addEventListener("input", () => {
        this._mqttDirty = true;
      });
    this.shadowRoot
      .querySelectorAll("button[data-device-settings]")
      .forEach((button) => {
        button.addEventListener("click", () =>
          this._handleDeviceSettings(button)
        );
      });
  }

  _renderContent() {
    if (this._activeTab === "lns") {
      return `
        <div class="section">
          <div class="card">
            <h2>Status</h2>
            <dl>
              <dt>Verbindung</dt>
              <dd>
                <span class="status">
                  <span class="dot ${this._status.connected ? "connected" : this._status.last_error ? "error" : ""}"></span>
                  ${this._status.connected ? "Aktiv" : "Nicht verbunden"}
                </span>
              </dd>
              <dt>Letzte Nachricht</dt>
              <dd>${this._formatDate(this._status.last_message_at)}</dd>
              <dt>Letztes Topic</dt>
              <dd><code>${this._escape(this._status.last_topic || "-")}</code></dd>
              <dt>Erkannt</dt>
              <dd>TTN ${this._status.lns_counts?.ttn || 0}, ChirpStack ${this._status.lns_counts?.chirpstack || 0}</dd>
              <dt>Fehler</dt>
              <dd>${this._escape(this._status.last_error || "-")}</dd>
            </dl>
          </div>
          <div class="card">
            <h2>MQTT Broker</h2>
            <form data-mqtt-form>
              <label>
                Host
                <input name="host" autocomplete="off" required value="${this._escape(
                  this._mqttConfig.host
                )}" />
              </label>
              <label>
                Port
                <input name="port" type="number" min="1" max="65535" value="${this._mqttConfig.port}" required />
              </label>
              <label class="checkbox">
                <input name="ssl" type="checkbox" ${this._mqttConfig.ssl ? "checked" : ""} />
                SSL
              </label>
              <label>
                Benutzername
                <input name="username" autocomplete="username" value="${this._escape(
                  this._mqttConfig.username
                )}" />
              </label>
              <label>
                Passwort
                <input
                  name="password"
                  type="password"
                  autocomplete="current-password"
                  placeholder="${this._status.has_password ? "Gespeichert" : ""}"
                  value="${this._escape(this._mqttConfig.password)}"
                />
              </label>
              <div class="actions">
                <button class="save" type="submit">Speichern</button>
                <span class="message">${this._saveMessage}</span>
              </div>
            </form>
          </div>
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

  async _handleMqttSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    this._mqttConfig = {
      host: String(formData.get("host") || ""),
      port: Number(formData.get("port") || 1883),
      ssl: formData.get("ssl") === "on",
      username: String(formData.get("username") || ""),
      password: String(formData.get("password") || ""),
    };
    this._saveMessage = "Speichern...";
    this._render();

    try {
      const payload = {
        host: this._mqttConfig.host,
        port: this._mqttConfig.port,
        ssl: this._mqttConfig.ssl,
        username: this._mqttConfig.username,
      };
      if (this._mqttConfig.password) {
        payload.password = this._mqttConfig.password;
      }
      await this._hass.callService("lorawan", "configure_mqtt", payload);
      this._mqttDirty = false;
      this._saveMessage = "Gespeichert";
    } catch (error) {
      this._saveMessage = "Speichern fehlgeschlagen";
    }
    this._render();
  }

  async _handleDeviceSettings(button) {
    const devEui = button.getAttribute("data-device-settings");
    const currentHours = button.getAttribute("data-device-hours") || "25";
    const value = window.prompt("Offline nach wie vielen Stunden?", currentHours);
    if (value === null) {
      return;
    }
    const hours = Number(value);
    if (!Number.isInteger(hours) || hours < 1 || hours > 8760) {
      window.alert("Bitte eine ganze Zahl zwischen 1 und 8760 eingeben.");
      return;
    }
    await this._hass.callService("lorawan", "configure_device", {
      dev_eui: devEui,
      offline_after_hours: hours,
    });
    await this._loadDevices();
    await this._loadStatus();
  }

  _renderDevices() {
    if (!this._devices.length) {
      return `
        <div class="device-row">
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
        const subtitle = [device.model, device.sw_version]
          .filter(Boolean)
          .join(" · ");
        return `
          <div class="device-row">
            <div>
              <div class="device-name">${this._escape(device.name)}</div>
              <div class="muted">${this._escape(subtitle || device.manufacturer || "LoRaWAN")}</div>
            </div>
            <div>
              <div class="muted">DevEUI</div>
              <code>${this._escape(identifier)}</code>
            </div>
            <div>
              <div class="muted">Entities</div>
              <div>${device.entity_count || 0}</div>
            </div>
            <div>
              <div class="muted">Offline nach</div>
              <div>${device.offline_after_hours || device.offline_after_default_hours || 25} h</div>
            </div>
            <button
              class="icon-button"
              type="button"
              title="Geräteeinstellungen"
              data-device-settings="${this._escape(identifier)}"
              data-device-hours="${device.offline_after_hours || device.offline_after_default_hours || 25}"
            >⚙</button>
            <a class="arrow" href="/config/devices/device/${this._escape(device.id)}">›</a>
          </div>
        `;
      })
      .join("");
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
      if (!this._mqttDirty) {
        this._mqttConfig = {
          ...this._mqttConfig,
          host: status.host ?? this._mqttConfig.host,
          port: status.port ?? this._mqttConfig.port,
          ssl: Boolean(status.ssl),
          username: status.username || "",
          password: "",
        };
      }
      this._render();
    } catch (error) {
      this._status = {
        ...this._status,
        connected: false,
        last_error: "Status nicht verfuegbar",
      };
      this._render();
    }
  }

  async _loadDevices() {
    if (!this._hass) {
      return;
    }
    try {
      const devices = await this._hass.callWS({ type: "lorawan/devices" });
      this._devices = devices.devices || [];
      this._render();
    } catch (error) {
      this._devices = [];
      this._render();
    }
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

customElements.define("lorawan-panel", LoRaWANPanel);
