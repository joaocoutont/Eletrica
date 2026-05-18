import os
import shutil

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
        save_catalog(default_catalog())
    return CATALOG_PATH


def load_catalog():
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


def save_catalog(data):
    os.makedirs(CATALOG_DIR, exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as fh:
        fh.write(_toml_dump(data))
    return CATALOG_PATH


def infer_family_from_source(source):
    source = _normalize_source(source)
    base = os.path.splitext(os.path.basename(source))[0]
    text = base.lower()
    category = "Tomada" if "tomada" in text else "Equipamento"
    modules = "2 Modulos" if "dupla" in text or "_2" in text else "1 Modulo"
    amperage = "20A" if "20a" in text else "10A"
    power = 1200.0 if amperage == "20A" and modules.startswith("2") else 600.0 if amperage == "20A" else 200.0 if modules.startswith("2") else 100.0
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
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if not fname.lower().endswith(".fcstd"):
                continue
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, LIBRARY_3D_DIR)
            sources.append(_normalize_source(rel))
    return sorted(sources)


def refresh_catalog_from_library():
    data = load_catalog()
    families = data.setdefault("family", [])
    existing = {_normalize_source(item.get("source_3d")) for item in families}
    for source in scan_library_sources():
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
