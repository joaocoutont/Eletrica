import os
import shutil
import json

try:
    import tomllib
except Exception:
    tomllib = None


WORKBENCH_DIR = os.path.dirname(os.path.dirname(__file__))
LIBRARY_DIR = os.path.join(WORKBENCH_DIR, "Library")
LIBRARY_3D_DIR = os.path.join(LIBRARY_DIR, "3D")
CATALOG_DIR = os.path.join(LIBRARY_DIR, "FamilyCatalog")
CATALOG_PATH = os.path.join(CATALOG_DIR, "families.toml")


DEFAULT_SOCKET_FAMILIES = [
    {
        "id": "tomada_simples_10a",
        "name": "Tomada Simples 10A",
        "category": "Tomada",
        "discipline": "Eletrica",
        "ifc_class": "IfcFlowTerminal",
        "source_3d": "Tomadas/Tomada_Simples_10A.FCStd",
        "source_2d": "",
        "modules": "1 Modulo",
        "amperage": "10A",
        "voltage": "127V",
        "power": 100.0,
        "apparent_power_va": 100.0,
        "active_power_w": 100.0,
        "power_factor": 1.0,
        "demand_factor": 1.0,
        "phase": "R",
        "load_classification": "TUG",
        "socket_application": "Predial",
        "ip_rating": "IP20",
        "electrical_standard": "NBR 5410",
        "height_type": "Media (1100mm)",
        "mounting_height": 1100.0,
        "manufacturer": "",
        "model": "",
        "catalog_code": "",
        "description": "Tomada padrao da biblioteca Eletrica.",
    },
    {
        "id": "tomada_simples_20a",
        "name": "Tomada Simples 20A",
        "category": "Tomada",
        "discipline": "Eletrica",
        "ifc_class": "IfcFlowTerminal",
        "source_3d": "Tomadas/Tomada_Simples_20A.FCStd",
        "source_2d": "",
        "modules": "1 Modulo",
        "amperage": "20A",
        "voltage": "127V",
        "power": 600.0,
        "apparent_power_va": 600.0,
        "active_power_w": 600.0,
        "power_factor": 1.0,
        "demand_factor": 1.0,
        "phase": "R",
        "load_classification": "TUG",
        "socket_application": "Predial",
        "ip_rating": "IP20",
        "electrical_standard": "NBR 5410",
        "height_type": "Media (1100mm)",
        "mounting_height": 1100.0,
        "manufacturer": "",
        "model": "",
        "catalog_code": "",
        "description": "Tomada 20A padrao da biblioteca Eletrica.",
    },
    {
        "id": "tomada_dupla_10a_10a",
        "name": "Tomada Dupla 10A + 10A",
        "category": "Tomada",
        "discipline": "Eletrica",
        "ifc_class": "IfcFlowTerminal",
        "source_3d": "Tomadas/Tomada_Dupla_10A_10A.FCStd",
        "source_2d": "",
        "modules": "2 Modulos",
        "amperage": "10A",
        "voltage": "127V",
        "power": 200.0,
        "apparent_power_va": 200.0,
        "active_power_w": 200.0,
        "power_factor": 1.0,
        "demand_factor": 1.0,
        "phase": "R",
        "load_classification": "TUG",
        "socket_application": "Predial",
        "ip_rating": "IP20",
        "electrical_standard": "NBR 5410",
        "height_type": "Media (1100mm)",
        "mounting_height": 1100.0,
        "manufacturer": "",
        "model": "",
        "catalog_code": "",
        "description": "Tomada dupla 10A padrao da biblioteca Eletrica.",
    },
    {
        "id": "tomada_dupla_20a",
        "name": "Tomada Dupla 20A",
        "category": "Tomada",
        "discipline": "Eletrica",
        "ifc_class": "IfcFlowTerminal",
        "source_3d": "Tomadas/Tomada_Dupla_20A.FCStd",
        "source_2d": "",
        "modules": "2 Modulos",
        "amperage": "20A",
        "voltage": "127V",
        "power": 1200.0,
        "apparent_power_va": 1200.0,
        "active_power_w": 1200.0,
        "power_factor": 1.0,
        "demand_factor": 1.0,
        "phase": "R",
        "load_classification": "TUG",
        "socket_application": "Predial",
        "ip_rating": "IP20",
        "electrical_standard": "NBR 5410",
        "height_type": "Media (1100mm)",
        "mounting_height": 1100.0,
        "manufacturer": "",
        "model": "",
        "catalog_code": "",
        "description": "Tomada dupla 20A padrao da biblioteca Eletrica.",
    },
]


