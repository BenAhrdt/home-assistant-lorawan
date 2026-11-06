"""Stable automation keys mapped to current registered control entity IDs."""
from collections import defaultdict
import re

CONTROL_DOMAINS = {
    "number", "select", "switch", "button", "text", "climate", "cover",
    "light", "humidifier", "lock", "lawn_mower", "vacuum",
}


def control_key(name: str) -> str:
    """Normalize technical profile names, independently of HA display names."""
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return re.sub(r"[^a-z0-9]+", "_", name.casefold()).strip("_")


def control_references(runtime, dev_eui, device_id, entries) -> dict[str, str]:
    """Resolve only this entry/device; omit disabled or ambiguous controls.

    Profile controls use normalized technical parameter names. Other writable
    integration entities use their stable unique-ID suffix, including domain.
    Entity IDs and friendly names are never used to derive the automation key.
    """
    candidates = defaultdict(list)
    prefix = f"{runtime.entry.entry_id}_{dev_eui}_"
    for entity in entries:
        domain = entity.entity_id.partition(".")[0]
        if (entity.platform != "lorawan" or entity.config_entry_id != runtime.entry.entry_id
                or entity.device_id != device_id or entity.disabled_by is not None
                or domain not in CONTROL_DOMAINS or not entity.unique_id.startswith(prefix)):
            continue
        descriptor = runtime.downlink_controls.get(entity.unique_id)
        if descriptor is not None:
            if descriptor["device"].dev_eui != dev_eui:
                continue
            parameter = descriptor["parameter"]
            key = control_key(str(parameter.get("automation_key") or parameter.get("name", "")))
        else:
            # Stale downlink registry entries must not become callable targets.
            suffix = entity.unique_id[len(prefix):]
            if suffix.startswith("downlink_"):
                continue
            key = control_key(suffix if suffix.startswith(f"{domain}_") else f"{domain}_{suffix}")
        if key:
            candidates[key].append(entity.entity_id)
    return {key: values[0] for key, values in sorted(candidates.items()) if len(values) == 1}
