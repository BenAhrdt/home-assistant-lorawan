const TRANSLATIONS = {
  de: {
    devices: "Geräte", protocol: "Protokoll", connection: "Verbindung", active: "Aktiv",
    disconnected: "Nicht verbunden", broker: "Broker", lastMessage: "Letzte Nachricht",
    lastTopic: "Letztes Topic", detected: "Erkannt", errors: "Fehler", formats: "Formate",
    status: "Status", entities: "Entitäten", mqttConnected: "MQTT verbunden",
    waitingForMqtt: "Wartet auf MQTT-Verbindung", recentMessages: "Letzte Nachrichten",
    showRecentMessages: "Letzte Nachrichten anzeigen", direction: "Richtung", close: "Schließen",
    deviceType: "Gerätetyp", sendWithUplink: "Mit Uplink senden", priority: "Priorität",
    confirmed: "Bestätigt", customDownlinkConfig: "Individuelle Downlink-Konfiguration",
    addParameter: "+ Parameter hinzufügen", saveProfile: "Profil speichern", saving: "Speichert…",
    cancel: "Abbrechen", deviceProfiles: "Gerätespezifische Downlink-Profile",
    profileDescription: "Profile und Parameter entsprechen dem ioBroker-Adapter. Änderungen gelten als lokale Überschreibung.",
    createProfile: "Eigenes Profil anlegen", newProfile: "Neues Downlink-Profil", duplicate: "Duplizieren",
    delete: "Löschen", type: "Typ", leading: "Führend", trailing: "Folgend", lengthBytes: "Länge (Byte)",
    onSequence: "Ein-Folge (Hex)", offSequence: "Aus-Folge (Hex)", clickSequence: "Klick-Folge (Hex)",
    multiplier: "Multiplikator", decimalPlaces: "Dezimalstellen", unit: "Einheit", noCrc: "keine CRC",
    swapBytes: "Byte-Reihenfolge tauschen", limitMinimum: "Minimum begrenzen", minimumValue: "Min.-Wert",
    limitMaximum: "Maximum begrenzen", maximumValue: "Max.-Wert", useStates: "Statuswerte verwenden",
    stateValues: "Statuswerte", duplicateParameter: "Parameter duplizieren", deleteParameter: "Parameter löschen",
    execute: "Ausführen", enabled: "Aktiv", send: "Senden", device: "Gerät", newEntry: "Neuer Eintrag",
    copy: "Kopie", newParameter: "Neuer Parameter", newProfileName: "Neues Profil",
    offlineAfterHours: "Offline nach Stunden", enableRawDiagnostics: "Raw-Diagnose aktivieren",
    enableRemainingDiagnostics: "Verbleibende Payload-Diagnose aktivieren", tileValues: "Werte auf der Gerätekachel",
    moveUp: "Nach oben", moveDown: "Nach unten", noActiveEntities: "Diesem Gerät sind noch keine aktiven Entitäten zugeordnet.",
    compositeClimate: "Zusammengesetzte Climate-Entitäten", notAssigned: "Nicht zugewiesen",
    additionalEntities: "Zusätzliche Entitäten", configure: "Konfigurieren", done: "Fertig",
    climateEntity: "Climate-Entität", climateEntities: "Climate-Entitäten",
    noAdditionalEntities: "Noch keine zusätzlichen Entitäten konfiguriert", configured: "konfiguriert",
    currentTemperature: "Isttemperatur (Uplink)", readTargetTemperature: "Solltemperatur lesen (Uplink, optional)",
    setTargetTemperature: "Solltemperatur setzen (Downlink, optional)", readHvacMode: "Betriebsmodus lesen (optional)",
    setHvacMode: "Betriebsmodus setzen (Downlink, optional)", removeClimate: "Climate entfernen",
    addAndAssignEntity: "Entität hinzufügen und zuweisen", save: "Speichern", deviceSettings: "Geräteeinstellungen",
    invalidHours: "Bitte eine ganze Zahl zwischen 1 und 8760 eingeben.", saveFailed: "Speichern fehlgeschlagen.",
    noDevices: "Keine Geräte gefunden", devicesAfterUplink: "Geräte erscheinen hier nach dem ersten passenden Uplink.",
    online: "Online", offline: "Offline", lastUplink: "Letzter Uplink", application: "Applikation",
    showMqttData: "MQTT-Daten anzeigen", noEvents: "Noch keine Ereignisse aufgezeichnet.", event: "Ereignis",
    press: "Drücken", emptyValue: "(leerer Wert)", on: "Ein", off: "Aus", open: "öffnen",
    currentShort: "Ist", targetShort: "Soll", openClimate: "Climate öffnen", sending: "Wird gesendet…",
    sent: "Gesendet ✓", failed: "Fehler ✕", writeFailed: "Wert konnte nicht geschrieben werden.",
    battery: "Batterie", garageDoor: "Garagentor", window: "Fenster", door: "Tür", contact: "Kontakt",
    opened: "Geöffnet", closed: "Geschlossen", locked: "Verriegelt", unlocked: "Entriegelt",
    idle: "Ruhe", motionDetected: "Bewegung erkannt", clear: "Frei", occupied: "Belegt", safe: "Sicher",
    unsafe: "Unsicher", noSmoke: "Kein Rauch", smokeDetected: "Rauch erkannt", dataLoading: "Daten werden geladen…",
    dataLoadFailed: "Daten konnten nicht geladen werden.", deviceLoadFailed: "Geräteliste konnte nicht geladen werden.", diagnosticUnavailable: "Nicht aktiviert oder noch kein Uplink empfangen.",
    moreMqttData: "Weitere MQTT-Daten", noMessages: "Noch keine Nachrichten",
    noConfirmation: "Noch keine Bestätigung", profileDeleteFailed: "Profil konnte nicht gelöscht werden",
    downlinkSent: "Downlink gesendet", downlinkSendFailed: "Downlink konnte nicht gesendet werden"
  },
  en: {
    devices: "Devices", protocol: "Log", connection: "Connection", active: "Active",
    disconnected: "Disconnected", broker: "Broker", lastMessage: "Last message", lastTopic: "Last topic",
    detected: "Detected", errors: "Errors", formats: "Formats", status: "Status", entities: "Entities",
    mqttConnected: "MQTT connected", waitingForMqtt: "Waiting for MQTT connection", recentMessages: "Recent messages",
    showRecentMessages: "Show recent messages", direction: "Direction", close: "Close", deviceType: "Device type",
    sendWithUplink: "Send with uplink", priority: "Priority", confirmed: "Confirmed",
    customDownlinkConfig: "Custom downlink configuration", addParameter: "+ Add parameter", saveProfile: "Save profile",
    saving: "Saving…", cancel: "Cancel", deviceProfiles: "Device-specific downlink profiles",
    profileDescription: "Profiles and parameters follow the ioBroker adapter. Changes are stored as local overrides.",
    createProfile: "Create custom profile", newProfile: "New downlink profile", duplicate: "Duplicate", delete: "Delete",
    type: "Type", leading: "Prefix", trailing: "Suffix", lengthBytes: "Length (bytes)", onSequence: "On sequence (hex)",
    offSequence: "Off sequence (hex)", clickSequence: "Click sequence (hex)", multiplier: "Multiplier",
    decimalPlaces: "Decimal places", unit: "Unit", noCrc: "no CRC", swapBytes: "Swap byte order",
    limitMinimum: "Limit minimum", minimumValue: "Minimum value", limitMaximum: "Limit maximum",
    maximumValue: "Maximum value", useStates: "Use state values", stateValues: "State values",
    duplicateParameter: "Duplicate parameter", deleteParameter: "Delete parameter", execute: "Run", enabled: "Enabled",
    send: "Send", device: "Device", newEntry: "New entry", copy: "Copy", newParameter: "New parameter",
    newProfileName: "New profile", offlineAfterHours: "Offline after hours", enableRawDiagnostics: "Enable raw diagnostics",
    enableRemainingDiagnostics: "Enable remaining payload diagnostics", tileValues: "Values on the device card",
    moveUp: "Move up", moveDown: "Move down", noActiveEntities: "No active entities are assigned to this device yet.",
    compositeClimate: "Composite climate entities", notAssigned: "Not assigned", currentTemperature: "Current temperature (uplink)",
    additionalEntities: "Additional entities", configure: "Configure", done: "Done",
    climateEntity: "climate entity", climateEntities: "climate entities",
    noAdditionalEntities: "No additional entities configured yet", configured: "configured",
    readTargetTemperature: "Read target temperature (uplink, optional)", setTargetTemperature: "Set target temperature (downlink, optional)",
    readHvacMode: "Read HVAC mode (optional)", setHvacMode: "Set HVAC mode (downlink, optional)", removeClimate: "Remove climate",
    addAndAssignEntity: "Add and assign entity", save: "Save", deviceSettings: "Device settings",
    invalidHours: "Enter a whole number between 1 and 8760.", saveFailed: "Saving failed.", noDevices: "No devices found",
    devicesAfterUplink: "Devices appear here after the first matching uplink.", online: "Online", offline: "Offline",
    lastUplink: "Last uplink", application: "Application", showMqttData: "Show MQTT data", noEvents: "No events recorded yet.",
    event: "Event", press: "Press", emptyValue: "(empty value)", on: "On", off: "Off", open: "open",
    currentShort: "Current", targetShort: "Target", openClimate: "Open climate", sending: "Sending…", sent: "Sent ✓",
    failed: "Failed ✕", writeFailed: "The value could not be written.", battery: "Battery", garageDoor: "Garage door",
    window: "Window", door: "Door", contact: "Contact", opened: "open", closed: "closed", locked: "Locked",
    unlocked: "Unlocked", idle: "Idle", motionDetected: "Motion detected", clear: "Clear", occupied: "Occupied",
    safe: "Safe", unsafe: "Unsafe", noSmoke: "No smoke", smokeDetected: "Smoke detected", dataLoading: "Loading data…",
    dataLoadFailed: "Data could not be loaded.", deviceLoadFailed: "Device list could not be loaded.", diagnosticUnavailable: "Not enabled or no uplink received yet.",
    moreMqttData: "Additional MQTT data", noMessages: "No messages yet", noConfirmation: "No confirmation yet",
    profileDeleteFailed: "Profile could not be deleted", downlinkSent: "Downlink sent",
    downlinkSendFailed: "Downlink could not be sent"
  }
};

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
    this._devicesError = null;
    this._deviceSettings = null;
    this._additionalEntitiesDialogOpen = false;
    this._deviceDiagnostics = null;
    this._selectedMessage = null;
    this._selectedConnectionId = null;
    this._downlinks = { devices: [], profiles: [], configured_profiles: [], builtin_profile_types: [] };
    this._downlinkDevice = "";
    this._downlinkProfile = "";
    this._profileEditor = null;
    this._profileEditorOriginalType = null;
    this._openParameterEditorIndex = null;
    this._narrow = false;
  }

  set narrow(narrow) {
    this._narrow = Boolean(narrow);
    this.toggleAttribute("narrow", this._narrow);
    this._updateMenuButton();
  }

  get narrow() {
    return this._narrow;
  }

  set hass(hass) {
    const previousLanguage = this._language();
    this._hass = hass;
    this._startStatusPolling();
    this._startDeviceSubscription();
    if (!this._rendered) {
      this._loadDownlinks();
    }
    if (!this._rendered || previousLanguage !== this._language()) {
      if (this._activeTab !== "downlinks") this._render();
    }
    this._updateMenuButton();
  }

  _updateMenuButton() {
    const menuButton = this.shadowRoot?.querySelector("ha-menu-button");
    if (!menuButton) return;
    menuButton.hass = this._hass;
    menuButton.narrow = this._narrow;
  }

  _language() {
    const language = this._hass?.locale?.language || this._hass?.language || navigator.language || "en";
    return String(language).toLowerCase().startsWith("de") ? "de" : "en";
  }

  _t(key) {
    return TRANSLATIONS[this._language()][key] || TRANSLATIONS.de[key] || key;
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
      ["devices", this._t("devices")],
      ["lns", "LNS / MQTT"],
      ["uplinks", "Uplinks"],
      ["downlinks", "Downlinks"],
      ["protocol", this._t("protocol")],
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
          box-sizing: border-box;
          width: 100%;
          margin: 0 auto;
          padding: 24px;
        }

        header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
        }

        .menu-button {
          display: none;
          flex: 0 0 auto;
          margin-left: -12px;
        }

        :host([narrow]) .menu-button {
          display: block;
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
        }

        .device-card[data-device-open] {
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
          font-weight: 500;
        }

        .device-card-header {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          align-items: center;
          gap: 2px 10px;
          margin-bottom: 6px;
        }

        .device-eui {
          margin-top: 12px;
          font-size: 0.9em;
        }

        .device-meta-row {
          display: flex;
          align-items: end;
          justify-content: space-between;
          gap: 12px;
        }

        .device-indicators {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 10px;
          padding-bottom: 1px;
          color: var(--secondary-text-color);
        }

        .device-indicator {
          display: inline-flex;
          align-items: center;
          gap: 3px;
          white-space: nowrap;
          font-weight: 500;
        }

        .device-indicator ha-icon {
          --mdc-icon-size: 21px;
        }

        .device-indicator.low-battery {
          color: var(--error-color, #db4437);
        }

        .device-status {
          justify-self: end;
          font-size: 13px;
        }

        .last-uplink {
          grid-column: 1 / -1;
          justify-self: end;
          color: var(--secondary-text-color);
          font-size: 12px;
          font-weight: 400;
          white-space: nowrap;
        }

        .tile-values {
          display: grid;
          gap: 5px;
          margin-top: 12px;
          padding-bottom: 34px;
          font-size: 0.9em;
        }

        .tile-value {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          width: 100%;
          border-radius: 4px;
          padding: 3px 4px;
          white-space: normal;
          overflow-wrap: anywhere;
        }

        .tile-value:hover {
          background: var(--secondary-background-color);
        }

        button.tile-entity-name,
        button.tile-read-value,
        button.tile-control-button {
          min-height: 26px;
          border: 0;
          padding: 2px 4px;
          color: var(--primary-text-color);
          background: transparent;
          font: inherit;
          text-align: left;
          white-space: normal;
        }

        button.tile-entity-name {
          min-width: 0;
          font-weight: 500;
        }
        button.tile-entity-name ha-icon {
          --mdc-icon-size: 19px;
          margin-right: 5px;
          vertical-align: middle;
        }
        button.climate-summary {
          white-space: nowrap;
          font-variant-numeric: tabular-nums;
        }

        button.tile-entity-name:hover,
        button.tile-entity-name:focus-visible,
        button.tile-read-value:hover,
        button.tile-read-value:focus-visible {
          text-decoration: underline;
          outline: none;
        }

        .tile-control-wrap {
          display: inline-flex;
          align-items: center;
          justify-content: flex-end;
          gap: 5px;
          min-width: 82px;
        }

        .tile-control {
          box-sizing: border-box;
          width: 82px;
          min-height: 28px;
          border: 0;
          border-bottom: 1px solid var(--secondary-text-color);
          border-radius: 2px 2px 0 0;
          padding: 3px 6px;
          color: var(--primary-text-color);
          background: var(--secondary-background-color);
          font: inherit;
          text-align: right;
        }

        .tile-control.tile-text-control {
          width: 112px;
          text-align: left;
        }

        .tile-control-unit {
          color: var(--secondary-text-color);
          white-space: nowrap;
        }

        button.tile-control-button {
          color: var(--primary-color);
          font-weight: 500;
          border-radius: 4px;
          transition: transform 80ms ease, background-color 160ms ease, color 160ms ease;
        }

        button.tile-control-button:hover {
          background: var(--secondary-background-color);
        }

        button.tile-control-button:active {
          transform: scale(0.94);
        }

        button.tile-control-button.sending {
          color: var(--secondary-text-color);
          background: var(--secondary-background-color);
        }

        button.tile-control-button.success {
          color: var(--success-color, #0b8f47);
          background: color-mix(in srgb, var(--success-color, #0b8f47) 12%, transparent);
        }

        button.tile-control-button.failed {
          color: var(--error-color, #db4437);
          background: color-mix(in srgb, var(--error-color, #db4437) 12%, transparent);
        }

        .tile-switch-control {
          width: 18px;
          min-height: auto;
          margin: 0 4px;
        }

        .value-selection {
          grid-column: 1 / -1;
          display: grid;
          gap: 8px;
          max-height: 280px;
          overflow-y: auto;
          padding: 10px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
        }

        .settings-subsection {
          grid-column: 1 / -1;
          display: grid;
          gap: 8px;
          padding: 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
        }

        .settings-subsection button {
          justify-self: start;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          padding: 9px 14px;
          color: var(--primary-text-color);
        }

        .value-selection-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
        }

        .value-selection-row label.checkbox {
          flex: 1;
          min-width: 0;
        }

        .value-order-actions {
          display: inline-flex;
          gap: 2px;
        }

        button.value-order-button {
          width: 30px;
          height: 30px;
          border: 0;
          border-radius: 50%;
          padding: 0;
          color: var(--primary-text-color);
          background: transparent;
          font-size: 17px;
        }

        button.value-order-button:hover:not(:disabled) {
          background: var(--secondary-background-color);
        }

        button.value-order-button:disabled {
          color: var(--disabled-text-color);
          cursor: default;
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

        .dialog-backdrop.secondary {
          z-index: 20;
        }

        .dialog {
          box-sizing: border-box;
          width: min(480px, 100%);
          padding: 24px;
          border-radius: 12px;
          background: var(--card-background-color);
          box-shadow: var(--ha-card-box-shadow, 0 4px 18px rgba(0, 0, 0, 0.3));
        }

        .additional-entities-dialog {
          width: min(640px, 100%);
          max-height: calc(100vh - 40px);
          overflow-y: auto;
        }

        .additional-entities-dialog form {
          gap: 12px;
        }

        .additional-entities-dialog .value-selection {
          max-height: none;
          overflow: visible;
        }

        .dialog form, .profile-editor {
          display: grid;
          grid-template-columns: 1fr;
        }

        .profile-editor details, .profile-list > details { padding: 12px; border: 1px solid var(--divider-color); border-radius: 8px; background: var(--card-background-color); }
        .profile-editor details > div, .profile-list details > div { margin-top: 12px; }
        .profile-actions { margin-bottom: 16px; }
        .new-profile-editor { margin-bottom: 16px; padding: 12px; border: 1px solid var(--divider-color); border-radius: 8px; }
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

        .protocol-list {
          display: grid;
          gap: 10px;
        }

        .protocol-event {
          display: grid;
          grid-template-columns: 10px minmax(0, 1fr) auto;
          gap: 10px;
          align-items: start;
          padding: 12px 14px;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          background: var(--card-background-color);
        }

        .protocol-level {
          width: 10px;
          height: 10px;
          margin-top: 5px;
          border-radius: 50%;
          background: var(--info-color, var(--primary-color));
        }

        .protocol-event.warning .protocol-level {
          background: var(--warning-color, #f5a623);
        }

        .protocol-event.error .protocol-level {
          background: var(--error-color, #db4437);
        }

        .protocol-title {
          font-weight: 500;
        }

        .protocol-message {
          margin-top: 3px;
          color: var(--secondary-text-color);
          overflow-wrap: anywhere;
        }

        .protocol-meta {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
          margin-top: 6px;
          font-size: 12px;
        }

        .protocol-time {
          color: var(--secondary-text-color);
          font-size: 12px;
          white-space: nowrap;
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
          .page { padding: 12px; }
          .list, .downlink-layout { grid-template-columns: 1fr; }
          .parameter { grid-template-columns: 1fr; }
        }
      </style>
      <div class="page">
        <header>
          <ha-menu-button class="menu-button"></ha-menu-button>
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
      ${this._renderAdditionalEntitiesDialog()}
      ${this._renderDeviceDiagnosticsDialog()}
      ${this._renderMessagesDialog()}
    `;

    this._updateMenuButton();

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
    this.shadowRoot.querySelectorAll("input[data-tile-value-toggle]").forEach((input) => {
      input.addEventListener("change", (event) => this._toggleTileValue(event.currentTarget));
    });
    this.shadowRoot.querySelectorAll("button[data-tile-value-move]").forEach((button) => {
      button.addEventListener("click", () => this._moveTileValue(button));
    });
    this.shadowRoot.querySelectorAll("button[data-climate-add]").forEach((button) => {
      button.addEventListener("click", () => this._addClimateEntity());
    });
    this.shadowRoot.querySelectorAll("button[data-climate-remove]").forEach((button) => {
      button.addEventListener("click", () => this._removeClimateEntity(Number(button.dataset.climateRemove)));
    });
    this.shadowRoot.querySelector("button[data-additional-entities-open]")?.addEventListener("click", () => {
      this._syncDeviceSettingsForm();
      this._additionalEntitiesDialogOpen = true;
      this._render();
    });
    this.shadowRoot.querySelector("button[data-additional-entities-close]")?.addEventListener("click", () => {
      this._syncClimateEntitiesForm();
      this._additionalEntitiesDialogOpen = false;
      this._render();
    });
    this.shadowRoot
      .querySelector("button[data-device-settings-cancel]")
      ?.addEventListener("click", () => {
        this._deviceSettings = null;
        this._additionalEntitiesDialogOpen = false;
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
      this._profileEditor = { deviceType: this._t("newProfileName"), downlinkParameter: [] };
      this._profileEditorOriginalType = null;
      this._openParameterEditorIndex = null;
      this._render();
    });
    this.shadowRoot.querySelectorAll("button[data-profile-edit-type]").forEach((button) => button.addEventListener("click", () => {
      this._downlinkProfile = button.getAttribute("data-profile-edit-type");
      this._profileEditor = this._cloneProfile(this._selectedDownlinkProfile());
      this._profileEditorOriginalType = this._downlinkProfile;
      this._openParameterEditorIndex = null;
      this._render();
    }));
    this.shadowRoot.querySelectorAll("details[data-profile-type]").forEach((details) => details.addEventListener("toggle", () => {
      if (!details.open) return;
      const deviceType = details.getAttribute("data-profile-type");
      if (this._profileEditorOriginalType === deviceType) return;
      this._downlinkProfile = deviceType;
      this._profileEditorOriginalType = deviceType;
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
    this.shadowRoot.querySelector("button[data-profile-cancel]")?.addEventListener("click", () => { this._profileEditor = null; this._profileEditorOriginalType = null; this._openParameterEditorIndex = null; this._render(); });
    this.shadowRoot.querySelector("button[data-parameter-add]")?.addEventListener("click", () => {
      this._profileEditor.downlinkParameter.push({ name: this._t("newParameter"), type: "number", port: this._profileEditor.port || 1, lengthInByte: 1, multiplyfaktor: 1 }); this._render();
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
    this.shadowRoot.querySelectorAll("button[data-entity-more-info]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this._showEntityMoreInfo(button.getAttribute("data-entity-more-info"));
      });
    });
    this.shadowRoot.querySelectorAll("[data-entity-control]").forEach((control) => {
      const eventName = control.tagName === "BUTTON" ? "click" : "change";
      control.addEventListener(eventName, (event) => this._handleEntityControl(event));
    });
    this.shadowRoot
      .querySelector("button[data-device-diagnostics-close]")
      ?.addEventListener("click", () => {
        this._deviceDiagnostics = null;
        this._render();
      });
    this.shadowRoot.querySelectorAll("[data-device-open]").forEach((card) => {
      card.addEventListener("click", (event) => {
        if (event.target.closest("button, input, select, textarea, a")) {
          return;
        }
        window.location.href = `/config/devices/device/${card.getAttribute("data-device-open")}`;
      });
      card.addEventListener("keydown", (event) => {
        if (event.target.closest("button, input, select, textarea, a")) {
          return;
        }
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
          <div class="card status-card" style="border-top: 4px solid ${this._escape(connection.color || "var(--primary-color)")}" role="button" tabindex="0" data-show-messages data-entry-id="${this._escape(connection.entry_id || "")}" title="${this._t("showRecentMessages")}">
            <h2>${this._escape(connection.name || "LoRaWAN")}</h2>
            <dl>
              <dt>${this._t("connection")}</dt>
              <dd>
                <span class="status">
                  <span class="dot ${connection.connected ? "connected" : connection.last_error ? "error" : ""}"></span>
                  ${connection.connected ? this._t("active") : this._t("disconnected")}
                </span>
              </dd>
              <dt>${this._t("broker")}</dt>
              <dd><code>${this._escape(connection.host || "-")}:${this._escape(connection.port || "-")}</code></dd>
              <dt>${this._t("lastMessage")}</dt>
              <dd>${this._formatDate(connection.last_message_at)}</dd>
              <dt>${this._t("lastTopic")}</dt>
              <dd><code>${this._escape(connection.last_topic || "-")}</code></dd>
              <dt>${this._t("detected")}</dt>
              <dd>${this._formatDetectedNetworks(connection.lns_counts)}</dd>
              <dt>Downlinks</dt>
              <dd>${this._formatDownlinkEvents(connection.downlink_event_counts)}</dd>
              <dt>${this._t("errors")}</dt>
              <dd>${this._escape(connection.last_error || "-")}</dd>
            </dl>
          </div>
          `).join("")}
          <div class="card">
            <h2>Topics</h2>
            <dl>
              ${(this._status.topics?.length
                ? this._status.topics
                : ["v3/+/devices/+/+", "v3/+/devices/+/down/+", "application/+/device/+/event/+", "application/+/device/+/command/down"]
              )
                .map(
                  (topic, index) => `
                    <dt>${["TTN Uplink", "TTN Downlink", "ChirpStack Events", "ChirpStack Downlink"][index] || "MQTT"}</dt>
                    <dd><code>${this._escape(topic)}</code></dd>
                  `
                )
                .join("")}
            </dl>
          </div>
          <div class="card">
            <h2>${this._t("formats")}</h2>
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

    if (this._activeTab === "protocol") {
      return this._renderProtocol();
    }

    const connections = this._status.connections || [];
    return `
      <div class="section">
        ${(connections.length ? connections : [this._status]).map((connection) => `
        <div class="card" style="border-top: 4px solid ${this._escape(connection.color || "var(--primary-color)")}">
          <h2>${this._escape(connection.name || "Uplinks")}</h2>
          <dl>
            <dt>${this._t("status")}</dt>
            <dd>${connection.connected ? this._t("mqttConnected") : this._t("waitingForMqtt")}</dd>
            <dt>Uplinks</dt>
            <dd>${connection.message_count || 0}</dd>
            <dt>${this._t("devices")}</dt>
            <dd>${connection.device_count || 0}</dd>
            <dt>${this._t("entities")}</dt>
            <dd>${connection.entity_count || 0}</dd>
          </dl>
        </div>
        `).join("")}
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
    const base = `${name || this._t("newEntry")} (${this._t("copy")})`;
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
    this._profileEditorOriginalType = null;
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
    const message = this._language() === "de"
      ? `Downlink-Profil „${profile.deviceType}“ wirklich löschen?`
      : `Really delete downlink profile “${profile.deviceType}”?`;
    if (!window.confirm(message)) return;
    try {
      const remaining = configured.filter((item) => item.deviceType !== profile.deviceType);
      if (isBuiltIn) remaining.push({ deviceType: profile.deviceType, _deleted: true });
      await this._hass.callService("lorawan", "configure_downlink_profiles", {
        downlink_profiles: remaining,
      });
      if (this._downlinkProfile === profile.deviceType) this._downlinkProfile = "";
      if (this._profileEditorOriginalType === profile.deviceType) {
        this._profileEditor = null;
        this._profileEditorOriginalType = null;
        this._openParameterEditorIndex = null;
      }
      await this._loadDownlinks();
      this._render();
    } catch (error) { window.alert(`${this._t("profileDeleteFailed")}: ${error.message || error}`); }
  }

  _renderDownlinks() {
    const profiles = (this._downlinks.profiles || []).filter((profile) => profile.deviceType !== "internalBaseDevice");
    const editor = (profile) => `
          <form class="profile-editor" data-profile-editor>
            <label>${this._t("deviceType")}<input name="deviceType" required value="${this._escape(profile.deviceType || "")}" /></label>
            <label>${this._t("sendWithUplink")}<select name="sendWithUplink" data-profile-send-with-uplink><option value="disabled" ${profile.sendWithUplink === "disabled" ? "selected" : ""}>${this._language() === "de" ? "deaktiviert" : "disabled"}</option><option value="enabled" ${profile.sendWithUplink === "enabled" ? "selected" : ""}>${this._language() === "de" ? "aktiviert" : "enabled"}</option><option value="enabled & collect" ${profile.sendWithUplink === "enabled & collect" ? "selected" : ""}>${this._language() === "de" ? "aktiviert und sammeln" : "enabled and collect"}</option></select></label>
            ${profile.sendWithUplink !== "disabled" ? `<label>Port<input name="port" type="number" value="${profile.port || 1}" /></label>
            <label>${this._t("priority")}<input name="priority" value="${this._escape(profile.priority || "NORMAL")}" /></label>
            <label class="checkbox"><input name="confirmed" type="checkbox" ${profile.confirmed ? "checked" : ""} /> ${this._t("confirmed")}</label>` : ""}
            <h3>${this._t("customDownlinkConfig")}</h3>
            <button class="action" type="button" data-parameter-add>${this._t("addParameter")}</button>
            ${(profile.downlinkParameter || []).map((parameter, index) => this._renderParameterEditor(parameter, index, profile)).join("")}
            <div class="actions"><button class="save" type="submit" ${profile.saving ? "disabled" : ""}>${profile.saving ? this._t("saving") : this._t("saveProfile")}</button><button class="action" type="button" data-profile-cancel ${profile.saving ? "disabled" : ""}>${this._t("cancel")}</button></div>
          </form>`;
    return `
      <div class="card">
        <h2>${this._t("deviceProfiles")}</h2>
        <p class="muted">${this._t("profileDescription")}</p>
        <div class="profile-actions"><button class="save" type="button" data-profile-new>${this._t("createProfile")}</button></div>
        ${this._profileEditor && this._profileEditorOriginalType === null ? `<div class="new-profile-editor"><h3>${this._t("newProfile")}</h3>${editor(this._profileEditor)}</div>` : ""}
        <div class="profile-list">${profiles.map((profile) => {
          const editing = this._profileEditor && this._profileEditorOriginalType === profile.deviceType;
          const profileActions = `<div class="actions"><button class="action duplicate" type="button" data-profile-duplicate-type="${this._escape(profile.deviceType)}">${this._t("duplicate")}</button><button class="action danger" type="button" data-profile-delete-type="${this._escape(profile.deviceType)}">${this._t("delete")}</button></div>`;
          return `<details ${editing ? "open" : ""} data-profile-type="${this._escape(profile.deviceType)}"><summary><strong>${this._escape(profile.deviceType)}</strong> <span class="muted">(${(profile.downlinkParameter || []).length} Parameter)</span></summary><div class="profile-content">${editing ? `${editor(this._profileEditor)}${profileActions}` : `<ul class="profile-parameters">${(profile.downlinkParameter || []).map((parameter) => `<li class="profile-parameter"><strong>${this._escape(parameter.name)}</strong> <span class="muted">${this._escape(parameter.type || "number")}${parameter.unit ? ` · ${this._escape(parameter.unit)}` : ""}</span></li>`).join("")}</ul>${profileActions}`}</div></details>`;
        }).join("")}</div>
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
      <label>${this._t("type")}<select name="p${index}type" data-parameter-type="${index}">${["number", "boolean", "button", "ascii", "string"].map((option) => `<option ${type === option ? "selected" : ""}>${option}</option>`).join("")}</select></label>
      <label>Port<input name="p${index}port" type="number" value="${value("port", profile.port || 1)}" /></label>
      <label>${this._t("priority")}<input name="p${index}priority" value="${value("priority", "NORMAL")}" /></label>
      <label class="checkbox"><input name="p${index}confirmed" type="checkbox" ${checked("confirmed")} /> ${this._t("confirmed")}</label>
      ${isValueType ? `<label>${this._t("leading")}<input name="p${index}front" value="${value("front")}" /></label>
      <label>${this._t("trailing")}<input name="p${index}end" value="${value("end")}" /></label>` : ""}
      ${type !== "boolean" && type !== "button" && type !== "string" ? `<label>${this._t("lengthBytes")}<input name="p${index}lengthInByte" type="number" min="1" max="20" value="${value("lengthInByte", 3)}" /></label>` : ""}
      ${type === "boolean" ? `<label>${this._t("onSequence")}<input name="p${index}on" value="${value("on")}" /></label><label>${this._t("offSequence")}<input name="p${index}off" value="${value("off")}" /></label>` : ""}
      ${type === "button" ? `<label>${this._t("clickSequence")}<input name="p${index}onClick" value="${value("onClick")}" /></label>` : ""}
      ${isNumber ? `<label>${this._t("multiplier")}<input name="p${index}multiplyfaktor" type="number" step="any" value="${value("multiplyfaktor", 1)}" /></label>
      <label>${this._t("decimalPlaces")}<input name="p${index}decimalPlaces" type="number" min="0" max="5" value="${value("decimalPlaces", 0)}" /></label>
      <label>${this._t("unit")}<input name="p${index}unit" value="${value("unit")}" /></label>` : ""}
      ${type === "ascii" ? `<label>${this._t("unit")}<input name="p${index}unit" value="${value("unit")}" /></label>` : ""}
      <label>CRC<select name="p${index}crc">${[["noCrc", this._t("noCrc")], ["CRC-8", "CRC-8"], ["KERMIT", "KERMIT"], ["KERMIT.LittleEndian", "KERMIT (Little Endian)"]].map(([option, label]) => `<option value="${option}" ${value("crc", "noCrc") === option ? "selected" : ""}>${label}</option>`).join("")}</select></label>
      ${isNumber ? `<label class="checkbox"><input name="p${index}swap" type="checkbox" ${checked("swap")} /> ${this._t("swapBytes")}</label>
      <label class="checkbox"><input name="p${index}limitMin" data-parameter-visibility="${index}:limitMin" type="checkbox" ${checked("limitMin")} /> ${this._t("limitMinimum")}</label>
      ${parameter.limitMin ? `<label>${this._t("minimumValue")}<input name="p${index}limitMinValue" type="number" step="any" value="${value("limitMinValue", 0)}" /></label>` : ""}
      <label class="checkbox"><input name="p${index}limitMax" data-parameter-visibility="${index}:limitMax" type="checkbox" ${checked("limitMax")} /> ${this._t("limitMaximum")}</label>
      ${parameter.limitMax ? `<label>${this._t("maximumValue")}<input name="p${index}limitMaxValue" type="number" step="any" value="${value("limitMaxValue", 0)}" /></label>` : ""}
      <label class="checkbox"><input name="p${index}withStates" data-parameter-visibility="${index}:withStates" type="checkbox" ${checked("withStates")} /> ${this._t("useStates")}</label>
      ${parameter.withStates ? `<label>${this._t("stateValues")}<input name="p${index}statesValue" value="${value("statesValue")}" /></label>` : ""}` : ""}
    </div><div class="actions"><button class="action duplicate" type="button" data-parameter-duplicate="${index}">${this._t("duplicateParameter")}</button><button class="action danger" type="button" data-parameter-delete="${index}">${this._t("deleteParameter")}</button></div></details>`;
  }

  _renderDownlinkParameter(parameter) {
    const name = this._escape(parameter.name);
    if (parameter.type === "button") {
      return `<div class="parameter"><div><strong>${name}</strong></div><button type="submit" name="parameter_name" value="${name}">${this._t("execute")}</button></div>`;
    }
    if (parameter.type === "boolean") {
      return `<div class="parameter"><div><strong>${name}</strong></div><label class="checkbox"><input type="checkbox" name="${name}" /> ${this._t("enabled")}</label></div>`;
    }
    const states = this._stateOptions(parameter);
    if (states.length) {
      return `<div class="parameter"><label><strong>${name}</strong>${parameter.unit ? ` (${this._escape(parameter.unit)})` : ""}</label><div class="actions"><select name="${name}">${states.map(([rawValue, label]) => `<option value="${this._escape(rawValue)}">${this._escape(label)} (${this._escape(rawValue)})</option>`).join("")}</select><button type="submit" name="parameter_name" value="${name}">${this._t("send")}</button></div></div>`;
    }
    const decimalPlaces = Math.max(0, Number(parameter.decimalPlaces || 0));
    const step = decimalPlaces === 0 ? "1" : String(10 ** -decimalPlaces);
    return `<div class="parameter"><label><strong>${name}</strong>${parameter.unit ? ` (${this._escape(parameter.unit)})` : ""}</label><div class="actions"><input name="${name}" type="number" step="${step}" ${parameter.limitMin ? `min="${parameter.limitMinValue}"` : ""} ${parameter.limitMax ? `max="${parameter.limitMaxValue}"` : ""} /><button type="submit" name="parameter_name" value="${name}">${this._t("send")}</button></div></div>`;
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
      window.alert(`${this._t("downlinkSent")}: ${result.payload_hex}`);
    } catch (error) { window.alert(`${this._t("downlinkSendFailed")}: ${error.message || error}`); }
  }

  async _saveProfile(event) {
    event.preventDefault();
    if (this._profileEditor?.saving) return;
    const data = new FormData(event.currentTarget);
    const controls = event.currentTarget.querySelectorAll("input, select, button");
    this._profileEditor.saving = true;
    controls.forEach((control) => { control.disabled = true; });
    const saveButton = event.currentTarget.querySelector('button[type="submit"]');
    if (saveButton) saveButton.textContent = this._t("saving");
    try {
      const old = this._cloneProfile(this._profileEditor);
      if (old) delete old.saving;
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
      delete profile.saving;
      if (sendWithUplink !== "disabled") {
        profile.port = number("port", old.port || 1);
        profile.priority = String(data.get("priority") || "NORMAL");
        profile.confirmed = data.get("confirmed") === "on";
      }
      if (!profile.deviceType || !Array.isArray(profile.downlinkParameter)) throw new Error("deviceType und downlinkParameter sind erforderlich");
      const current = (this._downlinks.configured_profiles || []).filter((item) => item.deviceType !== old.deviceType && item.deviceType !== profile.deviceType);
      current.push(profile);
      await this._hass.callService("lorawan", "configure_downlink_profiles", { downlink_profiles: current });
      await this._loadDownlinks();
      this._profileEditor = null;
      this._profileEditorOriginalType = null;
      this._downlinkProfile = profile.deviceType;
      this._render();
    } catch (error) {
      this._profileEditor.saving = false;
      controls.forEach((control) => { control.disabled = false; });
      if (saveButton) saveButton.textContent = this._t("saveProfile");
      window.alert(this._t("saveFailed"));
    }
  }

  async _handleDeviceSettings(button) {
    this._additionalEntitiesDialogOpen = false;
    this._deviceSettings = {
      devEui: button.getAttribute("data-device-settings"),
      entryId: button.getAttribute("data-entry-id") || "",
      name: button.getAttribute("data-device-name") || this._t("device"),
      hours: button.getAttribute("data-device-hours") || "25",
      raw: button.getAttribute("data-device-raw") === "true",
      remaining: button.getAttribute("data-device-remaining") === "true",
      availableEntities: JSON.parse(button.getAttribute("data-device-entities") || "[]"),
      tileValueKeys: JSON.parse(button.getAttribute("data-device-tile-value-keys") || "[]"),
      climateEntities: JSON.parse(button.getAttribute("data-device-climate-entities") || "[]"),
    };
    this._render();
  }

  async _handleDeviceSettingsSubmit(event) {
    event.preventDefault();
    if (this._deviceSettings?.saving) return;
    this._syncDeviceSettingsForm();
    const formData = new FormData(event.currentTarget);
    const hours = Number(formData.get("offline_after_hours"));
    if (!Number.isInteger(hours) || hours < 1 || hours > 8760) {
      window.alert(this._t("invalidHours"));
      return;
    }
    this._deviceSettings.saving = true;
    const controls = event.currentTarget.querySelectorAll("input, button");
    controls.forEach((control) => { control.disabled = true; });
    const saveButton = event.currentTarget.querySelector('button[type="submit"]');
    if (saveButton) saveButton.textContent = this._t("saving");
    try {
      await this._hass.callService("lorawan", "configure_device", {
        dev_eui: this._deviceSettings.devEui,
        entry_id: this._deviceSettings.entryId,
        offline_after_hours: hours,
        create_raw_sensors: formData.get("create_raw_sensors") === "on",
        create_remaining_sensors: formData.get("create_remaining_sensors") === "on",
        device_tile_values: this._deviceSettings.tileValueKeys,
        device_climate_entities: this._deviceSettings.climateEntities,
      });
      this._deviceSettings = null;
      await this._loadDevices();
      await this._loadStatus();
    } catch (error) {
      this._deviceSettings.saving = false;
      controls.forEach((control) => { control.disabled = false; });
      if (saveButton) saveButton.textContent = this._t("save");
      window.alert(this._t("saveFailed"));
    }
  }

  _orderedTileEntities(settings) {
    const entitiesById = new Map(settings.availableEntities.map((entity) => [entity.entity_id, entity]));
    const selected = settings.tileValueKeys.map((entityId) => entitiesById.get(entityId)).filter(Boolean);
    const selectedIds = new Set(settings.tileValueKeys);
    return selected.concat(settings.availableEntities.filter((entity) => !selectedIds.has(entity.entity_id)));
  }

  _toggleTileValue(input) {
    this._syncDeviceSettingsForm();
    const entityId = input.value;
    const keys = this._deviceSettings?.tileValueKeys || [];
    this._deviceSettings.tileValueKeys = input.checked
      ? keys.includes(entityId) ? keys : [...keys, entityId]
      : keys.filter((key) => key !== entityId);
    this._render();
  }

  _moveTileValue(button) {
    this._syncDeviceSettingsForm();
    const entityId = button.getAttribute("data-tile-value-move");
    const direction = button.getAttribute("data-move-direction");
    const keys = [...(this._deviceSettings?.tileValueKeys || [])];
    const index = keys.indexOf(entityId);
    const target = direction === "up" ? index - 1 : index + 1;
    if (index < 0 || target < 0 || target >= keys.length) return;
    [keys[index], keys[target]] = [keys[target], keys[index]];
    this._deviceSettings.tileValueKeys = keys;
    this._render();
  }

  _syncDeviceSettingsForm() {
    const form = this.shadowRoot.querySelector("form[data-device-settings-form]");
    if (!form || !this._deviceSettings) return;
    const data = new FormData(form);
    this._deviceSettings.hours = String(data.get("offline_after_hours") || this._deviceSettings.hours);
    this._deviceSettings.raw = data.get("create_raw_sensors") === "on";
    this._deviceSettings.remaining = data.get("create_remaining_sensors") === "on";
    this._syncClimateEntitiesForm();
  }

  _syncClimateEntitiesForm() {
    const form = this.shadowRoot.querySelector("form[data-climate-entities-form]");
    if (!form || !this._deviceSettings) return;
    const data = new FormData(form);
    this._deviceSettings.climateEntities = this._deviceSettings.climateEntities.map((climate, index) => ({
      ...climate,
      name: String(data.get(`climate_${index}_name`) || "Thermostat"),
      current_temperature_entity_id: String(data.get(`climate_${index}_current`) || ""),
      target_temperature_state_entity_id: String(data.get(`climate_${index}_target_state`) || ""),
      target_temperature_command_entity_id: String(data.get(`climate_${index}_target_command`) || ""),
      hvac_mode_state_entity_id: String(data.get(`climate_${index}_mode_state`) || ""),
      hvac_mode_command_entity_id: String(data.get(`climate_${index}_mode_command`) || ""),
    }));
  }

  _addClimateEntity() {
    this._syncClimateEntitiesForm();
    this._deviceSettings.climateEntities.push({
      id: `climate_${Date.now()}`,
      name: "Thermostat",
      current_temperature_entity_id: "",
      target_temperature_state_entity_id: "",
      target_temperature_command_entity_id: "",
      hvac_mode_state_entity_id: "",
      hvac_mode_command_entity_id: "",
    });
    this._render();
  }

  _removeClimateEntity(index) {
    this._syncClimateEntitiesForm();
    const [removedClimate] = this._deviceSettings.climateEntities.splice(index, 1);
    if (removedClimate?.id) {
      const cleanDevEui = this._deviceSettings.devEui.replace(/[:-]/g, "").toUpperCase();
      const uniqueId = `${this._deviceSettings.entryId}_${cleanDevEui}_climate_${removedClimate.id}`;
      const removedEntityIds = new Set(
        this._deviceSettings.availableEntities
          .filter((entity) => entity.unique_id === uniqueId)
          .map((entity) => entity.entity_id)
      );
      this._deviceSettings.availableEntities = this._deviceSettings.availableEntities
        .filter((entity) => !removedEntityIds.has(entity.entity_id));
      this._deviceSettings.tileValueKeys = this._deviceSettings.tileValueKeys
        .filter((entityId) => !removedEntityIds.has(entityId));
    }
    this._render();
  }

  _climateEntityOptions(entities, selected, domains) {
    const options = entities.filter((entity) => domains.includes(entity.domain));
    return `<option value="">${this._t("notAssigned")}</option>${options.map((entity) =>
      `<option value="${this._escape(entity.entity_id)}" ${entity.entity_id === selected ? "selected" : ""}>${this._escape(entity.name)} (${this._escape(entity.entity_id)})</option>`
    ).join("")}`;
  }

  async _showDeviceDiagnostics(button) {
    const devEui = button.getAttribute("data-device-json");
    this._deviceDiagnostics = {
      name: button.getAttribute("data-device-name") || this._t("device"),
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
    const orderedEntities = this._orderedTileEntities(settings);
    const selectedCount = settings.tileValueKeys.length;
    return `
      <div class="dialog-backdrop" role="presentation">
        <div class="dialog" role="dialog" aria-modal="true" aria-label="${this._t("deviceSettings")}">
          <h2>${this._escape(settings.name)}</h2>
          <form data-device-settings-form>
            <label>
              ${this._t("offlineAfterHours")}
              <input name="offline_after_hours" type="number" min="1" max="8760" required value="${this._escape(settings.hours)}" />
            </label>
            <label class="checkbox">
              <input name="create_raw_sensors" type="checkbox" ${settings.raw ? "checked" : ""} />
              ${this._t("enableRawDiagnostics")}
            </label>
            <label class="checkbox">
              <input name="create_remaining_sensors" type="checkbox" ${settings.remaining ? "checked" : ""} />
              ${this._t("enableRemainingDiagnostics")}
            </label>
            <div class="value-selection">
              <strong>${this._t("tileValues")}</strong>
              ${orderedEntities.length ? orderedEntities.map((entity) => {
                const selectedIndex = settings.tileValueKeys.indexOf(entity.entity_id);
                return `<div class="value-selection-row">
                  <label class="checkbox">
                    <input name="tile_values" type="checkbox" value="${this._escape(entity.entity_id)}" data-tile-value-toggle ${selectedIndex >= 0 ? "checked" : ""} />
                    ${this._escape(entity.name)}
                  </label>
                  ${selectedIndex >= 0 ? `<span class="value-order-actions">
                    <button class="value-order-button" type="button" title="${this._t("moveUp")}" data-tile-value-move="${this._escape(entity.entity_id)}" data-move-direction="up" ${selectedIndex === 0 ? "disabled" : ""}>↑</button>
                    <button class="value-order-button" type="button" title="${this._t("moveDown")}" data-tile-value-move="${this._escape(entity.entity_id)}" data-move-direction="down" ${selectedIndex === selectedCount - 1 ? "disabled" : ""}>↓</button>
                  </span>` : ""}
                </div>`;
              }).join("") : `<span class="muted">${this._t("noActiveEntities")}</span>`}
            </div>
            <div class="settings-subsection">
              <strong>${this._t("additionalEntities")}</strong>
              <span class="muted">${settings.climateEntities.length
                ? `${settings.climateEntities.length} ${settings.climateEntities.length === 1 ? this._t("climateEntity") : this._t("climateEntities")} ${this._t("configured")}`
                : this._t("noAdditionalEntities")}</span>
              <button type="button" data-additional-entities-open>${this._t("configure")}</button>
            </div>
            <div class="actions">
              <button class="save" type="submit" ${settings.saving ? "disabled" : ""}>${settings.saving ? this._t("saving") : this._t("save")}</button>
              <button type="button" data-device-settings-cancel ${settings.saving ? "disabled" : ""}>${this._t("cancel")}</button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  _renderAdditionalEntitiesDialog() {
    const settings = this._deviceSettings;
    if (!settings || !this._additionalEntitiesDialogOpen) return "";
    return `
      <div class="dialog-backdrop secondary" role="presentation">
        <div class="dialog additional-entities-dialog" role="dialog" aria-modal="true" aria-label="${this._t("additionalEntities")}">
          <h2>${this._t("additionalEntities")}</h2>
          <form data-climate-entities-form>
            <div class="value-selection">
              <strong>${this._t("compositeClimate")}</strong>
              ${(settings.climateEntities || []).map((climate, index) => `<fieldset>
                <legend>Climate ${index + 1}</legend>
                <label>Name
                  <input name="climate_${index}_name" type="text" required value="${this._escape(climate.name || "Thermostat")}" />
                </label>
                <label>${this._t("currentTemperature")}
                  <select name="climate_${index}_current">${this._climateEntityOptions(settings.availableEntities, climate.current_temperature_entity_id, ["sensor", "number"])}</select>
                </label>
                <label>${this._t("readTargetTemperature")}
                  <select name="climate_${index}_target_state">${this._climateEntityOptions(settings.availableEntities, climate.target_temperature_state_entity_id, ["sensor", "number"])}</select>
                </label>
                <label>${this._t("setTargetTemperature")}
                  <select name="climate_${index}_target_command">${this._climateEntityOptions(settings.availableEntities, climate.target_temperature_command_entity_id, ["number"])}</select>
                </label>
                <label>${this._t("readHvacMode")}
                  <select name="climate_${index}_mode_state">${this._climateEntityOptions(settings.availableEntities, climate.hvac_mode_state_entity_id, ["sensor", "select", "switch"])}</select>
                </label>
                <label>${this._t("setHvacMode")}
                  <select name="climate_${index}_mode_command">${this._climateEntityOptions(settings.availableEntities, climate.hvac_mode_command_entity_id, ["select", "switch"])}</select>
                </label>
                <button class="action danger" type="button" data-climate-remove="${index}">${this._t("removeClimate")}</button>
              </fieldset>`).join("")}
              <button type="button" data-climate-add>${this._t("addAndAssignEntity")}</button>
            </div>
            <div class="actions">
              <button class="save" type="button" data-additional-entities-close>${this._t("done")}</button>
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
        <div class="dialog" role="dialog" aria-modal="true" aria-label="${this._t("recentMessages")}">
          <h2>${this._t("recentMessages")}</h2>
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
          <h3>${this._t("direction")}</h3>
          <div>${this._selectedMessage.direction === "downlink" ? "Downlink · " + this._escape(this._selectedMessage.event || "event") : "Uplink"}</div>
          <h3>Payload</h3>
          <pre class="payload">${this._escape(this._selectedMessage.payload)}</pre>
          <div class="actions">
            <button type="button" data-messages-close>${this._t("close")}</button>
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
      <pre class="payload">${value === null ? this._t("diagnosticUnavailable") : this._escape(JSON.stringify(value, null, 2))}</pre>
    `;
    return `
      <div class="dialog-backdrop" role="presentation">
        <div class="dialog" role="dialog" aria-modal="true" aria-label="${this._t("showMqttData")}">
          <h2>${this._escape(diagnostics.name)}</h2>
          ${diagnostics.loading ? this._t("dataLoading") : diagnostics.error ? this._t("dataLoadFailed") : `
            ${renderPayload("Raw JSON", diagnostics.raw)}
            ${renderPayload(this._t("moreMqttData"), diagnostics.remaining)}
          `}
          <div class="actions">
            <button type="button" data-device-diagnostics-close>${this._t("close")}</button>
          </div>
        </div>
      </div>
    `;
  }

  _renderDevices() {
    if (this._devicesError) {
      return `
        <div class="device-card">
          <div>
            <div class="device-name">${this._t("deviceLoadFailed")}</div>
            <div class="muted">${this._escape(this._devicesError)}</div>
          </div>
        </div>
      `;
    }
    if (!this._devices.length) {
      return `
        <div class="device-card">
          <div>
            <div class="device-name">${this._t("noDevices")}</div>
            <div class="muted">${this._t("devicesAfterUplink")}</div>
          </div>
        </div>
      `;
    }

    return this._devices
      .map((device) => {
        const identifier = device.identifiers?.[0] || "-";
        const subtitle = device.model || device.manufacturer || "LoRaWAN";
        const indicators = this._deviceIndicators(device);
        const openAttributes = device.id
          ? `role="button" tabindex="0" data-device-open="${this._escape(device.id)}"`
          : "";
        return `
          <div class="device-card" style="border-top: 4px solid ${this._escape(device.connection_color || "var(--primary-color)")}" ${openAttributes}>
            <div>
              <div class="device-card-header">
                <div class="device-name">${this._escape(device.name)}</div>
                <span class="device-status status" title="${device.online ? this._t("online") : this._t("offline")}">
                  <span class="dot ${device.online ? "connected" : "error"}"></span>${device.online ? this._t("online") : this._t("offline")}
                </span>
                <span class="last-uplink">${this._t("lastUplink")}: ${this._escape(this._formatDate(device.last_uplink_at))}</span>
              </div>
              <div class="muted">${this._escape(subtitle)}</div>
              ${device.application_name ? `<div class="muted">${this._t("application")}: ${this._escape(device.application_name)}</div>` : ""}
              <div class="device-meta-row">
                <div class="device-eui muted">DevEUI<br /><code>${this._escape(identifier)}</code></div>
                ${indicators.length ? `<div class="device-indicators">${indicators.map((indicator) => `
                  <span class="device-indicator ${indicator.className || ""}" title="${this._escape(indicator.title)}">
                    <ha-icon icon="${this._escape(indicator.icon)}"></ha-icon>${indicator.text ? this._escape(indicator.text) : ""}
                  </span>
                `).join("")}</div>` : ""}
              </div>
              <div class="diagnostics">
                ${device.connection_name ? `<span class="tag connection-tag" style="${this._connectionTagStyle(device.connection_color)}">${this._escape(device.connection_name)}</span>` : ""}
                ${device.create_raw_sensors ? '<span class="tag">Raw</span>' : ""}
                ${device.create_remaining_sensors ? '<span class="tag">Rest</span>' : ""}
              </div>
            </div>
            ${device.tile_values?.length ? `<div class="tile-values">${device.tile_values.map((value) => `
              <div class="tile-value">
                ${this._renderTileEntityName(value)}
                ${this._renderTileEntityValue(value)}
              </div>
            `).join("")}</div>` : ""}
            <button
              class="icon-button device-settings"
              type="button"
              title="${this._t("deviceSettings")}"
              data-device-settings="${this._escape(identifier)}"
              data-entry-id="${this._escape(device.entry_id || "")}"
              data-device-name="${this._escape(device.name)}"
              data-device-hours="${device.offline_after_hours || device.offline_after_default_hours || 25}"
              data-device-raw="${Boolean(device.create_raw_sensors)}"
              data-device-remaining="${Boolean(device.create_remaining_sensors)}"
              data-device-entities="${this._escape(JSON.stringify(device.available_entities || []))}"
              data-device-tile-value-keys="${this._escape(JSON.stringify(device.tile_value_keys || []))}"
              data-device-climate-entities="${this._escape(JSON.stringify(device.climate_entities || []))}"
            >⚙</button>
            ${device.create_raw_sensors || device.create_remaining_sensors ? `<button
              class="icon-button device-json"
              type="button"
              title="${this._t("showMqttData")}"
              data-device-json="${this._escape(identifier)}"
              data-device-name="${this._escape(device.name)}"
            >{ }</button>` : ""}
          </div>
        `;
      })
      .join("");
  }

  _renderProtocol() {
    const events = this._status.protocol_events || [];
    if (!events.length) {
      return `<div class="card"><h2>${this._t("protocol")}</h2><div class="muted">${this._t("noEvents")}</div></div>`;
    }
    return `<div class="protocol-list">${events.map((event) => `
      <div class="protocol-event ${this._escape(event.level || "info")}" style="border-left: 4px solid ${this._escape(event.connection_color || "var(--primary-color)")}">
        <span class="protocol-level" style="background: ${this._escape(event.connection_color || "var(--primary-color)")}"></span>
        <div>
          <div class="protocol-title">${this._escape(event.title || this._t("event"))}</div>
          <div class="protocol-message">${this._escape(event.message || "")}</div>
          <div class="protocol-meta">
            <span class="tag">${this._escape(this._protocolCategory(event.category))}</span>
            ${event.connection_name ? `<span class="tag">${this._escape(event.connection_name)}</span>` : ""}
            ${event.application_name ? `<span class="tag">${this._t("application")}: ${this._escape(event.application_name)}</span>` : ""}
            ${event.dev_eui ? `<span class="tag"><code>${this._escape(event.dev_eui)}</code></span>` : ""}
          </div>
        </div>
        <time class="protocol-time" datetime="${this._escape(event.timestamp || "")}">${this._escape(this._formatDate(event.timestamp))}</time>
      </div>
    `).join("")}</div>`;
  }

  _protocolCategory(category) {
    return { connection: "LNS / MQTT", device: this._t("device"), downlink: "Downlink" }[category] || "System";
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
    return detected.length ? detected.join(", ") : this._t("noMessages");
  }

  _formatDownlinkEvents(counts) {
    const events = Object.entries(counts || {}).filter(([, count]) => count > 0);
    return events.length
      ? events.map(([event, count]) => `${this._escape(event)} ${count}`).join(", ")
      : this._t("noConfirmation");
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
      this._devicesError = null;
      if (this._activeTab !== "downlinks" && !this._deviceSettings) this._render();
    } catch (error) {
      this._devices = [];
      this._devicesError = error?.message || String(error);
      console.error("Could not load LoRaWAN devices", error);
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
    return new Date(value).toLocaleString(this._hass?.locale?.language || this._hass?.language || undefined);
  }

  _formatTileValue(value) {
    const domain = value.domain || String(value.entity_id || "").split(".")[0];
    if (domain === "button") return this._t("press");
    if (domain === "text" && ["", "unknown", "unavailable"].includes(String(value.state ?? ""))) {
      return this._t("emptyValue");
    }
    if (domain === "switch") {
      if (value.state === "on") return this._t("on");
      if (value.state === "off") return this._t("off");
    }
    if (domain === "binary_sensor") {
      if (value.state === "on") return this._binarySensorLabel(value.device_class, true);
      if (value.state === "off") return this._binarySensorLabel(value.device_class, false);
    }
    const display = value.state === null || value.state === undefined
      ? "-"
      : typeof value.state === "object" ? JSON.stringify(value.state) : String(value.state);
    return `${display}${value.unit ? ` ${value.unit}` : ""}`;
  }

  _renderTileControl(value) {
    const entityId = this._escape(value.entity_id);
    const domain = value.domain || String(value.entity_id || "").split(".")[0];
    if (domain === "button") {
      return `<button class="tile-control-button" type="button" data-entity-control="${entityId}" data-control-domain="button">${this._t("press")}</button>`;
    }
    if (domain === "number") {
      return `<span class="tile-control-wrap"><input class="tile-control" type="number" value="${this._escape(value.state)}" ${value.min !== null ? `min="${this._escape(value.min)}"` : ""} ${value.max !== null ? `max="${this._escape(value.max)}"` : ""} ${value.step !== null ? `step="${this._escape(value.step)}"` : ""} data-entity-control="${entityId}" data-control-domain="number" />${value.unit ? `<span class="tile-control-unit">${this._escape(value.unit)}</span>` : ""}</span>`;
    }
    if (domain === "text") {
      return `<input class="tile-control tile-text-control" type="text" value="${["unknown", "unavailable"].includes(String(value.state)) ? "" : this._escape(value.state)}" data-entity-control="${entityId}" data-control-domain="text" />`;
    }
    if (domain === "select") {
      return `<select class="tile-control" data-entity-control="${entityId}" data-control-domain="select">${(value.options || []).map((option) => `<option value="${this._escape(option)}" ${option === value.state ? "selected" : ""}>${this._escape(option)}</option>`).join("")}</select>`;
    }
    if (domain === "switch") {
      return `<input class="tile-switch-control" type="checkbox" ${value.state === "on" ? "checked" : ""} data-entity-control="${entityId}" data-control-domain="switch" />`;
    }
    if (domain === "climate") {
      if (value.target_temperature !== null || (Number(value.supported_features) & 1)) {
        return `<span class="tile-control-wrap"><input class="tile-control" type="number" value="${value.target_temperature !== null ? this._escape(value.target_temperature) : ""}" ${value.min !== null ? `min="${this._escape(value.min)}"` : ""} ${value.max !== null ? `max="${this._escape(value.max)}"` : ""} ${value.step !== null ? `step="${this._escape(value.step)}"` : ""} data-entity-control="${entityId}" data-control-domain="climate" /><span class="tile-control-unit">°C</span></span>`;
      }
      return `<button class="tile-read-value" type="button" data-entity-more-info="${entityId}">${value.current_temperature !== null ? `${this._escape(value.current_temperature)} °C` : this._t("openClimate")}</button>`;
    }
    return `<button class="tile-read-value" type="button" data-entity-more-info="${entityId}">${this._escape(this._formatTileValue(value))}</button>`;
  }

  _renderTileEntityName(value) {
    const entityId = this._escape(value.entity_id);
    const climateIcon = value.domain === "climate"
      ? '<ha-icon icon="mdi:thermostat"></ha-icon>'
      : "";
    return `<button class="tile-entity-name" type="button" data-entity-more-info="${entityId}" title="${this._escape(value.name)} ${this._t("open")}">${climateIcon}${this._escape(value.name)}</button>`;
  }

  _renderTileEntityValue(value) {
    if (value.domain !== "climate") return this._renderTileControl(value);
    const current = value.current_temperature;
    const target = value.target_temperature;
    const parts = [];
    if (current !== null && current !== undefined) parts.push(`${this._t("currentShort")} ${this._escape(current)} °C`);
    if (target !== null && target !== undefined) parts.push(`${this._t("targetShort")} ${this._escape(target)} °C`);
    return `<button class="tile-read-value climate-summary" type="button" data-entity-more-info="${this._escape(value.entity_id)}">${parts.length ? parts.join(" · ") : this._t("openClimate")}</button>`;
  }

  async _handleEntityControl(event) {
    event.stopPropagation();
    const control = event.currentTarget;
    const entityId = control.getAttribute("data-entity-control");
    const domain = control.getAttribute("data-control-domain");
    if (!entityId || !domain) return;
    const originalText = control.textContent;
    control.disabled = true;
    if (domain === "button") {
      control.textContent = this._t("sending");
      control.classList.add("sending");
    }
    try {
      if (domain === "button") await this._hass.callService("button", "press", { entity_id: entityId });
      if (domain === "number") await this._hass.callService("number", "set_value", { entity_id: entityId, value: Number(control.value) });
      if (domain === "text") await this._hass.callService("text", "set_value", { entity_id: entityId, value: control.value });
      if (domain === "select") await this._hass.callService("select", "select_option", { entity_id: entityId, option: control.value });
      if (domain === "switch") await this._hass.callService("switch", control.checked ? "turn_on" : "turn_off", { entity_id: entityId });
      if (domain === "climate") await this._hass.callService("climate", "set_temperature", { entity_id: entityId, temperature: Number(control.value) });
      if (domain === "button") {
        control.classList.remove("sending");
        control.classList.add("success");
        control.textContent = this._t("sent");
        setTimeout(() => this._loadDevices(), 1400);
        return;
      }
      await this._loadDevices();
    } catch (error) {
      if (domain === "button") {
        control.classList.remove("sending");
        control.classList.add("failed");
        control.textContent = this._t("failed");
        setTimeout(() => this._loadDevices(), 1800);
        return;
      }
      window.alert(this._t("writeFailed"));
      await this._loadDevices();
    } finally {
      if (domain !== "button") {
        control.disabled = false;
        control.textContent = originalText;
      }
    }
  }

  _showEntityMoreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(new CustomEvent("hass-more-info", {
      detail: { entityId },
      bubbles: true,
      composed: true,
    }));
  }

  _binarySensorLabel(deviceClass, active) {
    const labels = {
      door: [this._t("closed"), this._t("opened")],
      garage_door: [this._t("closed"), this._t("opened")],
      opening: [this._t("closed"), this._t("opened")],
      window: [this._t("closed"), this._t("opened")],
      lock: [this._t("locked"), this._t("unlocked")],
      motion: [this._t("idle"), this._t("motionDetected")],
      occupancy: [this._t("clear"), this._t("occupied")],
      problem: ["OK", "Problem"],
      safety: [this._t("safe"), this._t("unsafe")],
      smoke: [this._t("noSmoke"), this._t("smokeDetected")],
    };
    return (labels[String(deviceClass || "").toLowerCase()] || [this._t("off"), this._t("on")])[active ? 1 : 0];
  }

  _deviceIndicators(device) {
    const entities = device.available_entities || [];
    const deviceHint = `${device.name || ""} ${device.model || ""} ${device.manufacturer || ""}`
      .toLowerCase()
      .replaceAll(/[^a-z0-9]/g, "");
    const normalized = entities.map((entity) => ({
      ...entity,
      hint: `${entity.entity_id || ""} ${entity.name || ""}`.toLowerCase().replaceAll(/[^a-z0-9]/g, ""),
      deviceClass: String(entity.device_class || "").toLowerCase(),
    }));
    const indicators = [];
    const battery = normalized.find((entity) =>
      entity.hint.includes("batterypercent") || entity.hint.includes("batterypercentage")
    ) || normalized.find((entity) =>
      entity.deviceClass === "battery" || entity.hint.includes("batterylevel")
    );
    if (battery) {
      const percent = Number.parseFloat(String(battery.state).replace(",", "."));
      if (Number.isFinite(percent)) {
        indicators.push({
          icon: percent < 15 ? "mdi:battery-alert" : "mdi:battery",
          text: `${Math.round(percent)} %`,
          title: `${this._t("battery")}: ${percent} %`,
          className: percent < 15 ? "low-battery" : "",
        });
      }
    }

    const isContact = (entity) =>
      ["door", "window", "opening", "garage_door"].includes(entity.deviceClass) ||
      entity.hint.includes("contact") || entity.hint.includes("open");
    const contactTypes = [
      { match: (entity) => entity.deviceClass === "garage_door" || entity.hint.includes("garage") || (deviceHint.includes("garage") && isContact(entity)), type: "garage", label: this._t("garageDoor") },
      { match: (entity) => entity.deviceClass === "window" || entity.hint.includes("openwindow"), type: "window", label: this._t("window") },
      { match: (entity) => entity.deviceClass === "door" || entity.hint.includes("opendoor"), type: "door", label: this._t("door") },
      { match: isContact, type: "contact", label: this._t("contact") },
    ];
    for (const contactType of contactTypes) {
      const entity = normalized.find(contactType.match);
      if (!entity) continue;
      const open = this._isOpenState(entity.state);
      const icons = contactType.type === "garage"
        ? ["mdi:garage", "mdi:garage-open"]
        : contactType.type === "window"
          ? ["mdi:window-closed", "mdi:window-open"]
          : contactType.type === "door"
            ? ["mdi:door-closed", "mdi:door-open"]
            : ["mdi:door-closed", "mdi:door-open"];
      indicators.push({
        icon: icons[open ? 1 : 0],
        title: `${contactType.label}: ${open ? this._t("opened") : this._t("closed")}`,
      });
      break;
    }
    return indicators;
  }

  _isOpenState(value) {
    return ["on", "open", "opened", "true", "1", "yes", "offen", "geöffnet"].includes(
      String(value ?? "").trim().toLowerCase()
    );
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