def _slug(text):
    safe = []
    for ch in str(text).lower():
        if ch.isalnum():
            safe.append(ch)
        elif ch in [" ", "-", "_", ".", "/"]:
            safe.append("_")
    value = "".join(safe).strip("_")
    while "__" in value:
        value = value.replace("__", "_")
    return value or "familia"


def _normalize_source(source):
    return str(source or "").replace("\\", "/").strip("/")


def _source_exists(source):
    source = _normalize_source(source)
    if not source:
        return False
    if os.path.isabs(source):
        return os.path.exists(source)
    return os.path.exists(os.path.join(LIBRARY_3D_DIR, source.replace("/", os.sep)))


def _quote(value):
    text = str(value)
    text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return '"' + text + '"'


def _format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return f"{value:.6g}"
    return _quote(value)


def _parse_value(raw):
    raw = raw.strip()
    if not raw:
        return ""
    if raw in ["true", "false"]:
        return raw == "true"
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except Exception:
        return raw


def _simple_toml_load(text):
    data = {}
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "[[family]]":
            current = {}
            data.setdefault("family", []).append(current)
            continue
        if "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        target = current if current is not None else data
        target[key.strip()] = _parse_value(raw_value)
    return data


def _toml_dump(data):
    lines = [
        "# Catalogo leve de familias da bancada Eletrica.",
        "# Este arquivo guarda metadados BIM sem abrir os arquivos .FCStd.",
        f"schema_version = {_format_value(int(data.get('schema_version', 1)))}",
        f"library_root = {_format_value(data.get('library_root', 'Library/3D'))}",
        "",
    ]
    for family in data.get("family", []):
        lines.append("[[family]]")
        for key in [
            "id",
            "name",
            "category",
            "discipline",
            "ifc_class",
            "source_3d",
            "source_2d",
            "modules",
            "amperage",
            "voltage",
            "power",
            "apparent_power_va",
            "active_power_w",
            "power_factor",
            "demand_factor",
            "phase",
            "load_classification",
            "socket_application",
            "ip_rating",
            "electrical_standard",
            "height_type",
            "mounting_height",
            "manufacturer",
            "model",
            "catalog_code",
            "description",
        ]:
            if key in family:
                lines.append(f"{key} = {_format_value(family.get(key, ''))}")
        lines.append("")
    return "\n".join(lines)


def default_catalog():
    return {
        "schema_version": 1,
        "library_root": "Library/3D",
        "family": [dict(item) for item in DEFAULT_SOCKET_FAMILIES],
    }


def ensure_catalog():
    os.makedirs(CATALOG_DIR, exist_ok=True)
    if not os.path.exists(CATALOG_PATH):
        save_toml_catalog(default_catalog())
    return CATALOG_PATH


def load_toml_catalog():
    ensure_catalog()
    with open(CATALOG_PATH, "rb") as fh:
        content = fh.read()
    if tomllib:
        data = tomllib.loads(content.decode("utf-8"))
    else:
        data = _simple_toml_load(content.decode("utf-8"))
    data.setdefault("schema_version", 1)
    data.setdefault("library_root", "Library/3D")
    data.setdefault("family", [])
    return data


def save_toml_catalog(data):
    os.makedirs(CATALOG_DIR, exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as fh:
        fh.write(_toml_dump(data))
    return CATALOG_PATH


def _category_to_freecad(category, load_category=""):
    text = str(category or "")
    load = str(load_category or text)
    if load in ["GeneralSocket", "SpecificSocket"] or text in ["GeneralSocket", "SpecificSocket"]:
        return "Tomada"
    if load == "Lighting":
        return "Iluminacao"
    if load == "Switch":
        return "Interruptor"
    if load in ["DistributionPanel", "MainSwitchboard"]:
        return "Quadro"
    if load == "Motor":
        return "Motor"
    if load in ["DataPoint", "SecurityDevice", "SmartDevice"]:
        return "Automacao"
    if load == "GenericEquipment":
        return "Equipamento"
    return text or "Equipamento"


def _load_classification_from_category(category, default="Geral"):
    if category == "GeneralSocket":
        return "TUG"
    if category == "SpecificSocket":
        return "TUE"
    return default


def _family_from_sqlite_json(data):
    electrical = data.get("electrical", {}) if isinstance(data, dict) else {}
    physical = data.get("physical", {}) if isinstance(data, dict) else {}
    asset = data.get("asset", {}) if isinstance(data, dict) else {}
    category = data.get("category", "")
    dimensions = physical.get("dimensions_mm", [0.0, 0.0, 0.0])
    if not isinstance(dimensions, list):
        dimensions = [0.0, 0.0, 0.0]
    dimensions = (dimensions + [0.0, 0.0, 0.0])[:3]
    modules = int(physical.get("modules", 1) or 1)
    load_class = _load_classification_from_category(
        electrical.get("load_category", category),
        electrical.get("load_classification", "Geral"),
    )
    return {
        "id": data.get("family_id", ""),
        "name": data.get("name", data.get("family_id", "")),
        "category": _category_to_freecad(data.get("category", ""), electrical.get("load_category", "")),
        "rust_category": data.get("category", ""),
        "discipline": data.get("discipline", "Eletrica"),
        "ifc_class": data.get("ifc_class", ""),
        "source_3d": _normalize_source(data.get("source_3d", "")),
        "source_2d": _normalize_source(data.get("source_2d", "")),
        "modules": f"{modules} Modulos" if modules > 1 else "1 Modulo",
        "amperage": physical.get("amperage", ""),
        "voltage": f"{electrical.get('voltage', 127)}V",
        "power": electrical.get("apparent_power_va", 0.0),
        "apparent_power_va": electrical.get("apparent_power_va", 0.0),
        "active_power_w": electrical.get("active_power_watts", 0.0),
        "power_factor": electrical.get("power_factor", 1.0),
        "demand_factor": electrical.get("demand_factor", 1.0),
        "utilization_factor": electrical.get("utilization_factor", 1.0),
        "simultaneity_factor": electrical.get("simultaneity_factor", 1.0),
        "harmonic_dist_thd": electrical.get("harmonic_dist_thd", 0.0),
        "phase": electrical.get("phase", "R"),
        "load_classification": load_class,
        "socket_application": physical.get("socket_application", ""),
        "ip_rating": physical.get("ip_rating", ""),
        "electrical_standard": data.get("electrical_standard", "NBR 5410"),
        "height_type": physical.get("height_type", ""),
        "mounting_height": physical.get("mounting_height_mm", 0.0),
        "width_mm": dimensions[0],
        "height_mm": dimensions[1],
        "depth_mm": dimensions[2],
        "weight_kg": physical.get("weight_kg", 0.0),
        "material_name": physical.get("material_name", ""),
        "material_density_kg_m3": physical.get("material_density_kg_m3", 0.0),
        "embedded_carbon_kg_kg": physical.get("embedded_carbon_kg_kg", 0.0),
        "cost_per_unit": physical.get("cost_per_unit", 0.0),
        "manufacturer": asset.get("manufacturer", ""),
        "model": asset.get("model", ""),
        "catalog_code": asset.get("catalog_code", ""),
        "description": asset.get("description", ""),
        "omniclass_code": asset.get("omniclass_code", ""),
        "uniformat_code": asset.get("uniformat_code", ""),
        "expected_life_years": asset.get("expected_life_years", 0.0),
        "maintenance_manual_url": asset.get("maintenance_manual_url", ""),
    }


def load_sqlite_catalog():
    try:
        from EletricaLogic.FamilySQLite import connect
        conn = connect()
        try:
            rows = conn.execute(
                "SELECT data_json FROM families ORDER BY category, name"
            ).fetchall()
        finally:
            conn.close()
        families = []
        for (raw,) in rows:
            try:
                families.append(_family_from_sqlite_json(json.loads(raw)))
            except Exception:
                pass
        return {
            "schema_version": 1,
            "library_root": "Library/3D",
            "family": families,
            "source": "familias.sqlite",
        }
    except Exception:
        return None


def sqlite_catalog_has_families():
    data = load_sqlite_catalog()
    return bool(data and data.get("family"))


def save_sqlite_catalog(data):
    from EletricaLogic.FamilySQLite import connect, upsert_family
    conn = connect()
    try:
        for family in data.get("family", []):
            upsert_family(conn, family)
        conn.commit()
    finally:
        conn.close()


def load_catalog():
    sqlite_data = load_sqlite_catalog()
    if sqlite_data and sqlite_data.get("family"):
        return sqlite_data

    data = load_toml_catalog()
    try:
        save_sqlite_catalog(data)
    except Exception:
        pass
    return data


def save_catalog(data):
    save_sqlite_catalog(data)
    # Mantem o TOML como backup legivel e rota de recuperacao.
    save_toml_catalog(data)
    return CATALOG_PATH


def infer_family_from_source(source):
    source = _normalize_source(source)
    base = os.path.splitext(os.path.basename(source))[0]
    text = base.lower()
    category = "Tomada" if "tomada" in text else "Equipamento"
    if "tripla" in text or text.endswith("_t3") or "_t3" in text:
        modules = "3 Modulos"
    elif "dupla" in text or text.endswith("_t2") or "_t2" in text:
        modules = "2 Modulos"
    else:
        modules = "1 Modulo"
    amperage = "20A" if "20a" in text else "10A"
    module_count = 3 if modules.startswith("3") else 2 if modules.startswith("2") else 1
    unit_power = 600.0 if amperage == "20A" else 100.0
    power = unit_power * module_count
    power_factor = 1.0
    return {
        "id": _slug(base),
        "name": base.replace("_", " "),
        "category": category,
        "discipline": "Eletrica",
        "ifc_class": "IfcFlowTerminal" if category == "Tomada" else "IfcDistributionElement",
        "source_3d": source,
        "source_2d": "",
        "modules": modules,
        "amperage": amperage,
        "voltage": "127V",
        "power": power,
        "apparent_power_va": power,
        "active_power_w": power * power_factor,
        "power_factor": power_factor,
        "demand_factor": 1.0,
        "phase": "R",
        "load_classification": "TUG" if category == "Tomada" else "Geral",
        "socket_application": "Predial" if category == "Tomada" else "",
        "ip_rating": "IP20" if category == "Tomada" else "",
        "electrical_standard": "NBR 5410",
        "height_type": "Media (1100mm)",
        "mounting_height": 1100.0,
        "manufacturer": "",
        "model": "",
        "catalog_code": "",
        "description": "",
    }


def scan_library_sources():
    sources = []
    if not os.path.isdir(LIBRARY_3D_DIR):
        return sources
    for root, dirs, files in os.walk(LIBRARY_3D_DIR):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and "backup" not in d.lower() and "__pycache__" not in d.lower()
        ]
        for fname in files:
            if not fname.lower().endswith(".fcstd"):
                continue
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, LIBRARY_3D_DIR)
            sources.append(_normalize_source(rel))
    return sorted(sources)

def _family_module_count(value):
    text = str(value or "")
    for number in [3, 2, 1]:
        if text.startswith(str(number)) or str(number) in text:
            return number
    return 1

def _socket_replacement_source(family, available_sources):
    if family.get("category") != "Tomada":
        return ""
    identity = " ".join([
        str(family.get("id", "")),
        str(family.get("name", "")),
        str(family.get("source_3d", "")),
    ]).lower()
    if "simples" in identity:
        modules = 1
    elif "dupla" in identity:
        modules = 2
    elif "tripla" in identity:
        modules = 3
    elif "_t3" in identity or "cx_4x2_t3" in identity:
        modules = 3
    elif "_t2" in identity or "cx_4x2_t2" in identity:
        modules = 2
    elif "_t1" in identity or "cx_4x2_t1" in identity:
        modules = 1
    else:
        modules = _family_module_count(family.get("modules"))
    candidates = [f"Tomadas/Cx_4x2_T{modules}.FCStd"]
    is_20 = family.get("amperage") == "20A"
    if modules == 3:
        candidates.append("Tomadas/Tomada_Tripla_20A.FCStd" if is_20 else "Tomadas/Tomada_Tripla_10A.FCStd")
    elif modules == 2:
        candidates.append("Tomadas/Tomada_Dupla_20A.FCStd" if is_20 else "Tomadas/Tomada_Dupla_10A_10A.FCStd")
    else:
        candidates.append("Tomadas/Tomada_Simples_20A.FCStd" if is_20 else "Tomadas/Tomada_Simples_10A.FCStd")
    for candidate in candidates:
        if _normalize_source(candidate) in available_sources:
            return candidate
    return ""

def _sync_socket_defaults_from_identity(family):
    identity = " ".join([
        str(family.get("id", "")),
        str(family.get("name", "")),
        str(family.get("source_3d", "")),
    ]).lower()
    if family.get("category") != "Tomada":
        return
    if "simples" in identity:
        modules = 1
    elif "dupla" in identity:
        modules = 2
    elif "tripla" in identity:
        modules = 3
    elif "_t3" in identity or "cx_4x2_t3" in identity:
        modules = 3
    elif "_t2" in identity or "cx_4x2_t2" in identity:
        modules = 2
    elif "_t1" in identity or "cx_4x2_t1" in identity:
        modules = 1
    else:
        modules = _family_module_count(family.get("modules"))
    amperage = "20A" if "20a" in identity else family.get("amperage", "10A") or "10A"
    unit_power = 600.0 if amperage == "20A" else 100.0
    power = unit_power * modules
    family["modules"] = f"{modules} Modulos" if modules > 1 else "1 Modulo"
    family["amperage"] = amperage
    family["power"] = power
    family["apparent_power_va"] = power
    family["active_power_w"] = power * float(family.get("power_factor", 1.0) or 1.0)


def refresh_catalog_from_library():
    data = load_catalog()
    families = data.setdefault("family", [])
    sources = scan_library_sources()
    available = set(sources)
    for family in families:
        source = _normalize_source(family.get("source_3d"))
        source_is_backup = "backup" in source.lower()
        replacement = _socket_replacement_source(family, available) if source else ""
        standard_socket_needs_repair = (
            replacement
            and replacement != source
            and any(word in " ".join([str(family.get("id", "")), str(family.get("name", ""))]).lower() for word in ["simples", "dupla", "tripla"])
        )
        if source and (source_is_backup or standard_socket_needs_repair or (source not in available and not _source_exists(source))):
            if replacement:
                family["source_3d"] = replacement
                _sync_socket_defaults_from_identity(family)

    existing = {_normalize_source(item.get("source_3d")) for item in families}
    for source in sources:
        if source not in existing:
            families.append(infer_family_from_source(source))
            existing.add(source)
    save_catalog(data)
    return data


def list_families(category=None):
    data = load_catalog()
    result = []
    for family in data.get("family", []):
        item = dict(family)
        item["source_3d"] = _normalize_source(item.get("source_3d"))
        if category and item.get("category") != category:
            continue
        result.append(item)
    result.sort(key=lambda item: (item.get("category", ""), item.get("name", "")))
    return result


def find_family_by_source(source):
    needle = _normalize_source(source)
    needle_base = os.path.basename(needle)
    for family in list_families():
        candidate = _normalize_source(family.get("source_3d"))
        if candidate == needle or os.path.basename(candidate) == needle_base:
            return family
    return None


def find_family(category=None, modules=None, amperage=None):
    for family in list_families(category):
        if modules and not str(family.get("modules", "")).startswith(str(modules)[0]):
            continue
        if amperage and family.get("amperage") != amperage:
            continue
        return family
    return None


def family_full_path(source):
    source = _normalize_source(source)
    if os.path.isabs(source):
        return source
    return os.path.join(LIBRARY_3D_DIR, source.replace("/", os.sep))


def import_family_file(path, category="Importadas"):
    if not path or not os.path.exists(path):
        return None
    folder = "Tomadas" if category == "Tomada" else category
    target_dir = os.path.join(LIBRARY_3D_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    target = os.path.join(target_dir, base)
    counter = 2
    while os.path.exists(target):
        target = os.path.join(target_dir, f"{name}_{counter}{ext}")
        counter += 1
    shutil.copy2(path, target)
    source = _normalize_source(os.path.relpath(target, LIBRARY_3D_DIR))
    data = load_catalog()
    family = infer_family_from_source(source)
    family["category"] = "Tomada" if "tomada" in source.lower() else category
    data.setdefault("family", []).append(family)
    save_catalog(data)
    return family
